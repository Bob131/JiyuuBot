def tb(self, msginfo):
    if self.ltb == None:
        self.conman.gen_send("Nothing to dump!", msginfo)
    else:
        for line in self.ltb["exception"].split("\n"):
            self.conman.gen_send(line, msginfo)
        dump = json.dumps(self.ltb["msginfo"], indent=4, separators=(",", ": "))
        for line in dump.split("\n"):
            self.conman.gen_send(line, msginfo)
        self.ltb = None

self.permsman.suggest_cmd_perms("tb", 999)
self.commandlist["dump"] = {
        "type": MAPTYPE_COMMAND,
        "function": tb,
        "help": "Dumps traceback and msginfo struct of last occuring exception"
        }
