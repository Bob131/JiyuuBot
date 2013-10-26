def current(self, lel):
    self.conman.privmsg(self.conman.mpc.currentsong())

self.map_command("current", current)
self.map_help("current", ".current - displays current track info")
