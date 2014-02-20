def weblink(self, message):
    from urllib.request import urlopen
    from urllib.error import URLError
    matches = re.findall("(https*://[\w/\.\#\?%]+)", message)
    for match in matches:
        if len([pattern for pattern in self.regex.keys() if not re.match(pattern, match) == None]) == 1:
            try:
                req = urlopen(match)
            except URLError:
                break
            info = req.info()
            if "html" in info["Content-Type"].split(";")[0]:
                self.conman.gen_send("\x02%s\x02 - %sB" % (re.findall("<title>([^<]*)</title>", req.read().decode("UTF-8"))[0], info["Content-Length"]))
            else:
                self.conman.gen_send("\x02%s\x02 - %sB" % (info["Content-Type"], info["Content-Length"]))

self._map("regex", ".*https*://[\w/\.\#\?%]+.*", weblink, "Url Fetch")
