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
        if userdict["name"] == None or userdict["name"].strip() == "" or userdict["name"] == userdict["login"]:
            return userdict["login"]
        else:
            return strfrmt % (userdict["name"], userdict["login"])
    else:
        # if dict is like an owner block from a non-user request
        if "url" in userdict.keys():
            import requests
            req = requests.get(userdict["url"]).json()
            return self.funcs["git_get_name"](self, req)
        else:
            return userdict["login"]

def git(self, msginfo):
    import requests
    matches = re.findall("github.com/(.+[^\s#?])", msginfo["msg"])

    for match in matches:
        match = match.split("/")
        # remove last list element in case of trailing slash
        if match[-1] == "":
            del match[-1]

        # if github link to user profile
        if len(match) == 1:
            req = requests.get("http://osrc.dfm.io/%s.json" % match[0]).json()
            if not "message" in req.keys():
                self.conman.gen_send("\x02%s\x02 - %s repositories - %s contributions - Favourite language: %s (%s contributions)" % (self.funcs["git_get_name"](self, req, True), len(req["repositories"]), req["usage"]["total"], req["usage"]["languages"][0]["language"], req["usage"]["languages"][0]["count"]), msginfo)
            else:
                req = requests.get("https://api.github.com/users/%s" % match[0]).json()
                if not "message" in req.keys():
                    self.conman.gen_send(self.funcs["git_get_name"](self, req), msginfo)
                else:
                    self.conman.gen_send("User %s doesn't appear to exist" % match[0], msginfo)

        # if github link to repo
        elif len(match) == 2:
            req = requests.get("https://api.github.com/repos/%s/%s" % tuple(match)).json()
            tosend = ""
            try:
                _ = req['message']
            except:
                req['message'] = None
            if not req['message'] == "Not Found":
                try:
                    tosend = "\x02%s\x02 - \x02%s\x02 - by \x02%s\x02 - Created: %s - Last push: %s" % (match[1], req["description"], self.funcs["git_get_name"](self, req["owner"]), req["created_at"].split("T")[0], req["pushed_at"].split("T")[0])
                except KeyError as e:
                    if e.args[0] == "description":
                        tosend = "\x02%s\x02 - by \x02%s\x02 - Created: %s - Last push: %s" % (match[1], self.funcs["git_get_name"](self, req["owner"]), req["created_at"].split("T")[0], req["pushed_at"].split("T")[0])
                    else:
                        raise e
                if req["has_issues"]:
                    tosend += " - Open issues: %s" % req["open_issues_count"]
                if not req["homepage"] == None and not req["homepage"] == "":
                    tosend += " - %s" % req["homepage"]
                if req["fork"]:
                    tosend += " - Forked from %s (%s)" % (req["parent"]["full_name"], req["parent"]["html_url"])
            else:
                tosend = "Repo \x02%s/%s\x02 does not exist" % (match[-2], match[-1])
            self.conman.gen_send(tosend, msginfo)

        # if github link to issue
        elif match[2] == "issues" or match[2] == "pull":
            match[2] = "issues"
            # if issue number provided
            if len(match) == 4:
                req = requests.get("https://api.github.com/repos/%s/%s/%s/%s" % tuple(match)).json()
                self.conman.gen_send("%s/%s#%s - \x02%s\x02 - by \x02%s\x02 - Created: %s - Updated: %s - State: %s%s" % (match[0], match[1], req["number"], req["title"], self.funcs["git_get_name"](self, req["user"]), req["created_at"].split("T")[0], req["updated_at"].split("T")[0], req["state"].capitalize(), (" - Tags: " + ", ".join("\x02%s\x02" % label["name"] for label in req["labels"]) if not len(req["labels"]) == 0 else "")), msginfo)

        # if github link to file
        elif match[2] == "tree" or match[2] == "blob":
            branch = match[3]
            filepath = "/".join(match[4:])
            self.conman.gen_send("%s on branch %s - %s" % (filepath, branch, match[1]), msginfo)

        # if github link to commit
        elif match[2] == "commit":
            req = requests.get("https://api.github.com/repos/%s/%s/git/%ss/%s" % tuple(match)).json()
            self.conman.gen_send("\x02%s\x02 - by \x02%s\x02 - %s" % (req["message"], req["author"]["name"], req["committer"]["date"].split("T")[0]), msginfo)

self.funcs["git_get_name"] = git_get_name
self.commandlist[".*https?://(www\.)?github.com/.*"] = {
        "type": MAPTYPE_REGEX,
        "function": git,
        "prefix": "Github"
        }
