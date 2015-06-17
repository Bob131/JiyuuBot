import re
import requests
from . import regex_handler, send

@regex_handler(".*https*://boards.4chan.org/\w+/(res|thread)/[\d\w]+.*")
def chan(msginfo):
    matches = re.findall("boards.4chan.org/(\w+)/(?:res|thread)/([\d\#p]+)", msginfo["msg"])
    for match in matches:
        try:
            info = requests.get("https://a.4cdn.org/%s/res/%s.json" % (match[0], match[1].split("#")[0])).json()
        except ValueError:
            break
        match = match[1].split("#p")[-1]
        print("entered")
        thread = {}
        for post in info["posts"]:
            if post["no"] == int(match):
                thread = post
                break
        if not thread == {}:
            resp = "\x02>>{}\x02 - by \x02{}\x02 - posted at {}".format(thread["no"], thread["name"], thread["now"].replace("\\", ""))
            if not thread["resto"] == 0:
                resp += " - reply to " + thread["resto"]
            send(resp)
        else:
            send("Post id not found")
