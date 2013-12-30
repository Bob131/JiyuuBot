def next_track(self, command):
    self.conman.mpc.next()

self._map("command", "next", next_track)
self._map("help", "next", ".next - skips currently playing track")
