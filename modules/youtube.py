@self.regex(".*(youtube\.com|youtu\.be)/(watch\?)?([\w\d]+).*", prefix="YouTube")
def youtube(self, msginfo):
    string = msginfo["msg"]
    stuff = re.findall("youtu.be/([\w\d]+)", string) + re.findall("youtube.com/watch\?v=([\w\d]+)", string)
    if len(stuff) > 0:
        import requests
        for match in stuff:
            if "v=" in match:
                match = re.findall("v=([\w-]+[^&\s])", match)[0]
            try:
                if not self.confman.get("youtube", "apikey") == "":
                    auth = self.confman.get("youtube", "apikey", "")
                else:
                    auth = None
                jdata = requests.get("https://www.googleapis.com/youtube/v3/videos?id=%s&key=%s&part=snippet,contentDetails,statistics,status" % (match, auth)).json()
                import datetime
                import locale
                jdata = jdata["items"][0]
                import isodate
                duration = str(isodate.parse_duration(jdata["contentDetails"]["duration"]))
                self.conman.gen_send("\x02{}\x02 - Uploaded by \x02{}\x02 - {:,} views - Duration {} - Rating \x033✔{:,}\x03/\x034✗{:,}\x03".format(jdata["snippet"]["title"], jdata["snippet"]["channelTitle"], int(jdata["statistics"]["viewCount"]), duration, int(jdata["statistics"]["likeCount"]), int(jdata["statistics"]["dislikeCount"])), msginfo)
            except KeyError as e:
                # if stats unavailable
                if getattr(e, 'args')[0] == "yt$statistics" or getattr(e, 'args')[0] == "yt$rating":
                    self.conman.gen_send("\x02%s\x02 - Uploaded by \x02%s\x02 - Uploaded %s - Duration %s" % (jdata["title"]["$t"], jdata["author"][0]["name"]["$t"], jdata["published"]["$t"].split("T")[0], duration), msginfo)
                else:
                    self.conman.gen_send("%s" % jdata["error"]["message"], msginfo)
            except ValueError:
            	print("Video not found")
