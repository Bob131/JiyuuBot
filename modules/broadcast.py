def broadcast(self, msginfo):
    arg = msginfo["msg"][msginfo["msg"].index(" ")+1:]
    self.conman.broadcast(arg)

self.permsman.suggest_cmd_perms("broadcast", 999)
self.commandlist["broadcast"] = {
        "type": MAPTYPE_COMMAND,
        "function": broadcast
        }
