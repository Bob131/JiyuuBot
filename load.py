import os
import glob
import threading
import json
import re
import traceback

from configman import *

#Load config file from config.py
exec(open(os.path.join(os.path.dirname(__file__), "configs" + os.sep + "config.py"), "r").read())

if MPD:
    import mpd
else:
    import dummympd as mpd

#define Plugin Manager class
class PluginMan:
    def trywrapper(self, command, arg, source):
        if source["type"] == "HTTP":
            commlist = self.httplist
        elif source["type"] == "regex":
            commlist = self.regex
        else:
            commlist = self.commandlist
        try:
            source["prefix"] = commlist[command]["prefix"]
            thread_types[threading.current_thread().ident] = source
            commlist[command]["function"](self, arg)
        except Exception as e:
            if type(e) == KeyError:
                pass
            elif type(e) == mpd.ConnectionError:
                self.conman.reconnect_mpd()
                self.trywrapper(command, arg)
            else:
                traceback.print_exc()
                self.conman.privmsg("Error executing %s: %s" % (command, e))
        del thread_types[threading.current_thread().ident]

    def execute_command(self, command, source={"type": "PRIVMSG", "source": HOME_CHANNEL}):
        if source["type"] == "PRIVMSG" or source["type"] == "HTTP":
            try:
                mapped = command[:command.index(" ")]
                arg = command[command.index(" ")+1:].strip()
            except ValueError:
                mapped = command
                arg = ""
        else:
            mapped = source["pattern"]
            arg = command
        t = threading.Thread(target = self.trywrapper, args = (mapped, arg, source))
        t.daemon = 1
        t.start()
        return t.ident

    def _map(self, maptype, command, function, prefix=""):
        if " " in command:
            raise Exception("Spaces not allowed in the command argument for command mapping")
        if maptype == "command":
            self.commandlist[command] = {"function": function, "prefix": prefix}
        elif maptype == "http":
            self.httplist[command] = {"function": function, "prefix": ""}
        elif maptype == "alias":
            if not type(command) == str:
                raise Exception("Alias mapping must be to a string")
            self.commandlist[command] = self.commandlist[function]
            if function in self.helplist.keys():
                self.helplist[command] = self.helplist[function]
        elif maptype == "help":
            self.helplist[command] = function # here function is the help message
        elif maptype == "regex": # for matching message lines not starting with .
            if prefix == "":
                prefix = function.__name__
            self.regex[command] = {"function": function, "prefix": prefix}
        else:
            raise Exception("Invalid map type %s" % maptype)

    def run_func(self, name, *args, **kwargs):
        try:
            return self.funcs[name](self, *args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            self.conman.privmsg("Error executing helper function %s: %s" % (name, e))
            return None

    def reg_func(self, name, func):
        if name in self.funcs.keys():
            raise Exception("Function %s already registered" % name)
        else:
            self.funcs[name] = func

    def require(self, func):
        if not func in self.funcs.keys():
            raise Exception("Module %s not loaded" % func)

	#Define function to load modules
        #Two unused vars are required so that .reload executes correctly
    def load(self, unused = None, alsoUnused = None):
        #not in __init__ so that .reload removes entries for old modules
        self.commandlist = {"reload": {"function": self.load, "prefix": ""}}
        self.helplist = {"reload": ".reload - reloads modules"}
        self.httplist = {}
        self.funcs = {}
        self.regex = {}
        self.pluginlist = {}
        for plugpath in glob.glob(self.modulespath + "*.py"):
            self.pluginlist[plugpath] = set()
        plugincount = 0
        failcount = 0
        blockcount = 0
        for plugin in self.pluginlist.keys():
            if not plugin.replace(self.modulespath, "").replace(".py", "") in self.glob_confman.get_value("modules", "BLOCKLIST", []):
                try:
                    exec(open(plugin, "r").read())
                    plugincount += 1
                    self.pluginlist[plugin].add("loaded")
                except Exception as e:
                    try:
                        # if reloaded from a channel other than HOME_CHANNEL
                        ret_type = thread_types[threading.current_thread().ident]
                        if not ret_type["source"] == HOME_CHANNEL:
                            self.conman.gen_send("Error loading module %s: %s" % (os.path.basename(plugin), e))
                        self.conman.privmsg("Error loading module %s: %s" % (os.path.basename(plugin), e))
                    except:
                        self.conman.privmsg("Error loading module %s: %s" % (os.path.basename(plugin), e))
                    failcount += 1
                    self.pluginlist[plugin].add("failed")
            else:
                blockcount += 1
                self.pluginlist[plugin].add("blocked")
        self.conman.gen_send("Successfully loaded %s modules%s%s" % (plugincount, (" | %s modules failed" % failcount if failcount > 0 else ""), (" | %s modules blocked" % blockcount if blockcount > 0 else "")))

	#Define initialization function
    def __init__(self, conman_instance, permsman_instance, globconfman_instance, threaddict):
        global thread_types
        thread_types = threaddict
        self.modulespath = os.path.join(os.path.dirname(__file__), "modules") + os.sep
        self.conman = conman_instance
        self.confman = ConfigMan("module")
        self.glob_confman = globconfman_instance
        # this serves no function for the class itself, its just for exposing the information to modules that may request it
        self.permsman = permsman_instance
        self.load()



class ServiceMan:
    def trywrapper(self, func, recur = 0):
        thread_types[threading.current_thread().ident] = "PRIVMSG:"+HOME_CHANNEL
        try:
            func(self)
        except Exception as e:
            if type(e) == mpd.ConnectionError:
                self.conman.reconnect_mpd()
                self.trywrapper(func)
            else:
                if recur < 2:
                    self.conman.privmsg("Service %s failed. Restarting..." % func.__name__)
                    self.trywrapper(func, recur+1)
                else:
                    self.conman.privmsg("Error in service module %s. Halting thread. Error: %s" % (func.__name__, e))
        if not recur > 0:
            del thread_types[threading.current_thread().ident]

    def start_services(self):
        for func in self.funclist:
            t = threading.Thread(target = self.trywrapper, args=(func,))
            t.daemon = 1
            t.start()

    def map_service(self, function):
        self.funclist.append(function)

    def load(self):
        servlist = glob.glob(self.servicespath + "*.py")
        servcount = 0
        failcount = 0
        for service in servlist:
            if not service.replace(self.servicespath, "").replace(".py", "") in SERVICE_BLACKLIST:
                try:
                    exec(open(service, "r").read())
                    servcount += 1
                except Exception as e:
                    self.conman.privmsg("Error loading service %s: %s" % (os.path.basename(service), e))
                    failcount += 1
        self.conman.privmsg("Successfully loaded %s services, %s failed to load" % (servcount, failcount))
        self.start_services()

    def __init__(self, conman_instance, plugman_instance, threaddict):
        global thread_types
        thread_types = threaddict
        self.servicespath = os.path.join(os.path.dirname(__file__), "services") + os.sep
        self.conman = conman_instance
        self.plugman = plugman_instance
        self.confman = ConfigMan("service")
        self.funclist = []
        self.load()
