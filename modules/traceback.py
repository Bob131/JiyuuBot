@self.command(help="Dumps traceback and msginfo struct of last occuring exception", perm=999)
def tb(self, msginfo):
    if self.ltb == None:
        self.conman.gen_send("Nothing to dump!", msginfo)
    else:
        for line in self.ltb["exception"].split("\n"):
            self.conman.gen_send(line, msginfo)
        self.conman.gen_send("---------------------", msginfo)
        dump = json.dumps(self.ltb["msginfo"], indent=4, separators=(",", ": "))
        for line in dump.split("\n"):
            self.conman.gen_send(line, msginfo)
        self.ltb = None
