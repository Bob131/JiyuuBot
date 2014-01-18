import os
import glob
import threading
import json
import re

from configman import *

#Load config file from config.py
exec(open(os.path.join(os.path.dirname(__file__), "configs" + os.sep + "config.py"), "r").read())

if MPD:
    import mpd
else:
    import dummympd as mpd

#define Plugin Manager class
class PluginMan:
    def trywrapper(self, command, arg, source="PRIVMSG"):
        thread_types[threading.current_thread().ident] = source
        if source == "HTTP":
            commlist = self.httplist
        elif source == "regex":
            commlist = self.regex
        else:
            commlist = self.commandlist
        try:
            commlist[command](self, arg)
        except Exception as e:
            if type(e) == KeyError:
                pass
            elif type(e) == mpd.ConnectionError:
                self.conman.reconnect_mpd()
                self.trywrapper(command, arg)
            else:
                self.conman.gen_send("Error executing %s: %s" % (command, e))
        del thread_types[threading.current_thread().ident]

    def execute_regex(self, pattern, match):
        t = threading.Thread(target = self.trywrapper, args = (pattern, match, "regex"))
        t.daemon = 1
        t.start()
        return t.ident

    def execute_command(self, command, source="PRIVMSG"):
        try:
            mapped = command[:command.index(" ")]
            arg = command[command.index(" ")+1:]
        except ValueError:
            mapped = command
            arg = ""
        t = threading.Thread(target = self.trywrapper, args = (mapped, arg, source))
        t.daemon = 1
        t.start()
        return t.ident

    def _map(self, maptype, command, function):
        if " " in command:
            raise Exception("Spaces not allowed in the command argument for command mapping")
        if maptype == "command":
            self.commandlist[command] = function
        elif maptype == "http":
            self.httplist[command] = function
        elif maptype == "alias":
            if not type(command) == str:
                raise Exception("Alias mapping must be to a string")
            self.commandlist[command] = function
            if function in self.helplist.keys():
                self.helplist[command] = self.helplist[function]
        elif maptype == "help":
            self.helplist[command] = function # here function is the help message
        elif maptype == "regex": # for matching message lines not starting with .
            self.regex[command] = function
        else:
            raise Exception("Invalid map type %s" % maptype)

    def run_func(self, name, args):
        try:
            return self.funcs[name](self, args)
        except Exception as e:
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
        self.commandlist = {"reload": self.load}
        self.helplist = {"reload": ".reload - reloads modules"}
        self.httplist = {}
        self.funcs = {}
        self.regex = {}
        pluginlist = glob.glob(self.modulespath + "*.py")
        plugincount = 0
        failcount = 0
        for plugin in pluginlist:
            try:
                exec(open(plugin, "r").read())
                plugincount += 1
            except Exception as e:
                self.conman.privmsg("Error loading module %s: %s" % (os.path.basename(plugin), e))
                failcount += 1
        self.conman.privmsg("Successfully loaded %s modules, %s failed to load" % (plugincount, failcount))

	#Define initialization function
    def __init__(self, conman_instance, permsman_instance, threaddict):
        global thread_types
        thread_types = threaddict
        self.modulespath = os.path.join(os.path.dirname(__file__), "modules") + os.sep
        self.conman = conman_instance
        self.confman = ConfigMan("module")
        # this serves no function for the class itself, its just for exposing the information to modules that may request it
        self.permsman = permsman_instance
        self.load()



class ServiceMan:
    def trywrapper(self, func, recur = 0):
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
            try:
                exec(open(service, "r").read())
                servcount += 1
            except Exception as e:
                self.conman.privmsg("Error loading service %s: %s" % (os.path.basename(service), e))
                failcount += 1
        self.conman.privmsg("Successfully loaded %s services, %s failed to load" % (servcount, failcount))
        self.start_services()

    def __init__(self, conman_instance, plugman_instance):
        self.servicespath = os.path.join(os.path.dirname(__file__), "services") + os.sep
        self.conman = conman_instance
        self.plugman = plugman_instance
        self.confman = ConfigMan("service")
        self.funclist = []
        self.load()
