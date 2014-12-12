def report(self, msginfo):
    self.conman.gen_send("Reporting in! [Python3]", msginfo)

self.commandlist["bots"] = {
        "type": MAPTYPE_COMMAND,
        "function": report,
        "help": "get a list of bots in the current chan"
        }
