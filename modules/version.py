import os
import datetime
import time
import math
from . import send, functions, regex_handler

@functions
def version():
    gitlogf = open(os.getcwd() + os.sep + ".git/logs/refs/remotes/origin/master", "r")
    gitlog = gitlogf.read()
    gitlogf.close()
    gitlog = gitlog.split("\n")[-2].split(" ")
    commit = gitlog[1][:7]
    timeg = int(gitlog[4])
    vers = "Commit hash: \x02{}\x02".format(commit)
    vers += " - Last updated: {}".format(time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(timeg)))
    vers += " ({} ago)".format(datetime.timedelta(seconds=math.floor(time.time()-timeg)))
    yield "http://github.com/Bob131/JiyuuBot"
    yield vers

@functions.command
def version():
    """.version - print commit hash"""
    for line in functions.version():
        send(line)

@regex_handler("\x01VERSION\x01")
def version():
    for line in functions.version():
        send("\x01{}\x01".format(line))
