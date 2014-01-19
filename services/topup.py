def topup_queue(self):
    import time
    while 1:
        time.sleep(30)
        if len(self.conman.mpc.playlist()) < 5:
            self.plugman.execute_command("random")

self.map_service(topup_queue)
