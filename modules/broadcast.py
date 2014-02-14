def broadcast(self, command):
    for chan in self.conman.joined_chans:
        self.conman.privmsg(command, chan, "NOTICE: ")

self.permsman.suggest_cmd_perms("broadcast", 999)
self._map("command", "broadcast", broadcast)
