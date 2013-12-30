def add_tracks(self, arg):
    matches = self.conman.mpc.search("any", arg)
    if len(matches) > 1:
        import random
        self.conman.privmsg("%s results for search \"%s\"; selecting one at random" % (len(matches), arg))
        rand = random.randint(0, len(matches)-1)
        self.conman.privmsg("Adding %s" % matches[rand]["file"])
        self.conman.mpc.add(matches[rand]["file"])
    elif len(matches) == 0:
        self.conman.privmsg("No songs matching \"%s\"" % arg)
    else:
        self.conman.mpc.add(matches[0]["file"])

self._map("command", "add", add_tracks)
self._map("help", "add", ".add - adds tracks to the queue")
