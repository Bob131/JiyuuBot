def post(self, message):
    import requests
    matches = re.findall("boards.4chan.org/(\w+)/res/([\d\#p]+)", message)
    for match in matches:
        try:
            info = requests.get("https://a.4cdn.org/%s/res/%s.json" % (match[0], match[1].split("#")[0])).json()
        except ValueError:
            break
        match = match[1].split("#p")[-1]
        thread = {}
        for post in info["posts"]:
            if post["no"] == int(match):
                thread = post
                break
        if not thread == {}:
            self.conman.gen_send("\x02>>%s\x02 - by \x02%s\x02 - posted at %s%s" % (thread["no"], thread["name"], thread["now"].replace("\\", ""), ("" if thread["resto"] == 0 else " - reply to %s" % thread["resto"])))
        else:
            self.conman.gen_send("Post id not found")

self._map("regex", ".*https*://boards.4chan.org/\w+/res/[\d\w]+.*", post, "4chan")
