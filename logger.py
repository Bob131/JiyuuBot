import os
import sys
import time
import sys

class stdoutLog(object):
    def __init__(self):
        self.logpath = os.path.join(os.path.dirname(__file__), "logs", time.strftime("%Y-%m-%d_%H-%M-%S.log", time.localtime()))
        if not os.path.exists(os.path.dirname(self.logpath)):
            os.mkdir(os.path.dirname(self.logpath))
        self.stdout = sys.stdout
        self.log = open(self.logpath, "w")

    def write(self, out):
        self.stdout.write(out)
        self.log.write(out)
        self.log.flush()

    def flush(self):
        self.log.flush()
