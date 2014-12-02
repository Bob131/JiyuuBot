def who(self, msginfo):
    nick = msginfo["strg"][:msginfo["strg"].index("!")]
    chan = re.findall("(#[^\s,]+)", msginfo["strg"])[0]
    self.conman.gen_send(self.confman.get("join", "greeter", "Hello {}, welcome to {}!").format(nick, chan), msginfo)


self.commandlist["!JOIN"] = {
        "type": MAPTYPE_OTHER,
        "function": who
        }
