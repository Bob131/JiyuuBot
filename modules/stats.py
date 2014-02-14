#Define function to display stats of MPCD
def stats(self, cmd):
    statsdict = self.conman.mpc.stats()
    if thread_types[threading.current_thread().ident] == "HTTP":
        self.conman.gen_send(json.dumps(statsdict, sort_keys=True, indent=4, separators=(',', ': ')))
    else:
        import datetime
        self.conman.gen_send("Uptime: %s - Playtime: %s" % (datetime.timedelta(seconds=int(statsdict["uptime"])), datetime.timedelta(seconds=int(statsdict["playtime"]))))
        self.conman.gen_send("Artists: %s - Albums: %s - Songs: %s" % (statsdict["artists"], statsdict["albums"], statsdict["songs"]))

#Maps command and help text for command
self._map("command", "stats", stats)
self._map("http", "stats", stats)
self._map("help", "stats", ".stats - prints MPD statistics")
