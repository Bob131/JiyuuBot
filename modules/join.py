def who(self, msginfo):
    nick = msginfo["strg"][:msginfo["strg"].index("!")]
    self.conman.gen_send(self.confman.get("join", "greeter", "Hello {}, welcome to {}!").format(nick, msginfo["chan"]), msginfo)


self.commandlist["!JOIN"] = {
        "type": MAPTYPE_OTHER,
        "function": who
        }
