def add_random(self, command):
    import random
    filelist = os.listdir(os.path.join(MUSIC_PATH, NICK + "_downloaded_music"))
    numsongs = int(self.confman.get_value("add_random", "NUMBER_OF_SONGS", 10))
    for i in range(1,numsongs):
        filepath = filelist[random.randint(0, len(filelist)-1)]
        filepath = os.path.join(NICK + "_downloaded_music", filepath)
        # this is just a quick solution so that we didn't have so much fucking Dragonforce playing all the time
        if not os.path.isdir(os.path.join(MUSIC_PATH, filepath)):
            try:
                self.conman.mpc.add(filepath)
            except mpd.MPDError:
                pass

self.map_command("random", add_random)
self.map_help("random", ".random - adds 10 random tracks to the queue")
