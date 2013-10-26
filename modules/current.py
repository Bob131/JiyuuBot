def current(self, lel):
    currentTrack = self.conman.mpc.currentsong()
    if not currentTrack.get('time', "N/A") == "N/A":
        m, s = divmod(int(currentTrack.get('time', "N/A")), 60)
        time = "%d:%d" % (m, s)
    else:
        time = "N/A"
    title = currentTrack.get('title',"N/A")
    if title == "N/A":
        title = os.path.basename(currentTrack.get("file", "N/A")).replace(" - ", " ")
    parse = currentTrack.get('artist',"N/A") + " - " + currentTrack.get('album',"N/A") + " - " + title + " - " + time
    self.conman.privmsg(parse)

self.map_command("current", current)
self.map_help("current", ".current - displays current track info")
