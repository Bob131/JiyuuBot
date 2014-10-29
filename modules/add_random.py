def add_random(self, command):
    import random
    global selected_songs
    filelist = []
    for root, dirs, files in os.walk(MUSIC_PATH):
        for name in files:
            root = root.replace(MUSIC_PATH + os.sep, "")
            filelist.append(os.path.join(root, name))
    numsongs = int(self.confman.get_value("add_random", "NUMBER_OF_SONGS", 10))
    for i in range(1,numsongs):
        if len(selected_songs) == len(filelist):
            selected_songs = []
        filepath = ""
        while 1:
            filepath = filelist[random.randint(0, len(filelist)-1)]
            if not filepath.endswith(".m3u") and not filepath in selected_songs and not NICK + "_intros" + os.sep in filepath:
                continue
        selected_songs.append(filepath)
        try:
            self.conman.mpc.add(filepath)
        except mpd.MPDError:
            pass

selected_songs = []
self._map("command", "random", add_random)
self._map("help", "random", ".random - adds %s random tracks to the queue" % self.confman.get_value("add_random", "NUMBER_OF_SONGS", 10))
