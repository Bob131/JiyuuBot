def who(self, msginfo):
    nick = msginfo["strg"][:msginfo["strg"].index("!")]
    chan = re.findall("(#[^\s,]+)", msginfo["strg"])[0]
    host = msginfo["strg"][msginfo["strg"].index("@")+1:msginfo["strg"].index(" ")]
    if not chan in self.confman.get("join", "quiet_chans", []) and not host in self.confman.get("join", "quiet_hosts", []):
        self.conman.privmsg(self.confman.get("join", "greeter", "Hello {}, welcome to {}!").format(nick, chan), chan)


def quiet(self, msginfo):
    try:
        chan = msginfo["msg"].split(" ")[1]
    except IndexError:
        chan = msginfo["chan"]
    if self.permsman.get_msg_perms(msginfo["hostname"]):
        chanlist = set(self.confman.get("join", "quiet_chans", []))
        if msginfo["msg"].startswith(".quiet"):
            self.conman.gen_send("Silencing join messages for {}".format(chan), msginfo)
            chanlist.add(chan)
        else:
            self.conman.gen_send("Enabling join messages for {}".format(chan), msginfo)
            try:
                chanlist.remove(chan)
            except KeyError:
                pass
        self.confman.setv("join", "quiet_chans", list(chanlist))
    else:
        self.conman.gen_send("You don't have permission to do that", msginfo)


def shuush(self, msginfo):
    hostlist = set(self.confman.get("join", "quiet_hosts", []))
    if msginfo["msg"].startswith(".shuush"):
        self.conman.gen_send("Silencing join messages for {}".format(msginfo["hostname"]), msginfo)
        hostlist.add(msginfo["hostname"])
    else:
        self.conman.gen_send("Enabling join messages for {}".format(msginfo["hostname"]), msginfo)
        try:
            hostlist.remove(msginfo["hostname"])
        except KeyError:
            pass
    self.confman.setv("join", "quiet_hosts", list(hostlist))



self.commandlist["!JOIN"] = {
        "type": MAPTYPE_OTHER,
        "function": who
        }
self.commandlist["quiet"] = {
        "type": MAPTYPE_COMMAND,
        "function": quiet,
        "help": "Suppresses join messages for channel. Defaults to current channel. Syntax: .quiet [channel]"
        }
self.commandlist["dequiet"] = {
        "type": MAPTYPE_COMMAND,
        "function": quiet,
        "help": "Enables join messages for channel. Defaults to current channel. Syntax: .dequiet [channel]"
        }
self.commandlist["shuush"] = {
        "type": MAPTYPE_COMMAND,
        "function": shuush,
        "help": "Suppresses join messages for your hostname"
        }
self.commandlist["deshuush"] = {
        "type": MAPTYPE_COMMAND,
        "function": shuush,
        "help": "Enables join messages for your hostname"
        }
