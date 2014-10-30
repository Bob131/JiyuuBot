def announce(self, command):
    import random
    filelist = os.listdir(os.path.join(self.glob_confman.get("MPD", "MUSIC_PATH"), self.glob_confman.get("IRC", "NICK", allowTemp=False) + "_intros"))
    filepath = ""
    filepath = filelist[random.randint(0, len(filelist)-1)]
    filepath = os.path.join(self.glob_confman.get("IRC", "NICK", allowTemp=False) + "_intros", filepath)
    self.conman.mpc.addid(filepath, 1)

self.commandlist["announce"] = {
        "type": MAPTYPE_COMMAND,
        "function": announce,
        "help": "adds an intro track to the queue"
        }
