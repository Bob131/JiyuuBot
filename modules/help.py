#Help module to display command definitions to channel
def display_help(self, command):
    cmdlist = "Available commands: "
    for keys in self.helpcommandlist:
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
self.map_command("help", display_help)
self.map_help("help", ".help - displays help")
