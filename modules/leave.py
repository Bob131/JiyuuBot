def leave(self, cmd):
    info = thread_types[threading.current_thread().ident] 
    if self.permsman.get_msg_perms(info["nick"]):
        cmd = list(x for x in cmd.strip().split(" ") if not x == "")
        if len(cmd) == 0:
            self.conman.leave_irc(info["source"], info["nick"])
        else:
            self.conman.leave_irc(cmd[0], info["nick"])
    else:
        self.conman.gen_send("Not permitted to part")

self._map("command", "leave", leave)
