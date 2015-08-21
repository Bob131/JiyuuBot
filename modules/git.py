import re
import requests
from . import functions, send, config

@functions
def git_get_name(userdict):
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
            return functions.git_get_name(req)
        else:
            return userdict["login"]

@functions
def git_allowed(req):
    if req.get("message") and (req['message'].startswith("API rate limit exceeded") or req['message'].startswith("Bad")):
        print(req['message'])
        return False
    else:
        return True

@functions.http_link_handler(".*https?://(www\.)?github.com/.+")
def github(msginfo):
    matches = re.findall("github.com/(.+[^\s#?])", msginfo["msg"])

    for match in matches:
        match = match.split(" ")[0]
        match = match.split("/")
        # remove last list element in case of trailing slash
        if match[-1] == "":
            del match[-1]
        headers = {'User-Agent': 'JiyuuBot'}
        if config().get("oauth"):
            auth = (config()["OAUTH"], "x-oauth-basic")
        else:
            auth = None
        # if github link to user profile
        if len(match) == 1:
            req = requests.get("https://api.github.com/users/" + match[0], headers=headers, auth=auth).json()
            if not "message" in req.keys():
                send(functions.git_get_name(req) + " on Github")

        # if github link to repo
        elif len(match) == 2:
            match[1] = match[1].replace(".git", "")
            req = requests.get("https://api.github.com/repos/{}/{}".format(*tuple(match)), headers=headers, auth=auth).json()
            if functions.git_allowed(req) and not req.get('message') == "Not Found":
                tosend = "\x02{}\x02".format(match[1])
                if req.get("description"):
                    tosend +=  " - \x02{}\x02".format(req["description"])
                tosend += " - by \x02{}\x02".format(functions.git_get_name(req["owner"]))
                tosend += " - Last push: {}".format(req["pushed_at"].split("T")[0])
                if req["has_issues"] and req["open_issues_count"] > 0:
                    tosend += " - Open issues: {}".format(req["open_issues_count"])
                if req["homepage"]:
                    tosend += " - {}".format(req["homepage"])
                if req["fork"]:
                    tosend += " - Forked from {} ({})".format(req["parent"]["full_name"], req["parent"]["html_url"])
                send(tosend)

        # if github link to issue
        elif match[2] == "issues" or match[2] == "pull":
            match[2] = "issues"
            # if issue number provided
            if len(match) == 4:
                req = requests.get("https://api.github.com/repos/{}/{}/{}/{}".format(*tuple(match)), headers=headers, auth=auth).json()
                if functions.git_allowed(req):
                    tosend = "\x02{}\x02".format(req["title"])
                    tosend += " - by \x02{}\x02".format(functions.git_get_name(req["user"]))
                    tosend += " - Last response: {}".format(req["updated_at"].split("T")[0])
                    tosend += " - State: {}".format(req["state"].capitalize())
                    if len(req["labels"]) > 0:
                        tosend += " - Tags: "
                        tosend += ", ".join("\x02{}\x02".format(label["name"]) for label in req["labels"])
                    send(tosend)

        # if github link to commit
        elif match[2] == "commit":
            req = requests.get("https://api.github.com/repos/{}/{}/git/{}s/{}".format(*tuple(match)), headers=headers, auth=auth).json()
            if functions.git_allowed(req):
                tosend = "\x02{}\x02".format(req["message"])
                tosend += " - by \x02{}\x02".format(req["author"]["name"])
                tosend += " - {}".format(req["committer"]["date"].split("T")[0])
                send(tosend)
