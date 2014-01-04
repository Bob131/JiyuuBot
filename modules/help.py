#Help module to display command definitions to channel
def display_help(self, command):

    if thread_types[threading.current_thread().ident] == "HTTP":
        values = {}
        values["cmdno"] = len(self.httplist)
        values["cmds"] = []
        for keys in self.httplist.keys():
            values["cmds"].append(keys)
        self.conman.gen_send(json.dumps(values, sort_keys=True, indent=4, separators=(',', ': ')))
    else:
        cmdlist = "%s commands available: " % len(self.helplist)
        for keys in self.helplist.keys():
            cmdlist += ".%s " % keys
        self.conman.gen_send(cmdlist)
        if not command == "":
            if command.startswith("."):
                command = command[1:]
            try:
                self.conman.gen_send(self.helplist[command])
            except:
                self.conman.gen_send("Help for %s not available" % command)

#Maps command and help text for command
self._map("command", "help", display_help)
self._map("http", "help", display_help)
self._map("help", "help", ".help - displays help")
