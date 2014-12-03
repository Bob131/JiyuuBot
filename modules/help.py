#Help module to display command definitions to channel
def display_help(self, msginfo):
    args = msginfo["msg"].split(" ")[1:]
    if len(args) == 0:
        cmdlist = []
        for keys in self.commandlist.keys():
            if self.commandlist[keys].get("help", None):
                cmdlist.append("."+keys)
        self.conman.gen_send("%s commands available:" % len(cmdlist), msginfo)
        self.conman.gen_send(" ".join(cmdlist), msginfo)
    else:
        for arg in args:
            if arg.startswith("."):
                arg = arg[1:]
            # copy to preserve post-alias resolve
            argo = arg
            try:
                if self.commandlist[arg]["type"] == MAPTYPE_ALIAS:
                    arg = self.commandlist[arg]["pointer"]
                self.conman.gen_send(".%s - %s" % (argo, self.commandlist[arg]["help"]), msginfo)
            except:
                self.conman.gen_send("Help for %s not available" % command, msginfo)

#Maps command and help text for command
self.commandlist["help"] = {
        "type": MAPTYPE_COMMAND,
        "function": display_help,
        "help": "displays help. Syntax: .help [command]"
        }
