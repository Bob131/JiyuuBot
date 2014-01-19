def git(self, message):
    import requests
    matches = re.findall("github.com/([\w/-]+[^\s])", message)
    for match in matches:
        match = match.split("/")
        if match[-1] == "":
            del match[-1]
        if len(match) == 1:
            self.conman.gen_send("Github: %s" % match[0])
        elif len(match) == 2:
            req = requests.get("https://api.github.com/repos/%s/%s" % tuple(match)).json()
            tosend = "Github: %s - %s - by %s - Last push: %s" % (match[1], req["description"], match[0], req["pushed_at"].split("T")[0])
            if not req["homepage"] == None and not req["homepage"] == "":
                tosend += " - %s" % req["homepage"]
            self.conman.gen_send(tosend)
        elif match[2] == "issues" or match[2] == "pull":
            match[2] = "issues"
            if len(match) == 4:
                req = requests.get("https://api.github.com/repos/%s/%s/%s/%s" % tuple(match)).json()
                self.conman.gen_send("Github: %s/%s#%s - %s - by %s" % (match[0], match[1], req["number"], req["title"], req["user"]["login"]))
            else:
                req = requests.get("https://api.github.com/repos/%s/%s/%s" % tuple(match)).json() 
                numofiss = len(req)
                self.conman.gen_send("Github: %s - by %s - Open issues: %s" % (match[1], match[0], numofiss))
        elif match[2] == "tree":
            branch = match[3]
            filepath = "/".join(match[4:])
            self.conman.gen_send("Github: %s on branch %s - %s - by %s" % (filepath, branch, match[1], match[0]))

self._map("regex", ".*https?://(www\.)?github.com/.*", git)
