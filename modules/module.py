def mod_parse(self, cmd):
    arg = cmd.split(" ")
    if arg[0] == "list":
        self.conman.gen_send(", ".join(plugin.replace(self.modulespath, "").replace(".py", "") for plugin in self.pluginlist if arg[1] in self.pluginlist[plugin]))
    if arg[0] == "block":
        block = set(self.glob_confman.get_value("modules", "BLOCKLIST", []))
        for mod in arg[1].split(","):
            block.add(mod)
        self.glob_confman.set_value("modules", "BLOCKLIST", list(block))
        self.conman.gen_send("Blocked %s modules" % len(arg[1].split(",")))
    if arg[0] == "unblock":
        block = set(self.glob_confman.get_value("modules", "BLOCKLIST", []))
        for mod in arg[1].split(","):
            block.remove(mod)
        self.glob_confman.set_value("modules", "BLOCKLIST", list(block))
        self.conman.gen_send("Unblocked %s modules" % len(arg[1].split(",")))

self.permsman.suggest_cmd_perms("module", 999)
self._map("command", "module", mod_parse)
self._map("help", "module", ".module - Controls what modules should be loaded. Arguments are list, block and unblock. (un)block accepts comma-delimited arguments")
