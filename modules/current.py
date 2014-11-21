def current(self, msginfo):
    import datetime
    self.require("formatdetails")
    currentTrack = self.conman.mpc.currentsong()
    if type(currentTrack) == list:
        currentTrack = currentTrack[0]
    tosend = self.funcs["format_song_details"](self, currentTrack["file"])
    status = self.conman.mpc.status()
    elapsed = str(datetime.timedelta(seconds=int(status["time"][:status["time"].index(":")])))
    while elapsed.startswith("0") or elapsed.startswith(":"):
        elapsed = elapsed[1:]
    tosend = tosend[:tosend.rindex("-")+2] + elapsed + "/" + tosend[tosend.rindex("-")+2:]
    self.conman.gen_send(tosend, msginfo)

self.commandlist["current"] = {
        "type": MAPTYPE_COMMAND,
        "function": current,
        "help": "displays current track info"
        }
