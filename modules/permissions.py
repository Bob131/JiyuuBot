def get_perm_argparser(self, args):
    args = args.split(" ")
    if args[0] == "nick":
        self.conman.gen_send("Permission level for %s: %s" % (args[1], self.permsman.get_nick_perms(args[1])))
    elif args[0] == "cmd":
        if args[1].startswith("."):
            args[1] = args[1][1:]
        self.conman.gen_send("Permission level for %s: %s" % (args[1], self.permsman.get_cmd_perms(args[1])))
    elif args[0] == "msg":
        self.conman.gen_send("Message permissions for %s: %s" % (args[1], self.permsman.get_msg_perms(args[1])))

def set_perm_argparser(self, args):
    args = args.split(" ")
    if args[0] == "nick":
        self.conman.gen_send("Setting permission level for %s: %s" % (args[1], args[2]))
        self.permsman.set_nick_perms(args[1], args[2])
    elif args[0] == "cmd":
        if args[1].startswith("."):
            args[1] = args[1][1:]
        self.conman.gen_send("Setting permission level for %s: %s" % (args[1], args[2]))
        self.permsman.set_cmd_perms(args[1], args[2])
    elif args[0] == "msg":
        args[2] = args[2].lower() == "true" or args[2] == "1"
        self.conman.gen_send("Setting message permissions for %s: %s" % (args[1], args[2]))
        self.permsman.set_msg_perms(args[1], args[2])

self._map("command", "getperm", get_perm_argparser)
self._map("command", "setperm", set_perm_argparser)
