import os
import sys
import time
import sys

class stdoutLog(object):
    def __init__(self, logToFile):
        if logToFile:
            self.logpath = os.path.join(os.path.dirname(__file__), "logs", time.strftime("%Y-%m-%d_%H-%M-%S.log", time.localtime()))
            if not os.path.exists(os.path.dirname(self.logpath)):
                os.mkdir(os.path.dirname(self.logpath))
            self.log = open(self.logpath, "w")
        else:
            sys.stdout.write("WARNING: File logging is disabled\n")
            self.log = None
        self.stdout = sys.stdout

    def write(self, out):
        self.stdout.write(out)
        if self.log:
            self.log.write(out)
            self.log.flush()

    def flush(self):
        if self.log:
            self.log.flush()
