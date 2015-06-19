import os
import datetime
import time
import math
from . import command, send

@command
def version(msginfo):
    """.version - print commit hash and time of the last git pull"""
    gitlogf = open(os.getcwd() + os.sep + ".git/logs/refs/remotes/origin/master", "r")
    gitlog = gitlogf.read()
    gitlogf.close()
    gitlog = gitlog.split("\n")[-2].split(" ")
    commit = gitlog[1][:7]
    timeg = int(gitlog[4])
    vers = "http://github.com/Bob131/JiyuuBot - Commit hash: \x02%s\x02 - Last pull: %s (%s ago)" % (commit, time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(timeg)), datetime.timedelta(seconds=math.floor(time.time()-timeg)))
    send(vers)
