def next_track(self, command):
    self.conman.mpc.next()

self.commandlist["next"] = {
        "type": MAPTYPE_COMMAND,
        "function": next_track,
        "help": "skips currently playing track"
        }
