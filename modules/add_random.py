def add_random(self, _):
    import random
    filelist = []
    for root, dirs, files in os.walk(self.glob_confman.get("MPD", "MUSIC_PATH")):
        for name in files:
            root = root.replace(self.glob_confman.get("MPD", "MUSIC_PATH") + os.sep, "")
            filelist.append(os.path.join(root, name))
    numsongs = int(self.confman.get("add_random", "NUMBER_OF_SONGS", 10))
    while numsongs:
        filepath = filelist[random.randint(0, len(filelist)-1)]
        if not filepath.endswith(".m3u") and not NICK + "_intros" + os.sep in filepath:
            try:
                self.conman.mpc.add(filepath)
                numsongs-=1
            except mpd.MPDError:
                pass

self.commandlist["random"] = {
        "type": MAPTYPE_COMMAND,
        "function": add_random,
        "help": "adds %s random tracks to the queue" % self.confman.get("add_random", "NUMBER_OF_SONGS", 10)
        }
