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
                self.conman.gen_send("%s - Uploaded by %s - Uploaded %s - %s views - Duration %s" % (jdata["title"].encode('utf-8'), jdata["uploader"].encode('utf-8'), jdata["uploaded"].split("T")[0].encode('utf-8'), jdata["viewCount"], duration.encode('utf-8')))
            except KeyError:
                self.conman.gen_send("%s" % jdata["error"]["message"])

self._map("regex", ".*(youtube\.com|youtu\.be)/(watch\?)?([^\#\?]+).*", youtube, "YouTube")
