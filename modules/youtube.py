def youtube(self, string):
    stuff = re.findall("youtu.be/([^\#\?\s]+)", string) + re.findall("youtube.com/watch\?([^\#\?\s]+)", string)
    if len(stuff) > 0:
        import requests
        for match in stuff:
            if "v=" in match:
                match = re.findall("v=([\w-]+[^&\s])", match)[0]
            jdata = requests.get("https://gdata.youtube.com/feeds/api/videos/%s?alt=jsonc&v=2" % match).json()
            try:
                import datetime
                jdata = jdata["data"]
                duration = str(datetime.timedelta(seconds=jdata["duration"]))
                self.conman.gen_send("\x02%s\x02 - Uploaded by \x02%s\x02 - Uploaded %s - %s views - Duration %s" % (jdata["title"], jdata["uploader"], jdata["uploaded"].split("T")[0], jdata["viewCount"], duration))
            except KeyError:
                self.conman.gen_send("%s" % jdata["error"]["message"])

self._map("regex", ".*(youtube\.com|youtu\.be)/(watch\?)?([^\#\?]+).*", youtube, "YouTube")
