@self.regex("\.\w+.*")
def remind(self, msginfo):
    comm = msginfo["msg"].split(" ")[0].replace(".", "")
    memos = self.confman.get("remind", "memos", {})
    comm = comm.lower()
    if comm in memos.keys():
        self.conman.gen_send(memos[comm], msginfo)

@self.command(help="Add reminder for command. Syntax: .addrem <.command> <reminder>")
def addrem(self, msginfo):
    memos = self.confman.get("remind", "memos", {})
    command = msginfo["msg"].split(" ")[1:]
    command[0] = command[0].lower().replace(".", "")
    if not command[0] in memos.keys():
        memos[command[0]] = " ".join(command[1:]).strip()
        self.confman.setv("remind", "memos", memos)
        self.conman.gen_send(".%s now mapped" % command[0], msginfo)
    else:
        self.conman.gen_send(".%s already mapped" % command[0], msginfo)

@self.command(help="Remove reminder for command. Syntax: .delrem <.command>", perm=300)
def delrem(self, msginfo):
    memos = self.confman.get("remind", "memos", {})
    command = msginfo["msg"].split(" ")[1].lower().replace(".", "")
    try:
        del memos[command]
        self.confman.setv("remind", "memos", memos)
        self.conman.gen_send(".%s deleted" % command, msginfo)
    except KeyError:
        self.conman.gen_send(".%s does not exist" % command, msginfo)
