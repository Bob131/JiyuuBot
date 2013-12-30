import os
import mpd
import glob
import threading

from configman import *

#Load config file from config.py
exec(open(os.path.join(os.path.dirname(__file__), "configs" + os.sep + "config.py"), "r").read())

#define Plugin Manager class
class PluginMan:
    def trywrapper(self, command, arg):
        try:
            self.commandlist[command](self, arg)
        except Exception as e:
            if type(e) == KeyError:
                pass
            elif type(e) == mpd.ConnectionError:
                self.conman.reconnect_mpd()
                self.trywrapper(command, arg)
            else:
                self.conman.privmsg("Error executing %s: %s" % (command, e))

    def execute_command(self, command):
        try:
            mapped = command[:command.index(" ")]
            arg = command[command.index(" ")+1:]
        except ValueError:
            mapped = command
            arg = ""
        t = threading.Thread(target = self.trywrapper, args = (mapped, arg))
        t.daemon = 1
        t.start()

	#Define commands to their help message
    def map_help(self, command, message):
        if " " in command:
            raise Exception("Spaces not allowed in the command argument for help mapping")
        self.helplist[command] = message
	
	#Define commands to their function
    def map_command(self, command, function, helplist=True):
        if " " in command:
            raise Exception("Spaces not allowed in the command argument for command mapping")
        self.commandlist[command] = function
        if helplist:
            self.helpcommandlist.append(command)

    def run_func(self, name, args):
        try:
            return self.funcs[name](self, args)
        except Exception as e:
            raise e

    def reg_func(self, name, func):
        if name in self.funcs.keys():
            raise Exception("Function %s already registered" % name)
        else:
            self.funcs[name] = func

    def require(self, func):
        if not func in self.funcs.keys():
            raise Exception("Module %s not loaded" % func)

	#Define function to load modules
    def load(self, wut=None, wuty=None):
        #not in __init__ so that .reload removes entries for old modules
        self.commandlist = {"reload": self.load}
        self.helplist = {"reload": ".reload - reloads modules"}
        self.helpcommandlist = ["reload"]
        self.funcs = {}
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
    def __init__(self, conman_instance, permsman_instance):
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
