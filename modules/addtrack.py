def add_tracks(self, msginfo):
    arg = msginfo["msg"][msginfo["msg"].index(" ")+1:]
    matches = self.conman.mpc.search("any", arg)
    if len(matches) > 1:
        import random
        self.conman.gen_send("%s results for search \"%s\"; selecting one at random" % (len(matches), arg), msginfo)
        rand = random.randint(0, len(matches)-1)
        self.conman.gen_send("Adding %s" % matches[rand]["file"], msginfo)
        self.conman.mpc.add(matches[rand]["file"])
    elif len(matches) == 0:
        self.conman.gen_send("No songs matching \"%s\"" % arg, msginfo)
    else:
        self.conman.mpc.add(matches[0]["file"])

self.commandlist["add"] = {
        "type": MAPTYPE_COMMAND,
        "function": add_tracks,
        "help": "adds tracks to the queue"
        }
