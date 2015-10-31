import gi
from gi.repository import GObject
gi.require_version('JiyuuBot', '1.0')
from gi.repository import JiyuuBot

import re
import requests



class youtube_base:
    def youtube_info(self, id):
        auth = self.config.get_value("APIKey")
        if not auth:
            print("Bad credentials")
            return None
        jdata = requests.get("https://www.googleapis.com/youtube/v3/videos?id={}&key={}&part=snippet,contentDetails,statistics,status".format(id, auth)).json()
        try:
            jdata = jdata["items"][0]
        except IndexError:
            return
        duration = jdata["contentDetails"]["duration"][2:].replace("H", "h ").replace("M", "m ").replace("S", "s ").strip()
        info = "_{}_".format(jdata["snippet"]["title"])
        info += " by _{}_".format(jdata["snippet"]["channelTitle"])
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
                info += "✔{:,}".format(likes)
            if likes > 0 and dislikes > 0:
                info += "/"
            if dislikes > 0:
                info += "✗{:,}".format(dislikes)
        return info



class youtube_regex(GObject.Object, JiyuuBot.PluginsBasePlugin, youtube_base):
    config = GObject.Property(type=JiyuuBot.ConfigPluginConfig)

    def do_activate(self, config):
        self.config = config

    def do_should_exec(self, msg):
        return msg.regex('(youtube\.com|youtu\.be)/(watch\?)?([\w\d-]+)', False)

    def do_exec(self, msg):
        string = msg.get_text()
        stuff = re.findall("youtu.be/([\w-]+[^\?&\s])", string) + re.findall("youtube.com/watch\?v=([\w\d-]+)", string)
        for match in stuff:
            if "v=" in match:
                match = re.findall("v=([\w-]+[^&\s])", match)[0]
            if ".be\/" in match:
                match = re.findall(".be\/([\w-]+[^&\s])")[0]
            info = self.youtube_info(match)
            if info:
                msg.send(info)



class youtube_cmd(GObject.Object, JiyuuBot.PluginsBasePlugin, youtube_base):
    config = GObject.Property(type=JiyuuBot.ConfigPluginConfig)

    def do_activate(self, config):
        self.config = config

    def do_should_exec(self, msg):
        return msg.command('yt') or msg.command('youtube')

    def do_exec(self, msg):
        args = msg.get_args()
        query = " ".join(args)
        auth = self.config.get_value("APIKey")
        if auth and len(query) > 0:
            data = requests.get("https://www.googleapis.com/youtube/v3/search?q={}&key={}&part=snippet".format(query, auth)).json()
            if not len(data["items"]) > 0:
                msg.send("No results for {}".format(query))
            else:
                for result in data["items"]:
                    if result["id"]["kind"] == "youtube#video":
                        id = result["id"]["videoId"]
                        msg.send("{} - https://youtu.be/{}".format(self.youtube_info(id), id))
                        break
        elif not auth:
            msg.send("Cannot access Youtube API: Invalid credentials")
