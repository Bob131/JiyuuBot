def isup(self, domain):
    import requests
    domain = domain.replace("http://", "").split("/")[0]
    info = requests.get("http://isitup.org/%s.json" % domain).json()
    if info["status_code"] == 1:
        self.conman.gen_send("%s (%s) is up - %sms" % (info["domain"], info["response_ip"], str(float(info["response_time"]) * 1000).split(".")[0]))
    elif info["status_code"] == 2:
        self.conman.gen_send("%s (%s) is down" % (info["domain"], info["response_ip"]))
    elif info["status_code"] == 3:
        self.conman.gen_send("%s doesn't appear to exist" % info["domain"])

self._map("command", "isup", isup)
self._map("help", "isup", ".isup <domain> - Check whether website is up")
