#Module to display queue of songs from MPCD
def queue(self, command):
    self.require("format_song_details")
    queue = self.conman.mpc.playlist()
    try:
        if not command == "":
            if int(command) <= 0 or int(command) == len(queue):
                raise Exception("")
            queue = queue[int(command):]
    except:
        raise Exception("Invalid song id")
    num = 4
    if len(queue) < 4:
        num = len(queue)
    queuestr = "Next %s of %s tracks:\n" % (num, len(queue))
    for track in queue[ : num]:
        track = track.replace("file: ", "")
        queuestr += self.run_func("format_song_details", [track])+"\n"
    self.conman.privmsg(queuestr)

#Maps command and help text for command
self._map("command", "queue", queue)
self._map("help", "queue", ".queue [song id] - displays the next 4 queued songs, optionally starting from a particular song number")
