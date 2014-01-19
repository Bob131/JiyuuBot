def chans(self, cmd):
    tosend = ", ".join(self.conman.joined_chans)
    tosend = "Channels currently served by %s: %s" % (NICK, tosend)
    self.conman.gen_send(tosend)

self._map("command", "chans", chans)
self._map("help", "chans", ".chans - Displays channels being served")
