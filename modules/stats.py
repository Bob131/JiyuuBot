#Define function to display stats of MPCD
def stats(self, cmd):
    self.conman.privmsg(self.conman.mpc.stats())

#Maps command and help text for command
self.map_command("stats", stats)
self.map_help("stats", ".stats - prints MPD statistics")
