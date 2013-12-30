#Module to display queue of songs from MPCD
def queue(self, command):
    self.require("format_song_details")
    queue = self.conman.mpc.playlist()
    queuestr = "Next 4 of %s tracks:\n" % len(queue)
    for track in queue[ : 4]:
        track = track.replace("file: ", "")
        queuestr += self.run_func("format_song_details", [track])+"\n"
    self.conman.privmsg(queuestr)

#Maps command and help text for command
self.map_command("queue", queue)
self.map_help("queue", ".queue - displays the next 4 queued songs")
