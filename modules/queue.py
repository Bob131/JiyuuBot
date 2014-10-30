#Module to display queue of songs from MPD
def queue(self, msginfo):
    queue = self.conman.mpc.playlist()
    self.require("format_song_details")
    command = msginfo["msg"].split(" ")[1:]
    if command == []:
        command = "1"
    else:
        command = command[0]
    try:
        if not command == "":
            if int(command) <= 0 or int(command) == len(queue):
                raise Exception
            queue = queue[int(command):]
    except:
        if len(queue) == 1:
            pass
        else:
            raise Exception("Invalid song id")
    num = 4
    if len(queue) < 4:
        num = len(queue)
    queuestr = "Next %s of %s tracks:\n" % (num, len(queue))
    for track in queue[:num]:
        track = track.replace("file: ", "")
        queuestr += self.funcs["format_song_details"](self, track)+"\n"
    for line in queuestr.split("\n"):
        self.conman.gen_send(line, msginfo)

#Maps command and help text for command
self.commandlist["queue"] = {
        "type": MAPTYPE_COMMAND,
        "function": queue,
        "help": "displays the next 4 queued songs, optionally starting from a particular song number"
        }
