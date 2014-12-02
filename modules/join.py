def who(self, msginfo):
    nick = msginfo["strg"][:msginfo["strg"].index("!")]
    chan = re.findall("(#[^\s,]+)", msginfo["strg"])[0]
    self.conman.privmsg(self.confman.get("join", "greeter", "Hello {}, welcome to {}!").format(nick, chan), chan)


self.commandlist["!JOIN"] = {
        "type": MAPTYPE_OTHER,
        "function": who
        }
