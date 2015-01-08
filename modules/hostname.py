@self.irc(311)
def get_host(self, msginfo):
    self.glob_confman.setv("IRC", "HOSTNAME", msginfo["strg"].split(" ")[5], temp=True)
