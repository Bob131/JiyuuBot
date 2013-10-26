def add_random(self, command):
    import random
    global selected_songs
    filelist = os.listdir(os.path.join(MUSIC_PATH, NICK + "_downloaded_music"))
    numsongs = int(self.confman.get_value("add_random", "NUMBER_OF_SONGS", 10))
    for i in range(1,numsongs):
        if len(selected_songs) == len(filelist):
            selected_songs = []
        filepath = ""
        while 1:
            filepath = filelist[random.randint(0, len(filelist)-1)]
            filepath = os.path.join(NICK + "_downloaded_music", filepath)
            # this is just a quick solution so that we didn't have so much fucking Dragonforce playing all the time
            if not os.path.isdir(os.path.join(MUSIC_PATH, filepath)) and not filepath in selected_songs:
                break
        selected_songs.append(filepath)
        try:
            self.conman.mpc.add(filepath)
        except mpd.MPDError:
            pass

selected_songs = []
self.map_command("random", add_random)
self.map_help("random", ".random - adds 10 random tracks to the queue")
