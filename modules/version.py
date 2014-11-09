def version(self, msginfo):
    import datetime
    import time
    import math
    gitlogf = open(os.getcwd() + os.sep + ".git/logs/refs/remotes/origin/master", "r")
    gitlog = gitlogf.read()
    gitlogf.close()
    gitlog = gitlog.split("\n")[-2].split(" ")
    commit = gitlog[1][:7]
    timeg = int(gitlog[4])
    vers = "http://github.com/JiyuuProject/JiyuuBot - Commit hash: %s - Last pull: %s (%s ago)" % (commit, time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(timeg)), datetime.timedelta(seconds=math.floor(time.time()-timeg)))
    self.conman.gen_send(vers, msginfo)

self.commandlist["version"] = {
        "type": MAPTYPE_COMMAND,
        "function": version,
        "help": "Prints commit hash and last git pull"
        }
