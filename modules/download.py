def download(self, args):
    import urllib.request, urllib.error, urllib.parse
    import urllib.request, urllib.parse, urllib.error
    import time
    self.conman.gen_send("Fetching track " + args)
    dl = urllib.request.urlopen(args)
    fnameline=""
    for line in str(dl.info()).split("\r\n"):
        if "filename=" in line:
            fnameline = line
            break
    if dl.info().maintype == "audio":
        fname = urllib.request.url2pathname(args[args.rindex("/") + 1 : ])
        if not fnameline == "":
            fname = fnameline[fnameline.index("filename=") + 10 : fnameline.rindex("\"")].replace("/", " ")
        track = open(os.path.join(os.path.join(MUSIC_PATH, NICK + "_downloaded_music"), fname), "wb")
        track.write(dl.read())
        track.close()
        self.conman.mpc.update()
        time.sleep(5)
        self.conman.mpc.addid(os.path.join(NICK + "_downloaded_music", fname), 2)
        self.conman.gen_send(fname + " fetched and queued")
    else:
        self.conman.gen_send("Mime type " + dl.info().type + " not allowed.")

self._map("command", "download", download)
self._map("help", "download", ".download URL - downloads track and queues for playback") # map help first so that the help entry is copied when the command is aliased
self._map("alias", "dl", "download")
