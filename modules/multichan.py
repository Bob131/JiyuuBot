def chans(self, msginfo):
    tosend = ", ".join(self.conman.joined_chans)
    tosend = "%s channels currently served by %s: %s" % (len(self.conman.joined_chans), self.glob_confman.get("IRC", "NICK"), tosend)
    self.conman.gen_send(tosend, msginfo)


def leave(self, msginfo):
    if self.permsman.get_msg_perms(msginfo["hostname"]):
        cmd = msginfo["msg"].split(" ")[1:]
        if len(cmd) == 0:
            self.conman.leave_irc(msginfo["chan"], msginfo["nick"])
        else:
            for chan in cmd:
                if chan in self.conman.joined_chans:
                    self.conman.leave_irc(chan, msginfo["nick"])
                else:
                    self.conman.gen_send("Can't PART from a channel that hasn't been joined", msginfo)


def join(self, msginfo):
    if self.permsman.get_msg_perms(msginfo["hostname"]):
        cmd = msginfo["msg"].split(" ")[1:]
        for chan in cmd:
            if not chan in self.conman.joined_chans:
                self.conman.join_irc(chan, msginfo["nick"])
            else:
                self.conman.gen_send("Already serving {}".format(chan), msginfo)


def invite(self, msginfo):
    hostname = msginfo["strg"][msginfo["strg"].index("@")+1:msginfo["strg"].index(" ")]
    if self.permsman.get_msg_perms(hostname):
        nick = msginfo["strg"][:msginfo["strg"].index("!")]
        chan = msginfo["strg"][msginfo["strg"].index(" :")+2:]
        self.conman.join_irc(chan, nick)


def kick(self, msginfo):
    beingkicked = msginfo["strg"][msginfo["strg"].rindex(":")+1:]
    NICK = self.glob_confman.get("IRC", "NICK")
    if beingkicked == NICK:
        chan = re.findall("(#[^\s,]+)", msginfo["strg"])[0]
        nick = msginfo["strg"][:msginfo["strg"].index("!")]
        self.conman.leave_irc(chan, nick, True)



self.commandlist["chans"] = {
        "type": MAPTYPE_COMMAND,
        "function": chans,
        "help": "Displays channels being served"
        }
self.commandlist["leave"] = {
        "type": MAPTYPE_COMMAND,
        "function": leave
        }
self.commandlist["join"] = {
        "type": MAPTYPE_COMMAND,
        "function": join
        }
self.commandlist["!INVITE"] = {
        "type": MAPTYPE_OTHER,
        "function": invite
        }
self.commandlist["!KICK"] = {
        "type": MAPTYPE_OTHER,
        "function": kick
        }
