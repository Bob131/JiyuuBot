def format_song_details(self, uri):
    uri = uri[0]
    info = self.conman.mpc.listallinfo(uri)[0]
    m, s = divmod(int(info["time"]), 60)
    time = "%d:%d" % (m, s)
    try:
        title = info['title']
    except KeyError:
        title = os.path.basename(uri.replace(" - ", " "))
    parse = info['artist'] + " - " + info['album'] + " - " + title + " - " + time
    return parse

self.reg_func("format_song_details", format_song_details)
