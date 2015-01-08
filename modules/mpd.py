if self.glob_confman.get("MPD", "ENABLED"):
    if not "mpd" in sys.modules.keys():
        raise ImportError("MPD requested to be enabled but module is not installed")
    else:
        import mpd
        self.conman.mpc = mpd.MPDClient()
        self.conman.mpc.connect(self.glob_confman.get("MPD", "HOST"), self.glob_confman.get("MPD", "PORT"))
        self.conman.mpc.songlist = list(song["file"] for song in self.conman.mpc.listall("/") if "file" in song.keys())


        @self.command(help="adds %s random tracks to the queue" % self.confman.get("add_random", "NUMBER_OF_SONGS", 10))
        def random(self, _):
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


        @self.command(help="add tracks to the queue")
        def add(self, msginfo):
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


        @self.command(help="adds an intro track to the queue")
        def announce(self, command):
            import random
            filelist = self.conman.mpc.listall("/%s_intros" % self.glob_confman.get("IRC", "NICK"))
            filepath = filelist[random.randint(0, len(filelist)-1)]
            self.conman.mpc.addid(filepath, 1)


        @self.command(help="displays current track info")
        def current(self, msginfo):
            import datetime
            self.require("formatdetails")
            currentTrack = self.conman.mpc.currentsong()
            if type(currentTrack) == list:
                currentTrack = currentTrack[0]
            tosend = self.format_song_details(currentTrack["file"])
            status = self.conman.mpc.status()
            elapsed = str(datetime.timedelta(seconds=int(status["time"][:status["time"].index(":")])))
            while (elapsed.startswith("0") or elapsed.startswith(":")) and len(elapsed) > 4:
                elapsed = elapsed[1:]
            tosend = tosend[:tosend.rindex("-")+2] + elapsed + "/" + tosend[tosend.rindex("-")+2:]
            self.conman.gen_send(tosend, msginfo)


        @self.function
        def format_song_details(self, uri):
            info = self.conman.mpc.listallinfo(uri)[0]
            infodict = {"time": "N/A", "title": uri, "artist": "N/A", "album": "N/A"}
            for key in infodict.keys():
                try:
                    if key == "time":
                        import datetime
                        infodict["time"] = str(datetime.timedelta(seconds=int(info["time"])))
                        while (infodict["time"].startswith("0") or infodict["time"].startswith(":")) and len(infodict["time"]) > 4:
                            infodict["time"] = infodict["time"][1:]
                    else:
                        infodict[key] = info[key]
                except:
                    pass
            parse = "%s - %s - %s - %s" % (infodict["artist"], infodict["album"], infodict["title"], infodict["time"])
            return parse


        @self.command(help="skips currently playing track")
        def next(self, command):
            self.conman.mpc.next()


        @self.command(help="starts playing. Useful for if the queue empties and the stream dies")
        def play(self, command):
            self.conman.mpc.play()


        @self.command(help="displays the next 4 queued songs, optionally starting from a particular song number")
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
                queuestr += self.format_song_details(track)+"\n"
            for line in queuestr.split("\n"):
                self.conman.gen_send(line, msginfo)


        @self.command(help="prints MPD statistics")
        def stats(self, msginfo):
            statsdict = self.conman.mpc.stats()
            import datetime
            self.conman.gen_send("Uptime: %s - Playtime: %s" % (datetime.timedelta(seconds=int(statsdict["uptime"])), datetime.timedelta(seconds=int(statsdict["playtime"]))), msginfo)
            self.conman.gen_send("Artists: %s - Albums: %s - Songs: %s" % (statsdict["artists"], statsdict["albums"], statsdict["songs"]), msginfo)


        @self.command(help="update MPD database")
        def update(self, command):
            self.conman.mpc.update()


        @self.command(help="adds %s random tracks to the queue" % self.confman.get("add_random", "NUMBER_OF_SONGS", 10))
        def random(self, _):
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
