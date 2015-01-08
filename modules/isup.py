@self.command(help="Check whether a website is up. Syntax: .isup <domain>")
def isup(self, msginfo):
    domains = msginfo["msg"].split(" ")[1:]
    if len(domains) == 0:
        self.conman.gen_send("Error: not enough arguments", msginfo)
        msginfo["msg"] = ".help isup"
        self.commandlist["help"]["function"](self, msginfo)
    else:
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
