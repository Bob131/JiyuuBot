def hashtag(self, msginfo):
    message = re.findall(".*\#(\w+).*", msginfo["msg"])
    for tag in message:
        reg_tags = self.confman.get_value("hash", "REG_TAGS", {})
        tag = tag.lower()
        if tag in reg_tags.keys():
            self.conman.gen_send(reg_tags[tag], msginfo)

def add_hash(self, msginfo):
    reg_tags = self.confman.get_value("hash", "REG_TAGS", {})
    command = msginfo["msg"].split(" ")[1:]
    command[0] = command[0].lower().replace("#", "")
    if not command[0] in reg_tags.keys():
        reg_tags[command[0]] = command[1]
        self.confman.set_value("hash", "REG_TAGS", reg_tags)
        self.conman.gen_send("#%s now mapped" % command[0], msginfo)
    else:
        self.conman.gen_send("#%s already mapped" % command[0], msginfo)

def del_hash(self, msginfo):
    reg_tags = self.confman.get_value("hash", "REG_TAGS", {})
    command = msginfo["msg"].strip().lower().replace("#", "")
    try:
        del reg_tags[command]
        self.confman.set_value("hash", "REG_TAGS", reg_tags)
        self.conman.gen_send("#%s deleted" % command, msginfo)
    except KeyError:
        self.conman.gen_send("#%s does not exist" % command. msginfo)

self.commandlist[".*\#\w+.*"] = {
        "type": MAPTYPE_REGEX,
        "function": hashtag
        }
self.commandlist["addhash"] = {
        "type": MAPTYPE_COMMAND,
        "function": add_hash,
        "help": "Adds hastag"
        }
