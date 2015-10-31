import gi
from gi.repository import GObject
gi.require_version('JiyuuBot', '1.0')
from gi.repository import JiyuuBot

import re
import requests


class chan(GObject.Object, JiyuuBot.PluginsBasePlugin):
    regex = "https?://boards.4chan.org/(\w+)/(?:res|thread)/([\d]+)/([\w\-\d\#p]+)"

    def do_activate(self, _):
        pass

    def do_should_exec(self, msg):
        return msg.regex(self.regex, False)

    def do_exec(self, msg):
        for match in re.findall(self.regex, msg.get_text(), re.IGNORECASE):
            try:
                info = requests.get("https://a.4cdn.org/%s/res/%s.json" % (match[0], match[1].split("#")[0])).json()
            except ValueError:
                break
            print(match)
            try:
                match = int(match[-1].split("#p")[-1])
            except ValueError:
                match = int(match[1])
            thread = {}
            for post in info["posts"]:
                if post["no"] == match:
                    thread = post
                    break
            if not thread == {}:
                resp = ">>{} - by {} - posted at {}".format(thread["no"], thread["name"], thread["now"].replace("\\", ""))
                if not thread["resto"] == 0:
                    resp += " - reply to {}".format(thread["resto"])
                msg.send(resp)
            else:
                msg.send("Post ID not found")
