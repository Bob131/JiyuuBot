def youtube(self, string):
    stuff = re.findall("watch\?([^\#\?\s]+)", string)
    if len(stuff) > 0:
        import requests
        for match in stuff:
            match = re.findall("v=([\w-]+[^&\s])", match)[0]
            jdata = requests.get("https://gdata.youtube.com/feeds/api/videos/%s?alt=jsonc&v=2" % match).json()
            try:
                jdata = jdata["data"]
                self.conman.gen_send("Youtube: %s - Uploaded by %s - Uploaded %s - %s views" % (jdata["title"], jdata["uploader"], jdata["uploaded"], jdata["viewCount"]))
            except KeyError:
                self.conman.gen_send("Youtube: %s" % jdata["error"]["message"])

self._map("regex", ".*(youtube\.com|youtu\.be)/watch\?([^\#\?]+).*", youtube)
