def isup(self, msginfo):
    domains = msginfo["msg"].split(" ")[1:]
    import requests
    for domain in domains:
        domain = re.sub(".*://", "", domain)
        domain = domain.split("/")[0]
        info = requests.get("http://isitup.org/%s.json" % domain).json()
        if info["status_code"] == 1:
            self.conman.gen_send("%s (%s) is up - %sms" % (info["domain"], info["response_ip"], str(float(info["response_time"]) * 1000).split(".")[0]), msginfo)
        elif info["status_code"] == 2:
            self.conman.gen_send("%s (%s) is down" % (info["domain"], info["response_ip"]), msginfo)
        elif info["status_code"] == 3:
            self.conman.gen_send("%s doesn't appear to exist" % info["domain"], msginfo)

self.commandlist["isup"] = {
        "type": MAPTYPE_COMMAND,
        "function": isup,
        "help": "Check whether website is up"
        }
