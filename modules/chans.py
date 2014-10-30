def chans(self, msginfo):
    tosend = ", ".join(self.conman.joined_chans)
    tosend = "%s channels currently served by %s: %s" % (len(self.conman.joined_chans), self.glob_confman.get("IRC", "NICK"), tosend)
    self.conman.gen_send(tosend, msginfo)

self.commandlist["chans"] = {
        "type": MAPTYPE_COMMAND,
        "function": chans,
        "help": "Displays channels being served"
        }
