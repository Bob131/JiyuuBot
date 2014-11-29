def configs(self, msginfo):
    # to be finished
    if msginfo["msg"].startswith(".config reload"):
        self.confman.load()
