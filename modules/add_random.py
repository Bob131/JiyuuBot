def add_random(self, _):
    import random
    numsongs = int(self.confman.get("add_random", "NUMBER_OF_SONGS", 10))
    mpdsongs = int(self.conman.mpc.stats()["songs"])
    while numsongs:
        sid = random.randint(0, mpdsongs-1)
        try:
            self.conman.mpc.addid(self.conman.mpc.songlist[sid])
            numsongs-=1
        except mpd.MPDError:
            pass

self.commandlist["random"] = {
        "type": MAPTYPE_COMMAND,
        "function": add_random,
        "help": "adds %s random tracks to the queue" % self.confman.get("add_random", "NUMBER_OF_SONGS", 10)
        }
