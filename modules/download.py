def download(self, msginfo):
    import urllib.request, urllib.error, urllib.parse
    import urllib.request, urllib.parse, urllib.error
    import time
    args = msginfo["msg"].split(" ")[1:]
    for arg in args:
        self.conman.gen_send("Fetching track " + arg, msginfo)
        dl = urllib.request.urlopen(arg)
        fnameline=""
        for line in str(dl.info()).split("\r\n"):
            if "filename=" in line:
                fnameline = line
                break
        if dl.info().maintype == "audio":
            fname = urllib.request.url2pathname(arg[arg.rindex("/") + 1 : ])
            if not fnameline == "":
                fname = fnameline[fnameline.index("filename=") + 10 : fnameline.rindex("\"")].replace("/", " ")
            track = open(os.path.join(os.path.join(MUSIC_PATH, NICK + "_downloaded_music"), fname), "wb")
            track.write(dl.read())
            track.close()
            self.conman.mpc.update()
            time.sleep(5)
            self.conman.mpc.addid(os.path.join(NICK + "_downloaded_music", fname), 2)
            self.conman.gen_send(fname + " fetched and queued", msginfo)
        else:
            self.conman.gen_send("Mime type " + dl.info().type + " not allowed.", msginfo)

self.commandlist["download"] = {
        "type": MAPTYPE_COMMAND,
        "function": download,
        "help": "downloads track and queues for playback"
        }
self.commandlist["dl"] = {
        "type": MAPTYPE_ALIAS,
        "pointer": "download"
        }
