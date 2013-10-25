def service_announce(self):
    import time
    while 1:
        self.execute_command("announce")
        time.sleep(900)

self.map_serv(service_announce)
