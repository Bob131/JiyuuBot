import os
import glob
import connect
import mpd
import threading

#Load config file from config.py
exec(open(os.path.join(os.path.dirname(__file__), "config.py"), "r").read())

#define Plugin Manager class
class PluginMan:
    def trywrapper(self, command, arg):
        try:
            self.commandlist[command](self, arg)
        except Exception as e:
            if type(e) == KeyError:
                self.conman.privmsg("Command %s not found" % e)
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

	#Define function to load modules
    def load(self, wut=None, wuty=None):
        #not in __init__ so that .reload removes entries for old modules
        self.commandlist = {"reload": self.load}
        self.helplist = {"reload": ".reload - reloads modules"}
        self.helpcommandlist = ["reload"]
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
    def __init__(self):
        self.modulespath = os.path.join(os.path.dirname(__file__), "modules") + os.sep
        self.servicespath = os.path.join(os.path.dirname(__file__), "services") + os.sep
        self.conman = connect.ConnectionMan()
        self.load()
