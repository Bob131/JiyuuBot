def hashtag(self, message):
    message = re.findall(".*\#(\w+).*", message)
    for tag in message:
        reg_tags = self.confman.get_value("hash", "REG_TAGS", {})
        tag = tag.lower()
        if tag in reg_tags.keys():
            self.conman.gen_send(reg_tags[tag])

def add_hash(self, command):
    reg_tags = self.confman.get_value("hash", "REG_TAGS", {})
    command = command.split(" ", 1)
    command[0] = command[0].lower()
    if not command[0] in reg_tags.keys():
        reg_tags[command[0]] = command[1]
        self.confman.set_value("hash", "REG_TAGS", reg_tags)
        self.conman.gen_send("#%s now mapped" % command[0])
    else:
        self.conman.gen_send("#%s already mapped" % command[0])

self._map("regex", ".*\#\w+.*", hashtag)
self._map("command", "addhash", add_hash)
self._map("help", "addhash", ".addhash - Adds hastag")
