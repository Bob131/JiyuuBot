def nickname_taken(self, msginfo):
    self.conman.privmsg("Nickname reclamation failed: Nickname is in use")
    self.glob_confman.setv("IRC", "NICK", self.glob_confman.get("IRC", "NICK")+"_", temp=True)
    self.conman.queue_raw("NICK " + self.glob_confman.get("IRC", "NICK"))


def mandated_nick(self, msginfo):
    nick = msginfo["strg"].split(":")[-1].strip()
    if not nick == self.glob_confman.get("IRC", "NICK"):
        self.glob_confman.setv("IRC", "NICK", nick, temp=True)


def reclaim(self, msginfo):
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
self.commandlist["!433"] = {
        "type": MAPTYPE_OTHER,
        "function": nickname_taken
        }
self.commandlist["!NICK"] = {
        "type": MAPTYPE_OTHER,
        "function": mandated_nick
        }
