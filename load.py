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
            if type(e) == mpd.ConnectionError:
                self.conman.reconnect_mpd()
                t.start()
            else:
                self.conman.privmsg("Error: %s" % e)

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
        self.helplist[command] = message
	
	#Define commands to their function
    def map_command(self, command, function):
        self.commandlist[command] = function

	#Define function to load modules
    def load(self, wut=None, wuty=None):
        #not in __init__ so that .reload removes entries for old modules
        self.commandlist = {"reload": self.load}
        self.helplist = {"reload": ".reload - reloads modules"}
        pluginlist = glob.glob(self.modulespath + "*.py")
        for plugin in pluginlist:
            exec(open(plugin, "r").read())
        self.conman.privmsg("Successfully loaded %s modules" % len(pluginlist))

	#Define initialization function
    def __init__(self):
        self.modulespath = os.path.join(os.path.dirname(__file__), "modules") + os.sep
        self.conman = connect.ConnectionMan()
        self.load()
