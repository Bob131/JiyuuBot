def leave(self, msginfo):
    #TODO: Reimplement
    #if self.permsman.get_msg_perms(info["nick"]):
    cmd = msginfo["msg"].split(" ")[1:]
    if len(cmd) == 0:
        self.conman.leave_irc(msginfo["chan"], msginfo["nick"])
    else:
        for chan in cmd:
            if chan in self.conman.joined_chans:
                self.conman.leave_irc(chan, msginfo["nick"])
            else:
                self.conman.gen_send("Can't PART from a channel that hasn't been joined", msginfo)

self.commandlist["leave"] = {
        "type": MAPTYPE_COMMAND,
        "function": leave
        }
