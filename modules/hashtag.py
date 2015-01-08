@self.regex("[^\.]*\#\w+.*", prefix="")
def hashtag(self, msginfo):
    message = re.findall(".*\#(\w+).*", msginfo["msg"])
    for tag in message:
        reg_tags = self.confman.get("hash", "REG_TAGS", {})
        tag = tag.lower()
        if tag in reg_tags.keys():
            self.conman.gen_send(reg_tags[tag], msginfo)

@self.command(help="Adds hastag. Syntax: .addhash #<hashtag> <string> | See also: .delhash")
def addhash(self, msginfo):
    reg_tags = self.confman.get("hash", "REG_TAGS", {})
    command = msginfo["msg"].split(" ")[1:]
    command[0] = command[0].lower().replace("#", "")
    if not command[0] in reg_tags.keys():
        reg_tags[command[0]] = " ".join(command[1:]).strip()
        self.confman.setv("hash", "REG_TAGS", reg_tags)
        self.conman.gen_send("#%s now mapped" % command[0], msginfo)
    else:
        self.conman.gen_send("#%s already mapped" % command[0], msginfo)

@self.command(help="Deletes previously added hashtag. Syntax: .delhash #<hashtag> | See also: .addhash", perm=300)
def delhash(self, msginfo):
    reg_tags = self.confman.get("hash", "REG_TAGS", {})
    command = msginfo["msg"].split(" ")[1].lower().replace("#", "")
    try:
        del reg_tags[command]
        self.confman.setv("hash", "REG_TAGS", reg_tags)
        self.conman.gen_send("#%s deleted" % command, msginfo)
    except KeyError:
        self.conman.gen_send("#%s does not exist" % command, msginfo)
