def update(self, command):
    self.conman.mpc.update()

self.commandlist["update"] = {
        "type": MAPTYPE_COMMAND,
        "function": update,
        "help": "Update MPD database"
        }
