def nyaa(self, msginfo):
    import requests
    from bs4 import BeautifulSoup
    urls = re.findall("nyaa.se/\\?page=view&tid=(\d+)", msginfo["msg"])
    for url in urls:
        request = requests.get("http://nyaa.se/?page=view&tid={}".format(url))
        if request.status_code == 200 and not "does not appear to be in the database" in request.text:
            soup = BeautifulSoup(request.text)
            name = soup.find(class_="viewtorrentname").contents[0]
            size = soup.find_all(class_="vtop")[-1].contents[0]
            # seeders/leachers
            up = soup.find(class_="viewsn").contents[0]
            down = soup.find(class_="viewln").contents[0]
            tosend = "\x02{}\x02 - Size: {} - Peers: {} - Download: {}".format(name, size, "\x033↑{}/\x034↓{}\x03".format(up, down), "http://nyaa.se/view=download&tid={}".format(url))
            self.conman.gen_send(tosend, msginfo)
        elif request.status_code == 200:
            self.conman.gen_send("Error: Torrent ID \x02{}\x02 not found".format(url), msginfo)
        else:
            self.conman.gen_send("Error fetching {}: {}".format(url, request.status_code.title), msginfo)


self.commandlist[".*nyaa.se/\?page=view\&tid=.*"] = {
        "type": MAPTYPE_REGEX,
        "function": nyaa,
        "prefix": "Nyaa"
        }
