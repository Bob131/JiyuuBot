import gi
from gi.repository import GObject
gi.require_version('JiyuuBot', '1.0')
from gi.repository import JiyuuBot

import re
import requests

class git(JiyuuBot.PluginsBasePlugin):
    regex = "https?://(?:www\.)?github.com/(.+[^\s#?])"
    config = GObject.Property(type=JiyuuBot.ConfigPluginConfig)


    def do_activate(self, _, config):
        self.config = config


    def do_should_exec(self, msg):
        return msg.regex(self.regex, False)


    def git_get_name(self, userdict):
        # string format to use if both a login and a name are available
        strfrmt = "%s (%s)"

        if "public_repos" in userdict.keys():
            if userdict["name"] == None or userdict["name"].strip() == "" or userdict["name"] == userdict["login"]:
                return userdict["login"]
            else:
                return strfrmt % (userdict["name"], userdict["login"])
        else:
            # if dict is like an owner block from a non-user request
            if "url" in userdict.keys():
                req = requests.get(userdict["url"]).json()
                return self.git_get_name(req)
            else:
                return userdict["login"]


    def git_allowed(self, req):
        if req.get("message") and (req['message'].startswith("API rate limit exceeded") or req['message'].startswith("Bad")):
            print(req['message'])
            return False
        else:
            return True


    def do_exec(self, msg):
        for match in re.findall(self.regex, msg.get_text(), re.IGNORECASE):
            match = match.split(" ")[0]
            match = match.split("/")
            # remove last list element in case of trailing slash
            if match[-1] == "":
                del match[-1]
            headers = {'User-Agent': 'JiyuuBot'}
            if self.config.has_key("Oauth"):
                auth = (self.config.get_value("Oauth"), "x-oauth-basic")
            else:
                auth = None

            # if github link to user profile
            if len(match) == 1:
                req = requests.get("https://api.github.com/users/" + match[0], headers=headers, auth=auth).json()
                if not "message" in req.keys():
                    msg.send(self.git_get_name(req) + " on Github")

            # if github link to repo
            elif len(match) == 2:
                match[1] = match[1].replace(".git", "")
                req = requests.get("https://api.github.com/repos/{}/{}".format(*tuple(match)), headers=headers, auth=auth).json()
                if self.git_allowed(req) and not req.get('message') == "Not Found":
                    tosend = "{}".format(match[1])
                    if req.get("description"):
                        tosend +=  " - {}".format(req["description"])
                    tosend += " - by {}".format(self.git_get_name(req["owner"]))
                    tosend += " - Last push: {}".format(req["pushed_at"].split("T")[0])
                    if req["has_issues"] and req["open_issues_count"] > 0:
                        tosend += " - Open issues: {}".format(req["open_issues_count"])
                    if req["homepage"]:
                        tosend += " - {}".format(req["homepage"])
                    if req["fork"]:
                        tosend += " - Forked from {} ({})".format(req["parent"]["full_name"], req["parent"]["html_url"])
                    msg.send(tosend)

            # if github link to issue
            elif match[2] == "issues" or match[2] == "pull":
                match[2] = "issues"
                # if issue number provided
                if len(match) == 4:
                    req = requests.get("https://api.github.com/repos/{}/{}/{}/{}".format(*tuple(match)), headers=headers, auth=auth).json()
                    if self.git_allowed(req):
                        tosend = "{}".format(req["title"])
                        tosend += " - by {}".format(self.git_get_name(req["user"]))
                        tosend += " - Last response: {}".format(req["updated_at"].split("T")[0])
                        tosend += " - State: {}".format(req["state"].capitalize())
                        if len(req["labels"]) > 0:
                            tosend += " - Tags: "
                            tosend += ", ".join("{}".format(label["name"]) for label in req["labels"])
                        msg.send(tosend)

            # if github link to commit
            elif match[2] == "commit":
                req = requests.get("https://api.github.com/repos/{}/{}/git/{}s/{}".format(*tuple(match)), headers=headers, auth=auth).json()
                if self.git_allowed(req):
                    tosend = "{}".format(req["message"])
                    tosend += " - by {}".format(req["author"]["name"])
                    tosend += " - {}".format(req["committer"]["date"].split("T")[0])
                    msg.send(tosend)
