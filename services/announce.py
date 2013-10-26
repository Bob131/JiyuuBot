def announce(self):
    import time
    while 1:
        self.plugman.execute_command("announce")
        time.sleep(900)

self.map_service(announce)
