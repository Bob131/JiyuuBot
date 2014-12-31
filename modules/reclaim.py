def nickname_taken(self, msginfo):
    self.conman.privmsg("Nickname request failed: Nickname is in use")
    self.glob_confman.setv("IRC", "NICK", self.glob_confman.get("IRC", "NICK")+"_", temp=True)
    self.conman.queue_raw("NICK " + self.glob_confman.get("IRC", "NICK"))


def mandated_nick(self, msginfo):
    # if NICK is referring to us
    if msginfo["strg"].split(" ")[0].split("@")[-1] == self.glob_confman.get("IRC", "HOSTNAME"):
        nick = msginfo["strg"].split("NICK")[-1].replace(":", "", 1).strip()
        if not nick == self.glob_confman.get("IRC", "NICK"):
            self.glob_confman.setv("IRC", "NICK", nick, temp=True)


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


self.permsman.suggest_cmd_perms("reclaim", 999)
self.commandlist["reclaim"] = {
        "type": MAPTYPE_COMMAND,
        "function": reclaim,
        "help": "Attempt to reclaim nick as defined in config.json"
        }
self.permsman.suggest_cmd_perms("claim", 999)
self.commandlist["claim"] = {
        "type": MAPTYPE_ALIAS,
        "pointer": "reclaim"
        }
self.commandlist["!433"] = {
        "type": MAPTYPE_OTHER,
        "function": nickname_taken
        }
self.commandlist["!432"] = {
        "type": MAPTYPE_OTHER,
        "function": nickname_taken
        }
self.commandlist["!NICK"] = {
        "type": MAPTYPE_OTHER,
        "function": mandated_nick
        }
