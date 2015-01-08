import os
import sys
import glob
import threading
import json
import re
import traceback
import types

from configman import *

#constants for _map
MAPTYPE_COMMAND = 0
MAPTYPE_ALIAS = 1
MAPTYPE_REGEX = 2
MAPTYPE_IRC = MAPTYPE_REGEX

ORIGINAL_MEMBERS = ()


#define Plugin Manager class
class PluginMan:
    def trywrapper(self, command, msginfo):
        with self.lock:
            try:
                self.commandlist[command]["function"](self, msginfo)
            except Exception as e:
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
            mapped = msginfo["msg"].split(" ")[0].replace(".", "").lower()
        elif msginfo["type"] == "regex":
            mapped = msginfo["pattern"]
        else:
            raise Exception("Invalid message type")

        try:
            if self.commandlist[mapped]["type"] == MAPTYPE_ALIAS:
                mapped = self.commandlist[mapped]["pointer"]

            if self.commandlist[mapped].get("prefix", None):
                msginfo["prefix"] = self.commandlist[mapped]["prefix"]

            if self.commandlist[mapped]["type"] == MAPTYPE_COMMAND:
                if not self.permsman.get_perms(msginfo["hostname"], mapped):
                    self.conman.gen_send("You do not have high enough permissions to execute that command", msginfo)
                    return None

            t = threading.Thread(target = self.trywrapper, args = (mapped, msginfo))
            t.daemon = 1
            t.start()

        # silence traceback if not such command exists
        except KeyError:
            pass


    # map decorators
    def command(self, *args, **kargs):
        def decorator(f):
            try:
                name = args[0]
            except IndexError:
                name = f.__name__
            self.commandlist[name] = {
                    "type": MAPTYPE_COMMAND,
                    "function": f
                    }
            if 'help' in kargs.keys():
                self.commandlist[name]["help"] = kargs['help']
            if 'perm' in kargs.keys():
                self.permsman.suggest_cmd_perms(name, kargs['perm'])
            return f
        return decorator

    def alias(self, from_, to):
        self.commandlist[from_] = {
                "type": MAPTYPE_ALIAS,
                "pointer": to
                }

    def regex(self, pattern, **kargs):
        def decorator(f):
            prefix = kargs.get('prefix', None) or f.__name__.title()
            self.commandlist[pattern] = {
                    "type": MAPTYPE_REGEX,
                    "function": f,
                    "prefix": prefix
                    }
            return f
        return decorator

    def irc(self, command):
        def decorator(f):
            self.commandlist["!{}".format(str(command))] = {
                    "type": MAPTYPE_IRC,
                    "function": f
                    }
            return f
        return decorator

    def function(self, f):
        self.__dict__[f.__name__] = types.MethodType(f, self)
        return f


    def require(self, plugin):
        plugin = "{}/{}.py".format(self.modulespath, plugin)
        if not list(self.pluginlist.get(plugin, ["failed"]))[0] == "failed":
            raise Exception("Required plugin %s not loaded" % plugin)


    #Define function to load modules
    def load(self, _, msginfo):
        #remove functions
        current_members = tuple(self.__dict__.keys()) # copy into new value
        for name in current_members:
            if not name in ORIGINAL_MEMBERS:
                print("Destroying old object {}".format(name))
                del self.__dict__[name]
        #not in __init__ so that .reload removes entries for old modules
        self.commandlist = {"reload": {
            "type": MAPTYPE_COMMAND,
            "function": self.load,
            "help": ".reload - reloads modules"
            }}
        self.pluginlist = {}
        for plugpath in glob.glob(self.modulespath + "*.py"):
            self.pluginlist[plugpath] = set()
        plugincount = 0
        failcount = 0
        blockcount = 0
        for plugin in self.pluginlist.keys():
            if not plugin.replace(self.modulespath, "").replace(".py", "") in self.glob_confman.get("modules", "BLACKLIST", []):
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
                    traceback.print_exc()
            else:
                blockcount += 1
                self.pluginlist[plugin].add("blocked")
        self.regex_cache = list(pattern for pattern in self.commandlist.keys() if self.commandlist[pattern]["type"] == MAPTYPE_REGEX)
        self.conman.gen_send("Successfully loaded %s modules%s%s" % (plugincount, (" | %s modules failed" % failcount if failcount > 0 else ""), (" | %s modules blocked" % blockcount if blockcount > 0 else "")), msginfo)


    # PluginMan constructor
    def __init__(self, conman_instance, globconfman_instance, permsman_instance):
        self.modulespath = os.path.join(os.path.dirname(__file__), "modules") + os.sep
        self.conman = conman_instance
        self.confman = ConfigMan("module")
        self.glob_confman = globconfman_instance
        self.permsman = permsman_instance
        self.ltb = None
        self.lock = threading.Lock()
        global ORIGINAL_MEMBERS
        ORIGINAL_MEMBERS = tuple(self.__dict__.keys())
        with self.lock:
            self.load(None, {"chan": self.glob_confman.get("IRC", "HOME_CHANNEL")})
