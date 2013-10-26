def announce(self, command):
    import random
    filelist = os.listdir(os.path.join(MUSIC_PATH, NICK + "_intros"))
    filepath = filelist[random.randint(0, len(filelist)-1)]
    filepath = os.path.join(NICK + "_intros", filepath)
    self.conman.privmsg("Adding %s" % filepath)
    self.conman.mpc.addid(filepath, 1)

self.map_command("announce", announce)
self.map_help("announce", ".announce - adds an intro track to the queue")
