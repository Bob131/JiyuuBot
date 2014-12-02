def configs(self, msginfo):
    # to be finished
    if msginfo["msg"].startswith(".config reload"):
        self.confman.load()
        self.glob_confman.load()


self.commandlist["config"] = {
        "type": MAPTYPE_COMMAND,
        "function": configs
        }
