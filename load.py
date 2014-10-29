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

#constants for _map
MAPTYPE_COMMAND = 0
MAPTYPE_ALIAS = 1
MAPTYPE_REGEX = 2


#define Plugin Manager class
class PluginMan:
    def trywrapper(self, command, msginfo):
        try:
            self.commandlist[command]["function"](self, msginfo)
        except Exception as e:
            if type(e) == KeyError:
                pass
            elif type(e) == mpd.ConnectionError:
                self.conman.reconnect_mpd()
                self.trywrapper(command, msginfo)
            else:
                traceback.print_exc()
                self.conman.privmsg("Error executing %s: %s" % (command, e))


    def execute_command(self, msginfo):
        if msginfo["type"] == "PRIVMSG":
            try:
                mapped = msginfo["msg"][1:msginfo["msg"].index(" ")]
            except ValueError:
                mapped = msginfo["msg"][1:]
        elif msginfo["type"] == "regex":
            mapped = msginfo["pattern"]
        else:
            raise Exception("Invalid message type")

        try:
            if self.commandlist[mapped]["type"] == MAPTYPE_ALIAS:
                mapped = self.commandlist[mapped]["pointer"]

            if self.commandlist[mapped].get("prefix", None):
                msginfo["prefix"] = self.commandlist[mapped]["prefix"]

            t = threading.Thread(target = self.trywrapper, args = (mapped, msginfo))
            t.daemon = 1
            t.start()

        # silence traceback if not such command exists
        except KeyError:
            pass


    def require(self, func):
        if not self.funcs.get(func, None):
            raise Exception("Required function %s not loaded" % func)


    #Define function to load modules
    def load(self, unused, msginfo):
        #not in __init__ so that .reload removes entries for old modules
        self.commandlist = {"reload": {
            "type": MAPTYPE_COMMAND,
            "function": self.load,
            "help": ".reload - reloads modules"
            }}
        self.funcs = {}
        self.pluginlist = {}
        for plugpath in glob.glob(self.modulespath + "*.py"):
            self.pluginlist[plugpath] = set()
        plugincount = 0
        failcount = 0
        blockcount = 0
        for plugin in self.pluginlist.keys():
            if not plugin.replace(self.modulespath, "").replace(".py", "") in self.glob_confman.get_value("modules", "MODULE_BLACKLIST", []):
                try:
                    exec(open(plugin, "r").read())
                    plugincount += 1
                    self.pluginlist[plugin].add("loaded")
                except Exception as e:
                    # if reloaded from a channel other than HOME_CHANNEL
                    if not msginfo["chan"] == HOME_CHANNEL:
                        self.conman.gen_send("Error loading module %s: %s" % (os.path.basename(plugin), e))
                    self.conman.privmsg("Error loading module %s: %s" % (os.path.basename(plugin), e))
                    failcount += 1
                    self.pluginlist[plugin].add("failed")
            else:
                blockcount += 1
                self.pluginlist[plugin].add("blocked")
        self.conman.gen_send("Successfully loaded %s modules%s%s" % (plugincount, (" | %s modules failed" % failcount if failcount > 0 else ""), (" | %s modules blocked" % blockcount if blockcount > 0 else "")), msginfo)


    # PluginMan constructor
    def __init__(self, conman_instance, globconfman_instance):
        self.modulespath = os.path.join(os.path.dirname(__file__), "modules") + os.sep
        self.conman = conman_instance
        self.confman = ConfigMan("module")
        self.glob_confman = globconfman_instance
        #TODO: Reimplement
        # this serves no function for the class itself, its just for exposing the information to modules that may request it
        #self.permsman = permsman_instance
        self.load(None, {"chan": HOME_CHANNEL})



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
