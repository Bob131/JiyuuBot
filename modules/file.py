def rfile(self, asdasd):
    tosend = self.conman.mpc.currentsong()
    if type(tosend) == list:
        tosend = tosend[0]
    self.conman.gen_send("\"%s\"" % tosend["file"])

self._map("http", "file", rfile)
