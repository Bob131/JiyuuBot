import gi
from gi.repository import GObject
gi.require_version('JiyuuBot', '1.0')
from gi.repository import JiyuuBot

import re
import requests
from bs4 import BeautifulSoup


class nyaa(JiyuuBot.PluginsBasePlugin):
    regex = "https?://([\w\.]*)nyaa.se/\?page=view&tid=(\d+)"

    def do_should_exec(self, msg):
        return msg.regex(self.regex, False)

    def do_exec(self, msg):
        for url in re.findall(self.regex, msg.get_text(), re.IGNORECASE):
            lewd, url = url
            request = requests.get("http://{}nyaa.se/?page=view&tid={}".format(lewd, url))
            if request.status_code == 200 and not "does not appear to be in the database" in request.text:
                soup = BeautifulSoup(request.text.encode(request.encoding))
                name = soup.find(class_="viewtorrentname").contents[0]
                size = soup.find_all(class_="vtop")[-1].contents[0]
                # seeders/leachers
                up = soup.find(class_="viewsn").contents[0]
                down = soup.find(class_="viewln").contents[0]
                tosend = "{} - Size: {} - Peers: {}".format(name, size, "↑{}/↓{}".format(up, down))
                msg.send(tosend)
            elif request.status_code == 200:
                msg.send("Error: Torrent ID {} not found".format(url))
            else:
                msg.send("Error fetching {}: {}".format(url, request.status_code.title))
