def get_perm_argparser(self, msginfo):
    args = msginfo["msg"].split(" ")[1:]
    if len(args) == 0:
        args = ["host", msginfo["hostname"]]
    if args[0] == "host":
        self.conman.gen_send("Permission level for %s: %s" % (args[1], self.permsman.get_host_perms(args[1])), msginfo)
    elif args[0] == "cmd":
        if args[1].startswith("."):
            args[1] = args[1][1:]
        self.conman.gen_send("Permission level for %s: %s" % (args[1], self.permsman.get_cmd_perms(args[1])), msginfo)
    elif args[0] == "msg":
        self.conman.gen_send("Message permissions for %s: %s" % (args[1], self.permsman.get_msg_perms(args[1])), msginfo)

def set_perm_argparser(self, msginfo):
    args = msginfo["msg"].split(" ")[1:]
    if args[0] == "host":
        self.conman.gen_send("Setting permission level for %s: %s" % (args[1], args[2]), msginfo)
        self.permsman.set_host_perms(args[1], args[2])
    elif args[0] == "cmd":
        if args[1].startswith("."):
            args[1] = args[1][1:]
        self.conman.gen_send("Setting permission level for %s: %s" % (args[1], args[2]), msginfo)
        self.permsman.set_cmd_perms(args[1], args[2])
    elif args[0] == "msg":
        args[2] = args[2].lower() == "true" or args[2] == "1"
        self.conman.gen_send("Setting message permissions for %s: %s" % (args[1], args[2]), msginfo)
        self.permsman.set_msg_perms(args[1], args[2])

self.commandlist["getperm"] = {
        "type": MAPTYPE_COMMAND,
        "function": get_perm_argparser,
        "help": "Get permission info. Called on its own, it returns the permission level for your hostname. Syntax: .getperm [(msg <hostname>)|(cmd <command>)|(host <hostname>)]"
        }
self.commandlist["setperm"] = {
        "type": MAPTYPE_COMMAND,
        "function": set_perm_argparser,
        "help": "Set permission info. Syntax: .setperm (msg <hostname> <true or false>)|(cmd <command> <perm level>)|(host <hostname> <perm level>)"
        }
self.permsman.suggest_cmd_perms("setperm", 999)
