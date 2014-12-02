def remind(self, msginfo):
    comm = msginfo["msg"].split(" ")[0].replace(".", "")
    memos = self.confman.get("remind", "memos", {})
    comm = comm.lower()
    if comm in memos.keys():
        self.conman.gen_send(memos[comm], msginfo)

def add_reminder(self, msginfo):
    memos = self.confman.get("remind", "memos", {})
    command = msginfo["msg"].split(" ")[1:]
    command[0] = command[0].lower().replace(".", "")
    if not command[0] in memos.keys():
        memos[command[0]] = " ".join(command[1:]).strip()
        self.confman.setv("remind", "memos", memos)
        self.conman.gen_send(".%s now mapped" % command[0], msginfo)
    else:
        self.conman.gen_send(".%s already mapped" % command[0], msginfo)

def del_reminder(self, msginfo):
    memos = self.confman.get("remind", "memos", {})
    command = msginfo["msg"].split(" ")[1].lower().replace(".", "")
    try:
        del memos[command]
        self.confman.setv("remind", "memos", memos)
        self.conman.gen_send(".%s deleted" % command, msginfo)
    except KeyError:
        self.conman.gen_send(".%s does not exist" % command, msginfo)

self.commandlist["\.\w+.*"] = {
        "type": MAPTYPE_REGEX,
        "function": remind
        }
self.commandlist["addrem"] = {
        "type": MAPTYPE_COMMAND,
        "function": add_reminder,
        }
self.permsman.suggest_cmd_perms("delrem", 300)
self.commandlist["delrem"] = {
        "type": MAPTYPE_COMMAND,
        "function": del_reminder
        }
