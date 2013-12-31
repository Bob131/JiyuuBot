def version(self, command):
    import datetime
    import time
    import math
    gitlogf = open(os.getcwd() + os.sep + ".git/logs/refs/remotes/origin/master", "r")
    gitlog = gitlogf.read()
    gitlogf.close()
    gitlog = gitlog.split("\n")[-2].split(" ")
    commit = gitlog[1]
    timeg = int(gitlog[4])
    vers = "Commit hash: %s - Last pull: %s (%s ago)" % (commit, time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(timeg)), datetime.timedelta(seconds=math.floor(time.time()-timeg)))
    self.conman.privmsg(vers)

self._map("command", "version", version)
self._map("help", "version", ".version - Prints commit hash and last git pull")
version(self, "")
