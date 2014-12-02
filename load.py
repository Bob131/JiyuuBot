import os
import glob
import threading
import json
import re
import traceback
try:
    import mpd
    boolMPD = True
except ImportError:
    boolMPD = False
    print("Unable to load mpd")

from configman import *

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
            if type(e) == mpd.ConnectionError and boolMPD:
                self.conman.reconnect_mpd()
                self.trywrapper(command, msginfo)
            else:
                traceback.print_exc()
                self.ltb = {
                        "exception": traceback.format_exc(),
                        "msginfo": msginfo
                        }
                self.conman.gen_send("Error executing %s: %s" % (command, e), msginfo)
                if not msginfo["chan"] == self.glob_confman.get("IRC", "HOME_CHANNEL"):
                    self.conman.privmsg("Exception occured. Check traceback")


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


    def require(self, plugin):
        plugin = "{}/{}.py".format(self.modulespath, plugin)
        if not list(self.pluginlist.get(plugin, ["failed"]))[0] == "failed":
            raise Exception("Required plugin %s not loaded" % plugin)


    #Define function to load modules
    def load(self, _, msginfo):
        #not in __init__ so that .reload removes entries for old modules
        self.commandlist = {"reload": {
            "type": MAPTYPE_COMMAND,
            "function": self.load,
            "help": ".reload - reloads modules"
            }}
        self.funcs = {}
        self.pluginlist = {}
        self.regex_cache = None
        for plugpath in glob.glob(self.modulespath + "*.py"):
            self.pluginlist[plugpath] = set()
        plugincount = 0
        failcount = 0
        blockcount = 0
        for plugin in self.pluginlist.keys():
            if not plugin.replace(self.modulespath, "").replace(".py", "") in self.glob_confman.get("modules", "MODULE_BLACKLIST", []):
                try:
                    exec(open(plugin, "r").read())
                    plugincount += 1
                    self.pluginlist[plugin].add("loaded")
                except Exception as e:
                    # if reloaded from a channel other than HOME_CHANNEL
                    if not msginfo["chan"] == self.glob_confman.get("IRC", "HOME_CHANNEL"):
                        self.conman.gen_send("Error loading module %s: %s" % (os.path.basename(plugin), e), msginfo)
                    self.conman.privmsg("Error loading module %s: %s" % (os.path.basename(plugin), e))
                    failcount += 1
                    self.pluginlist[plugin].add("failed")
            else:
                blockcount += 1
                self.pluginlist[plugin].add("blocked")
        self.conman.gen_send("Successfully loaded %s modules%s%s" % (plugincount, (" | %s modules failed" % failcount if failcount > 0 else ""), (" | %s modules blocked" % blockcount if blockcount > 0 else "")), msginfo)


    # PluginMan constructor
    def __init__(self, conman_instance, globconfman_instance, permsman_instance):
        self.modulespath = os.path.join(os.path.dirname(__file__), "modules") + os.sep
        self.conman = conman_instance
        self.confman = ConfigMan("module")
        self.glob_confman = globconfman_instance
        self.permsman = permsman_instance
        self.ltb = None
        self.load(None, {"chan": self.glob_confman.get("IRC", "HOME_CHANNEL")})
