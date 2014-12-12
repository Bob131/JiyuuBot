def add_random(self, _):
    import random
    numsongs = int(self.confman.get("add_random", "NUMBER_OF_SONGS", 10))
    mpdsongs = int(self.conman.mpc.stats()["songs"])
    while numsongs:
        sid = random.randint(0, mpdsongs-1)
        try:
            self.conman.mpc.addid(self.conman.mpc.songlist[sid])
            numsongs-=1
        except mpd.MPDError:
            pass


def add_tracks(self, msginfo):
    arg = msginfo["msg"][msginfo["msg"].index(" ")+1:]
    matches = self.conman.mpc.search("any", arg)
    if len(matches) > 1:
        import random
        self.conman.gen_send("%s results for search \"%s\"; selecting one at random" % (len(matches), arg), msginfo)
        rand = random.randint(0, len(matches)-1)
        self.conman.gen_send("Adding %s" % matches[rand]["file"], msginfo)
        self.conman.mpc.add(matches[rand]["file"])
    elif len(matches) == 0:
        self.conman.gen_send("No songs matching \"%s\"" % arg, msginfo)
    else:
        self.conman.mpc.add(matches[0]["file"])


def announce(self, command):
    import random
    filelist = self.conman.mpc.listall("/%s_intros" % self.glob_confman.get("IRC", "NICK"))
    filepath = filelist[random.randint(0, len(filelist)-1)]
    self.conman.mpc.addid(filepath, 1)


def current(self, msginfo):
    import datetime
    self.require("formatdetails")
    currentTrack = self.conman.mpc.currentsong()
    if type(currentTrack) == list:
        currentTrack = currentTrack[0]
    tosend = self.funcs["format_song_details"](self, currentTrack["file"])
    status = self.conman.mpc.status()
    elapsed = str(datetime.timedelta(seconds=int(status["time"][:status["time"].index(":")])))
    while elapsed.startswith("0") or elapsed.startswith(":"):
        elapsed = elapsed[1:]
    tosend = tosend[:tosend.rindex("-")+2] + elapsed + "/" + tosend[tosend.rindex("-")+2:]
    self.conman.gen_send(tosend, msginfo)


def format_song_details(self, uri):
    info = self.conman.mpc.listallinfo(uri)[0]
    infodict = {"time": "N/A", "title": uri, "artist": "N/A", "album": "N/A"}
    for key in infodict.keys():
        try:
            if key == "time":
                import datetime
                infodict["time"] = str(datetime.timedelta(seconds=int(info["time"])))
                while infodict["time"].startswith("0") or infodict["time"].startswith(":"):
                    infodict["time"] = infodict["time"][1:]
            else:
                infodict[key] = info[key]
        except:
            pass
    parse = "%s - %s - %s - %s" % (infodict["artist"], infodict["album"], infodict["title"], infodict["time"])
    return parse


def next_track(self, command):
    self.conman.mpc.next()


def play_queue(self, command):
    self.conman.mpc.play()


def queue(self, msginfo):
    queue = self.conman.mpc.playlist()
    self.require("formatdetails")
    command = msginfo["msg"].split(" ")[1:]
    if command == []:
        command = int(self.conman.mpc.currentsong()["pos"]) + 2
    else:
        command = command[0]
    try:
        if not command == "":
            if int(command) <= 0 or int(command) == len(queue):
                raise Exception
            queue = queue[int(command)-1:]
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


def stats(self, msginfo):
    statsdict = self.conman.mpc.stats()
    import datetime
    self.conman.gen_send("Uptime: %s - Playtime: %s" % (datetime.timedelta(seconds=int(statsdict["uptime"])), datetime.timedelta(seconds=int(statsdict["playtime"]))), msginfo)
    self.conman.gen_send("Artists: %s - Albums: %s - Songs: %s" % (statsdict["artists"], statsdict["albums"], statsdict["songs"]), msginfo)


def update(self, command):
    self.conman.mpc.update()


def add_random(self, _):
    import random
    numsongs = int(self.confman.get("add_random", "NUMBER_OF_SONGS", 10))
    mpdsongs = int(self.conman.mpc.stats()["songs"])
    while numsongs:
        sid = random.randint(0, mpdsongs-1)
        try:
            self.conman.mpc.addid(self.conman.mpc.songlist[sid])
            numsongs-=1
        except mpd.MPDError:
            pass




if self.glob_confman.get("MPD", "ENABLED"):
    if not "mpd" in sys.modules.keys():
        raise ImportError("MPD requested to be enabled but module is not installed")
    else:
        import mpd
        self.conman.mpc = mpd.MPDClient()
        self.conman.mpc.connect(self.glob_confman.get("MPD", "HOST"), self.glob_confman.get("MPD", "PORT"))
        self.conman.mpc.songlist = list(song["file"] for song in self.conman.mpc.listall("/") if "file" in song.keys())
        self.commandlist["random"] = {
                "type": MAPTYPE_COMMAND,
                "function": add_random,
                "help": "adds %s random tracks to the queue" % self.confman.get("add_random", "NUMBER_OF_SONGS", 10)
                }
        self.commandlist["add"] = {
                "type": MAPTYPE_COMMAND,
                "function": add_tracks,
                "help": "adds tracks to the queue"
                }
        self.commandlist["announce"] = {
                "type": MAPTYPE_COMMAND,
                "function": announce,
                "help": "adds an intro track to the queue"
                }
        self.commandlist["current"] = {
                "type": MAPTYPE_COMMAND,
                "function": current,
                "help": "displays current track info"
                }
        self.funcs["format_song_details"] = format_song_details
        self.commandlist["next"] = {
                "type": MAPTYPE_COMMAND,
                "function": next_track,
                "help": "skips currently playing track"
                }
        self.commandlist["play"] = {
                "type": MAPTYPE_COMMAND,
                "function": play_queue,
                "help": "starts playing. Useful for if the queue empties and the stream dies"
                }
        self.commandlist["queue"] = {
                "type": MAPTYPE_COMMAND,
                "function": queue,
                "help": "displays the next 4 queued songs, optionally starting from a particular song number"
                }
        self.commandlist["stats"] = {
                "type": MAPTYPE_COMMAND,
                "function": stats,
                "help": "prints MPD statistics"
                }
        self.commandlist["update"] = {
                "type": MAPTYPE_COMMAND,
                "function": update,
                "help": "Update MPD database"
                }
        self.commandlist["random"] = {
                "type": MAPTYPE_COMMAND,
                "function": add_random,
                "help": "adds %s random tracks to the queue" % self.confman.get("add_random", "NUMBER_OF_SONGS", 10)
                }
