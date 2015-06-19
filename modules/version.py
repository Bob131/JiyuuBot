import os
import datetime
import time
import math
from . import command, send

@command
def version(msginfo):
    """.version - print commit hash"""
    gitlogf = open(os.getcwd() + os.sep + ".git/logs/refs/remotes/origin/master", "r")
    gitlog = gitlogf.read()
    gitlogf.close()
    gitlog = gitlog.split("\n")[-2].split(" ")
    commit = gitlog[1][:7]
    timeg = int(gitlog[4])
    vers = "Commit hash: \x02{}\x02".format(commit)
    vers += " - Last updated: {}".format(time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(timeg)))
    vers += " ({} ago)".format(datetime.timedelta(seconds=math.floor(time.time()-timeg)))
    send("http://github.com/Bob131/JiyuuBot")
    send(vers)
