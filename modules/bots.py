@self.command(help="get a list of bots in the current chan")
def bots(self, msginfo):
    self.conman.gen_send("Reporting in! [Python3]", msginfo)
