def broadcast(self, msginfo):
    arg = msginfo["msg"][msginfo["msg"].index(" ")+1:]
    for chan in self.conman.joined_chans:
        msginfo["chan"] = chan
        self.conman.gen_send(arg, msginfo)

self.permsman.suggest_cmd_perms("broadcast", 999)
self.commandlist["broadcast"] = {
        "type": MAPTYPE_COMMAND,
        "function": broadcast,
        "prefix": "NOTICE"
        }
