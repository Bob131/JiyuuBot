def download(self, args):
    import urllib2
    import urllib
    import time
    self.conman.privmsg("Fetching track " + args)
    dl = urllib2.urlopen(args)
    fnameline=""
    for line in str(dl.info()).split("\r\n"):
        if "filename=" in line:
            fnameline = line
            break
    if dl.info().maintype == "audio":
        fname = urllib.url2pathname(args[args.rindex("/") + 1 : ])
        if not fnameline == "":
            fname = fnameline[fnameline.index("filename=") + 10 : fnameline.rindex("\"")].replace("/", " ")
        track = open(os.path.join(os.path.join(MUSIC_PATH, NICK + "_downloaded_music"), fname), "wb")
        track.write(dl.read())
        track.close()
        self.conman.mpc.update()
        time.sleep(5)
        self.conman.mpc.addid(os.path.join(NICK + "_downloaded_music", fname), 2)
        self.conman.privmsg(fname + " fetched and queued")
    else:
        self.conman.privmsg("Mime type " + dl.info().type + " not allowed.")

self.map_command("download", download)
self.map_command("dl", download, False)
self.map_help("download", "< .download | .dl > URL - downloads track and queues for playback")
self.map_help("dl", "< .download | .dl > URL - downloads track and queues for playback")
