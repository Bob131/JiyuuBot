#Module to display queue of songs from MPCD
def queue(self, command):
    queue = self.conman.mpc.playlist()
    if thread_types[threading.current_thread().ident] == "HTTP":
        newlist = []
        for song in queue:
            newlist.append(self.conman.mpc.listallinfo(song[6:])[0])
        self.conman.gen_send(json.dumps(newlist, sort_keys=True, indent=4, separators=(',', ': ')))
    else:
        self.require("format_song_details")
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
        self.conman.gen_send(queuestr)

#Maps command and help text for command
self._map("command", "queue", queue)
self._map("http", "queue", queue)
self._map("help", "queue", ".queue [song id] - displays the next 4 queued songs, optionally starting from a particular song number")
