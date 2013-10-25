def next_track(self, command):
    self.conman.mpc.next()

self.map_command("next", next_track)
self.map_help("next", ".next - skips currently playing track")
