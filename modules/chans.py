def chans(self, cmd):
    tosend = ", ".join(self.conman.joined_chans)
    tosend = "%s channels currently served by %s: %s" % (len(self.conman.joined_chans), NICK, tosend)
    self.conman.gen_send(tosend)

self._map("command", "chans", chans)
self._map("help", "chans", ".chans - Displays channels being served")
