@self.command(help="Controls what modules should be loaded. Arguments are list, block and unblock. (un)block accepts comma-delimited arguments. Syntax: .module (block|unblock) <module> OR .module list [blocked])", perm=999)
def module(self, msginfo):
    arg = msginfo["msg"].split(" ")[1:]
    if len(arg) == 0:
        return None
    if arg[0] == "list":
        if len(arg) == 1:
            self.conman.gen_send(", ".join(plugin.replace(self.modulespath, "").replace(".py", "") for plugin in self.pluginlist), msginfo)
        else:
            if arg[1] == "block" or arg[1] == "blocked":
                blmods = ", ".join(self.glob_confman.get("modules", "BLACKLIST", []))
                if blmods == "":
                    blmods = "No modules blocked"
                self.conman.gen_send(blmods, msginfo)
    elif arg[0] == "block":
        block = set(self.glob_confman.get("modules", "BLACKLIST", []))
        for mod in arg[1].split(","):
            block.add(mod.strip())
        self.glob_confman.setv("modules", "BLACKLIST", list(block))
        self.conman.gen_send("Blocked %s modules" % len(arg[1].split(",")), msginfo)
    elif arg[0] == "unblock":
        block = set(self.glob_confman.get("modules", "BLACKLIST", []))
        for mod in arg[1].split(","):
            block.remove(mod.strip())
        self.glob_confman.setv("modules", "BLACKLIST", list(block))
        self.conman.gen_send("Unblocked %s modules" % len(arg[1].split(",")), msginfo)
