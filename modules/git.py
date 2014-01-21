def git_get_name(self, userdict, from_osrc=False):
    # string format to use if both a login and a name are available
    strfrmt = "%s (%s)"

    # process is easy if from the Open Source Report Card
    if from_osrc:
        if not userdict["name"] == userdict["username"]:
            return strfrmt % (userdict["name"], userdict["username"])
        else:
            return userdict["name"]

    # if dict from api.github.com
    if "name" in userdict.keys():
        if userdict["name"] == None or userdict["name"] == userdict["login"]:
            return userdict["login"]
        else:
            return strfrmt % (userdict["name"], userdict["login"])
    else:
        # if dict is like an owner block from a non-user request
        if "url" in userdict.keys():
            import requests
            req = requests.get(userdict["url"]).json()
            return self.run_func("git_get_name", req)
        else:
            return userdict["login"]

def git(self, message):
    import requests
    matches = re.findall("github.com/([\w/-]+[^\s])", message)

    for match in matches:
        match = match.split("/")
        # remove last list element in case of trailing slash
        if match[-1] == "":
            del match[-1]

        # if github link to user profile
        if len(match) == 1:
            req = requests.get("http://osrc.dfm.io/%s.json" % match[0]).json()
            if not "message" in req.keys():
                self.conman.gen_send("Github: %s - %s repositories - %s contributions - Favourite language: %s (%s contributions)" % (self.run_func("git_get_name", req, True), len(req["repositories"]), req["usage"]["total"], req["usage"]["languages"][0]["language"], req["usage"]["languages"][0]["count"]))
            else:
                req = requests.get("https://api.github.com/users/%s" % match[0]).json()
                if not "message" in req.keys():
                    self.conman.gen_send("Github: %s" % self.run_func("git_get_name", req))
                else:
                    self.conman.gen_send("Github: User %s doesn't appear to exist" % match[0])

        # if github link to repo
        elif len(match) == 2:
            req = requests.get("https://api.github.com/repos/%s/%s" % tuple(match)).json()
            tosend = "Github: %s - %s - by %s - Created: %s - Last push: %s" % (match[1], req["description"], self.run_func("git_get_name", req["owner"]), req["created_at"].split("T")[0], req["pushed_at"].split("T")[0])
            if req["has_issues"]:
                tosend += " - Open issues: %s" % req["open_issues_count"]
            if not req["homepage"] == None and not req["homepage"] == "":
                tosend += " - %s" % req["homepage"]
            if req["fork"]:
                tosend += " - Forked from %s (%s)" % (req["parent"]["full_name"], req["parent"]["html_url"])
            self.conman.gen_send(tosend)

        # if github link to issue
        elif match[2] == "issues" or match[2] == "pull":
            match[2] = "issues"
            # if issue number provided
            if len(match) == 4:
                req = requests.get("https://api.github.com/repos/%s/%s/%s/%s" % tuple(match)).json()
                self.conman.gen_send("Github: %s/%s#%s - %s - by %s - Created: %s - Updated: %s" % (match[0], match[1], req["number"], req["title"], self.run_func("git_get_name", req["user"]), req["created_at"].split("T")[0], req["updated_at"].split("T")[0]))

        # if github link to file
        elif match[2] == "tree":
            branch = match[3]
            filepath = "/".join(match[4:])
            self.conman.gen_send("Github: %s on branch %s - %s" % (filepath, branch, match[1]))

        # if github link to commit
        elif match[2] == "commit":
            req = requests.get("https://api.github.com/repos/%s/%s/git/%ss/%s" % tuple(match)).json()
            self.conman.gen_send("Github: %s - by %s - %s" % (req["message"], req["author"]["name"], req["committer"]["date"].split("T")[0]))

self.reg_func("git_get_name", git_get_name)
self._map("regex", ".*https?://(www\.)?github.com/.*", git)
