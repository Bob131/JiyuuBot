def get_perm_nick(self, args):
    self.conman.privmsg("Permission level for %s: %s" % (args, self.permsman.get_nick_perms(args)))

def perm_argparser(self, args):
    args = args.split(" ")
    if args[1] == "nick":
        self.get_perm_nick(self, args[2])

self.get_perm_nick = get_perm_nick
self.map_command("perm", perm_argparser)
