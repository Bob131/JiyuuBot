@self.command(help="Get permission info. Called on its own, it returns the permission level for your hostname. Syntax: .getperm [(msg <hostname>)|(cmd <command>)|(host <hostname>)]")
def getperm(self, msginfo):
    args = msginfo["msg"].split(" ")[1:]
    if len(args) == 0:
        args = ["host", msginfo["hostname"]]
    if args[0] == "host":
        self.conman.gen_send("Permission level for %s: %s" % (args[1], self.permsman.get_host_perms(args[1])), msginfo)
    elif args[0] == "cmd":
        if args[1].startswith("."):
            args[1] = args[1][1:]
        if self.commandlist[args[1]]["type"] == MAPTYPE_ALIAS:
            args[1] = self.commandlist[args[1]]["pointer"]
        self.conman.gen_send("Permission level for %s: %s" % (args[1], self.permsman.get_cmd_perms(args[1])), msginfo)
    elif args[0] == "msg":
        self.conman.gen_send("Message permissions for %s: %s" % (args[1], self.permsman.get_msg_perms(args[1])), msginfo)

@self.command(help="Set permission info. Syntax: .setperm (msg <hostname> <true or false>)|(cmd <command> <perm level>)|(host <hostname> <perm level>)", perm=999)
def setperm(self, msginfo):
    args = msginfo["msg"].split(" ")[1:]
    if args[0] == "host":
        self.conman.gen_send("Setting permission level for %s: %s" % (args[1], args[2]), msginfo)
        self.permsman.set_host_perms(args[1], args[2])
    elif args[0] == "cmd":
        if args[1].startswith("."):
            args[1] = args[1][1:]
        if self.commandlist[args[1]]["type"] == MAPTYPE_ALIAS:
            args[1] = self.commandlist[args[1]]["pointer"]
        self.conman.gen_send("Setting permission level for %s: %s" % (args[1], args[2]), msginfo)
        self.permsman.set_cmd_perms(args[1], args[2])
    elif args[0] == "msg":
        args[2] = args[2].lower() == "true" or args[2] == "1"
        self.conman.gen_send("Setting message permissions for %s: %s" % (args[1], args[2]), msginfo)
        self.permsman.set_msg_perms(args[1], args[2])
