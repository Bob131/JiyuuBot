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

self.funcs["format_song_details"] = format_song_details
