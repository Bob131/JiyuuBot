@self.irc("JOIN")
def who(self, msginfo):
    nick = msginfo["strg"][:msginfo["strg"].index("!")]
    chan = re.findall("(#[^\s,]+)", msginfo["strg"])[0]
    host = msginfo["strg"][msginfo["strg"].index("@")+1:msginfo["strg"].index(" ")]
    if not chan in self.confman.get("join", "quiet_chans", []) and not host in self.confman.get("join", "quiet_hosts", []):
        self.conman.queue_raw("NOTICE {} :{}".format(nick, self.confman.get("join", "greeter", "Hello {nick}, welcome to {chan}!").format(nick=nick, chan=chan)))


@self.command("quiet", help="Suppresses join messages for channel. Defaults to current channel. Syntax: .quiet [channel]")
@self.command("dequiet", help="Enables join messages for channel. Defaults to current channel. Syntax: .dequiet [channel]")
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


@self.command("shuush", help="Suppresses join messages for your hostname")
@self.command("deshuush", help="Enables join messages for your hostname")
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
