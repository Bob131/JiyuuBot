import re
import requests
from bs4 import BeautifulSoup
from . import functions, send

@functions.http_link_handler("https?://([\w\.]*)nyaa.se/\?page=view&tid=(\d+)")
def nyaa(msg, matches):
    for url in matches:
        lewd, url = url
        request = requests.get("http://{}nyaa.se/?page=view&tid={}".format(lewd, url))
        if request.status_code == 200 and not "does not appear to be in the database" in request.text:
            soup = BeautifulSoup(request.text.encode(request.encoding))
            name = soup.find(class_="viewtorrentname").contents[0]
            size = soup.find_all(class_="vtop")[-1].contents[0]
            # seeders/leachers
            up = soup.find(class_="viewsn").contents[0]
            down = soup.find(class_="viewln").contents[0]
            tosend = "\x02{}\x02 - Size: {} - Peers: {}".format(name, size, "\x033↑{}\x03/\x034↓{}\x03".format(up, down))
            send(tosend)
        elif request.status_code == 200:
            send("Error: Torrent ID \x02{}\x02 not found".format(url))
        else:
            send("Error fetching {}: {}".format(url, request.status_code.title))
