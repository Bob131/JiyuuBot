def mod_parse(self, msginfo):
    arg = msginfo["msg"].split(" ")[1:]
    if len(arg) == 0:
        return None
    if arg[0] == "list":
        self.conman.gen_send(", ".join(plugin.replace(self.modulespath, "").replace(".py", "") for plugin in self.pluginlist), msginfo)
    elif arg[0] == "block":
        block = set(self.glob_confman.get("modules", "BLACKLIST", []))
        for mod in arg[1].split(","):
            block.add(mod.strip())
        self.glob_confman.setv("modules", "BLACKLIST", list(block))
        self.conman.gen_send("Blocked %s modules" % len(arg[1].split(",")), msginfo)
    elif arg[0] == "unblock":
        block = set(self.glob_confman.get("modules", "BLOCKLIST", []))
        for mod in arg[1].split(","):
            block.remove(mod.strip())
        self.glob_confman.setv("modules", "BLACKLIST", list(block))
        self.conman.gen_send("Unblocked %s modules" % len(arg[1].split(",")), msginfo)

self.permsman.suggest_cmd_perms("module", 999)
self.commandlist["module"] = {
        "type": MAPTYPE_COMMAND,
        "function": mod_parse,
        "help": "Controls what modules should be loaded. Arguments are list, block and unblock. (un)block accepts comma-delimited arguments"
        }
