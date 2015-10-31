import gi
from gi.repository import GObject
gi.require_version('JiyuuBot', '1.0')
from gi.repository import JiyuuBot

import re
import requests


class isitup(GObject.Object, JiyuuBot.PluginsBasePlugin):
    def do_activate(self, _):
        pass

    def do_should_exec(self, msg):
        return msg.command('isitup') or msg.command('isup')

    def do_exec(self, msg):
        domains = msg.get_args()
        if len(domains) > 0:
            for domain in domains:
                domain = re.sub(".*://", "", domain)
                domain = domain.split("/")[0]
                info = requests.get("https://isitup.org/{}.json".format(domain)).json()
                if info["status_code"] == 1:
                    msg.send("%s (%s) is up - %sms" % (info["domain"], info["response_ip"], str(float(info["response_time"]) * 1000).split(".")[0]))
                elif info["status_code"] == 2:
                    msg.send("%s (%s) is down" % (info["domain"], info["response_ip"]))
                elif info["status_code"] == 3:
                    msg.send("%s doesn't appear to exist" % info["domain"])
