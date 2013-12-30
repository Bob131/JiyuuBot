#Help module to display command definitions to channel
def display_help(self, command):
    cmdlist = "%s commands available: " % len(self.helplist)
    for keys in self.helplist.keys():
        cmdlist += ".%s " % keys
    self.conman.privmsg(cmdlist)
    if not command == "":
        if command.startswith("."):
            command = command[1:]
        try:
            self.conman.privmsg(self.helplist[command])
        except:
            self.conman.privmsg("Help for %s not available" % command)

#Maps command and help text for command
self._map("command", "help", display_help)
self._map("help", "help", ".help - displays help")
