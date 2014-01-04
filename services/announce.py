def announce(self):
    import time
    waittime = int(self.confman.get_value("announce", "ANNOUNCE_INTERVAL", 900))
    while 1:
        self.plugman.execute_command("announce", "PRIVMSG")
        time.sleep(waittime)

self.map_service(announce)
