def announce(self, command):
    import random
    filelist = os.listdir(os.path.join(MUSIC_PATH, NICK + "_intros"))
    filepath = ""
    filepath = filelist[random.randint(0, len(filelist)-1)]
    filepath = os.path.join(NICK + "_intros", filepath)
    self.conman.mpc.addid(filepath, 1)

self.commandlist["announce"] = {
        "type": MAPTYPE_COMMAND,
        "function": announce,
        "help": "adds an intro track to the queue"
        }
