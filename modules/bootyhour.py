def booty_hour(self, command):
    for i in range(1,90):
        self.conman.mpc.add(self.glob_confman.get("IRC", "NICK", allowTemp=False)+"_downloaded_music/How to pronounce ( ͡° ͜ʖ ͡°) - from YouTube by Offliberty.mp3")

self.commandlist["bootyhour"] = {
        "type": MAPTYPE_COMMAND,
        "function": booty_hour
        }
