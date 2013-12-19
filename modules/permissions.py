def set_perm_nick(self, nick, lvl):
    self.conman.privmsg("Setting permission level for %s: %s" % (nick, lvl))
    self.permsman.set_nick_perms(nick, lvl)

def get_perm_nick(self, args):
    self.conman.privmsg("Permission level for %s: %s" % (args, self.permsman.get_nick_perms(args)))

def set_perm_cmd(self, cmd, lvl):
    self.conman.privmsg("Setting permission level for %s: %s" % (cmd, lvl))
    self.permsman.set_cmd_perms(cmd, lvl)

def get_perm_cmd(self, args):
    self.conman.privmsg("Permission level for %s: %s" % (args, self.permsman.get_cmd_perms(args)))

def get_perm_argparser(self, args):
    args = args.split(" ")
    if args[0] == "nick":
        self.get_perm_nick(self, args[1])
    elif args[0] == "cmd":
        self.get_perm_cmd(self, args[1])

def set_perm_argparser(self, args):
    args = args.split(" ")
    if args[0] == "nick":
        self.set_perm_nick(self, args[1], args[2])
    elif args[0] == "cmd":
        self.set_perm_cmd(self, args[1], args[2])

self.get_perm_nick = get_perm_nick
self.set_perm_nick = set_perm_nick
self.get_perm_cmd = get_perm_cmd
self.set_perm_cmd = set_perm_cmd
self.map_command("getperm", get_perm_argparser, False)
self.map_command("setperm", set_perm_argparser, False)
