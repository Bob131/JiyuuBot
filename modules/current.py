def current(self, msginfo):
    self.require("format_song_details")
    currentTrack = self.conman.mpc.currentsong()
    if type(currentTrack) == list:
        currentTrack = currentTrack[0]
    tosend = self.funcs["format_song_details"](self, currentTrack["file"])
    self.conman.gen_send(tosend, msginfo)

self.commandlist["current"] = {
        "type": MAPTYPE_COMMAND,
        "function": current,
        "help": "displays current track info"
        }
