#Define function to display stats of MPCD
def stats(self, cmd):
    import datetime
    statsdict = self.conman.mpc.stats()
    self.conman.privmsg("Uptime: %s - Playtime: %s" % (datetime.timedelta(seconds=int(statsdict["uptime"])), datetime.timedelta(seconds=int(statsdict["playtime"]))))
    self.conman.privmsg("Artists: %s - Albums: %s - Songs: %s" % (statsdict["artists"], statsdict["albums"], statsdict["songs"]))

#Maps command and help text for command
self.map_command("stats", stats)
self.map_help("stats", ".stats - prints MPD statistics")
