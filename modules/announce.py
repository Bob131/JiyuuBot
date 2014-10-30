def announce(self, command):
    import random
    filelist = self.conman.mpc.listall("/%s_intros" % self.glob_confman.get("IRC", "NICK"))
    filepath = filelist[random.randint(0, len(filelist)-1)]
    self.conman.mpc.addid(filepath, 1)

self.commandlist["announce"] = {
        "type": MAPTYPE_COMMAND,
        "function": announce,
        "help": "adds an intro track to the queue"
        }
