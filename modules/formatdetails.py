def format_song_details(self, uri):
    uri = uri[0]
    info = self.conman.mpc.listallinfo(uri)[0]
    infodict = {"time": "N/A", "title": uri, "artist": "N/A", "album": "N/A"}
    for key in infodict.keys():
        try:
            if key == "time":
                import datetime
                infodict["time"] = datetime.timedelta(seconds=int(info["time"]))
            else:
                infodict[key] = info[key]
        except:
            pass
    parse = infodict["artist"] + " - " + infodict["album"] + " - " + infodict["title"] + " - " + infodict["time"]
    return parse

self.reg_func("format_song_details", format_song_details)
