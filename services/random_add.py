def service_wait(self):
    import time
    while 1:
        time.sleep(30)
        if len(self.conman.mpc.playlist()) < 5:
            self.execute_command("random")

self.map_serv(service_wait)
