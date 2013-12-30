def current(self, lel):
    self.require("format_song_details")
    currentTrack = self.conman.mpc.currentsong()
    self.conman.privmsg(self.run_func("format_song_details", [currentTrack["file"]]))

self.map_command("current", current)
self.map_help("current", ".current - displays current track info")
