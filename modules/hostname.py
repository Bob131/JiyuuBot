def get_host(self, msginfo):
    self.glob_confman.setv("IRC", "HOSTNAME", msginfo["strg"].split(" ")[5], temp=True)


self.commandlist["!311"] = {
        "type": MAPTYPE_OTHER,
        "function": get_host
        }
