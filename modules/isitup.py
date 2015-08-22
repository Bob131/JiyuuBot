import re
import requests
from . import send, functions

@functions.command("isup")
def isitup(args):
    """
        .isitup <domain> - test whether a website is up
        Service provided by https://isitup.org
    """
    domains = args[1:]
    if len(domains) > 0:
        for domain in domains:
            domain = re.sub(".*://", "", domain)
            domain = domain.split("/")[0]
            info = requests.get("https://isitup.org/{}.json".format(domain)).json()
            if info["status_code"] == 1:
                send("\x02%s\x02 (%s) is up - %sms" % (info["domain"], info["response_ip"], str(float(info["response_time"]) * 1000).split(".")[0]))
            elif info["status_code"] == 2:
                send("\x02%s\x02 (%s) is down" % (info["domain"], info["response_ip"]))
            elif info["status_code"] == 3:
                send("\x02%s\x02 doesn't appear to exist" % info["domain"])
