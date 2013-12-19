def set_perm_nick(self, nick, lvl):
    self.conman.privmsg("Setting permission level for %s: %s" % (nick, lvl))
    self.permsman.set_nick_perms(nick, lvl)

def get_perm_nick(self, args):
    self.conman.privmsg("Permission level for %s: %s" % (args, self.permsman.get_nick_perms(args)))

def get_perm_argparser(self, args):
    args = args.split(" ")
    if args[0] == "nick":
        self.get_perm_nick(self, args[1])

def set_perm_argparser(self, args):
    args = args.split(" ")
    if args[0] == "nick":
        self.get_perm_nick(self, args[1], args[2])

self.get_perm_nick = get_perm_nick
self.set_perm_nick = set_perm_nick
self.map_command("getperm", get_perm_argparser)
self.map_command("setperm", set_perm_argparser)
