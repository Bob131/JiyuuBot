def report(self, msginfo):
    self.conman.gen_send("Reporting in! [Python3]", msginfo)

self.commandlist["bots"] = {
        "type": MAPTYPE_COMMAND,
        "function": report
        }
