def youtube(self, msginfo):
    string = msginfo["msg"]
    stuff = re.findall("youtu.be/([^\#\?\s]+)", string) + re.findall("youtube.com/watch\?([^\#\?\s]+)", string)
    if len(stuff) > 0:
        import requests
        for match in stuff:
            if "v=" in match:
                match = re.findall("v=([\w-]+[^&\s])", match)[0]
            jdata = requests.get("https://gdata.youtube.com/feeds/api/videos/%s?alt=json&v=2" % match).json()
            try:
                import datetime
                import locale
                jdata = jdata["entry"]
                duration = str(datetime.timedelta(seconds=int(jdata["media$group"]["yt$duration"]["seconds"])))
                self.conman.gen_send("\x02%s\x02 - Uploaded by \x02%s\x02 - Uploaded %s - %s views - Duration %s" % (jdata["title"]["$t"], jdata["author"][0]["name"]["$t"], jdata["published"]["$t"].split("T")[0], locale.format("%d", int(jdata["yt$statistics"]["viewCount"]), grouping=True), duration), msginfo)
            except KeyError:
                self.conman.gen_send("%s" % jdata["error"]["message"], msginfo)

self.commandlist[".*(youtube\.com|youtu\.be)/(watch\?)?([^\#\?]+).*"] = {
        "type": MAPTYPE_REGEX,
        "function": youtube,
        "prefix": "YouTube"
        }
