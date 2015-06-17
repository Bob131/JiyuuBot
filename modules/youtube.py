import re
import datetime
import locale
import isodate
import requests
from . import regex_handler, config, send

@regex_handler(".*(youtube\.com|youtu\.be)/(watch\?)?([\w\d-]+).*")
def youtube(msginfo):
    string = msginfo["msg"]
    stuff = re.findall("youtu.be/([\w-]+[^&\s])", string) + re.findall("youtube.com/watch\?v=([\w\d-]+)", string)
    for match in stuff:
        if "v=" in match:
            match = re.findall("v=([\w-]+[^&\s])", match)[0]
        if ".be\/" in match:
            match = re.findall(".be\/([\w-]+[^&\s])")[0]
        try:
            auth = config().get("apikey")
            if not auth:
                raise ValueError
            jdata = requests.get("https://www.googleapis.com/youtube/v3/videos?id=%s&key=%s&part=snippet,contentDetails,statistics,status" % (match, auth)).json()
            jdata = jdata["items"][0]
            duration = str(isodate.parse_duration(jdata["contentDetails"]["duration"]))
            send("\x02{}\x02 - Uploaded by \x02{}\x02 - {:,} views - Duration {} - Rating \x033✔{:,}\x03/\x034✗{:,}\x03".format(jdata["snippet"]["title"], jdata["snippet"]["channelTitle"], int(jdata["statistics"]["viewCount"]), duration, int(jdata["statistics"]["likeCount"]), int(jdata["statistics"]["dislikeCount"])))
        except KeyError as e:
            # if stats unavailable
            if getattr(e, 'args')[0] == "yt$statistics" or getattr(e, 'args')[0] == "yt$rating":
                send("\x02%s\x02 - Uploaded by \x02%s\x02 - Uploaded %s - Duration %s" % (jdata["title"]["$t"], jdata["author"][0]["name"]["$t"], jdata["published"]["$t"].split("T")[0], duration))
            else:
                send("%s" % jdata["error"]["message"])
        except ValueError:
            pass
