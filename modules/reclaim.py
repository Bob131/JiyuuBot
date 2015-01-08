@self.irc(432)
@self.irc(433)
def nickname_taken(self, msginfo):
    self.conman.privmsg("Nickname request failed: Nickname is in use")
    self.glob_confman.setv("IRC", "NICK", self.glob_confman.get("IRC", "NICK")+"_", temp=True)
    self.conman.queue_raw("NICK " + self.glob_confman.get("IRC", "NICK"))


@self.irc("NICK")
def mandated_nick(self, msginfo):
    # if NICK is referring to us
    if msginfo["strg"].split(" ")[0].split("@")[-1] == self.glob_confman.get("IRC", "HOSTNAME"):
        nick = msginfo["strg"].split("NICK")[-1].replace(":", "", 1).strip()
        if not nick == self.glob_confman.get("IRC", "NICK"):
            self.glob_confman.setv("IRC", "NICK", nick, temp=True)

self.alias("claim", "reclaim")

@self.command(help="Attempt to reclaim nick as defined in config.json", perm=900)
def reclaim(self, msginfo):
    if len(msginfo["msg"].split(" ")) > 1:
        self.glob_confman.setv("IRC", "NICK", msginfo["msg"].split(" ")[1], temp=True)
        self.conman.queue_raw("NICK {}".format(msginfo["msg"].split(" ")[1]))
        self.conman.queue
    else:
        #flush temporary nick
        self.glob_confman.load(True)
        #set new nick
        self.conman.queue_raw("NICK {}".format(self.glob_confman.get("IRC", "NICK")))
