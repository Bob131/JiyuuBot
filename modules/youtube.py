def youtube(self, msginfo):
    string = msginfo["msg"]
    stuff = re.findall("youtu.be/([^\#\?\s]+)", string) + re.findall("youtube.com/watch\?([^\#\?\s]+)", string)
    if len(stuff) > 0:
        import requests
        for match in stuff:
            if "v=" in match:
                match = re.findall("v=([\w-]+[^&\s])", match)[0]
            try:
                jdata = requests.get("https://gdata.youtube.com/feeds/api/videos/%s?alt=json&v=2" % match).json()
                import datetime
                import locale
                jdata = jdata["entry"]
                duration = str(datetime.timedelta(seconds=int(jdata["media$group"]["yt$duration"]["seconds"])))
                self.conman.gen_send("\x02%s\x02 - Uploaded by \x02%s\x02 - Uploaded %s - %s views - Duration %s - Rating \x033%s\x03/\x034%s\x03" % (jdata["title"]["$t"], jdata["author"][0]["name"]["$t"], jdata["published"]["$t"].split("T")[0], locale.format("%d", int(jdata["yt$statistics"]["viewCount"]), grouping=True), duration, jdata["yt$rating"]["numLikes"], jdata["yt$rating"]["numDislikes"]), msginfo)
            except KeyError as e:
                # if stats unavailable
                if getattr(e, 'args')[0] == "yt$statistics":
                    self.conman.gen_send("\x02%s\x02 - Uploaded by \x02%s\x02 - Uploaded %s - Duration %s" % (jdata["title"]["$t"], jdata["author"][0]["name"]["$t"], jdata["published"]["$t"].split("T")[0], duration), msginfo)
                else:
                    self.conman.gen_send("%s" % jdata["error"]["message"], msginfo)
            except ValueError:
            	print("Video not found")

self.commandlist[".*(youtube\.com|youtu\.be)/(watch\?)?([^\#\?]+).*"] = {
        "type": MAPTYPE_REGEX,
        "function": youtube,
        "prefix": "YouTube"
        }
