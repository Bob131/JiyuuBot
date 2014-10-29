#Define function to display stats of MPD
def stats(self, msginfo):
    statsdict = self.conman.mpc.stats()
    import datetime
    self.conman.gen_send("Uptime: %s - Playtime: %s" % (datetime.timedelta(seconds=int(statsdict["uptime"])), datetime.timedelta(seconds=int(statsdict["playtime"]))), msginfo)
    self.conman.gen_send("Artists: %s - Albums: %s - Songs: %s" % (statsdict["artists"], statsdict["albums"], statsdict["songs"]), msginfo)

#Maps command and help text for command
self.commandlist["stats"] = {
        "type": MAPTYPE_COMMAND,
        "function": stats,
        "help": "prints MPD statistics"
        }
