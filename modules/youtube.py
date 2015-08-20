import re
import requests
from . import functions, command, regex_handler, config, send

@functions
def youtube_info(id):
    auth = config().get("apikey")
    if not auth:
        return None
    jdata = requests.get("https://www.googleapis.com/youtube/v3/videos?id={}&key={}&part=snippet,contentDetails,statistics,status".format(id, auth)).json()
    try:
        jdata = jdata["items"][0]
    except IndexError:
        return
    duration = jdata["contentDetails"]["duration"][2:].replace("H", "h ").replace("M", "m ").replace("S", "s ").strip()
    info = "\x02{}\x02".format(jdata["snippet"]["title"])
    info += " by \x02{}\x02".format(jdata["snippet"]["channelTitle"])
    info += " ({})".format(duration)
    if int(jdata["statistics"]["viewCount"]) == 1:
        info += " - {:,} view".format(int(jdata["statistics"]["viewCount"]))
    else:
        info += " - {:,} views".format(int(jdata["statistics"]["viewCount"]))
    likes = int(jdata["statistics"]["likeCount"])
    dislikes = int(jdata["statistics"]["dislikeCount"])
    if likes > 0 or dislikes > 0:
        info += " - "
        if likes > 0:
            info += "\x033✔{:,}\x03".format(likes)
        if likes > 0 and dislikes > 0:
            info += "/"
        if dislikes > 0:
            info += "\x034✗{:,}\x03".format(dislikes)
    return info

@regex_handler(".*(youtube\.com|youtu\.be)/(watch\?)?([\w\d-]+).*")
def youtube(msginfo):
    string = msginfo["msg"]
    stuff = re.findall("youtu.be/([\w-]+[^\?&\s])", string) + re.findall("youtube.com/watch\?v=([\w\d-]+)", string)
    for match in stuff:
        if "v=" in match:
            match = re.findall("v=([\w-]+[^&\s])", match)[0]
        if ".be\/" in match:
            match = re.findall(".be\/([\w-]+[^&\s])")[0]
        info = functions.youtube_info(match)
        if info:
            send(info)

@command("yt")
def youtube(msginfo):
    """.youtube <query> - search for a video on YouTube"""
    query = " ".join(msginfo["msg"].split(" ")[1:])
    auth = config().get("apikey")
    if auth and len(query) > 0:
        data = requests.get("https://www.googleapis.com/youtube/v3/search?q={}&key={}&part=snippet".format(query, auth)).json()
        if not len(data["items"]) > 0:
            send("No results for \x02{}\x02".format(query))
        else:
            for result in data["items"]:
                if result["id"]["kind"] == "youtube#video":
                    id = result["id"]["videoId"]
                    send("{} - https://youtu.be/{}".format(functions.youtube_info(id), id))
                    break
