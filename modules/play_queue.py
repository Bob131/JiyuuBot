def play_queue(self, command):
    self.conman.mpc.play()

self._map("command", "play", play_queue)
self._map("help", "play", ".play - starts playing. Useful for if the queue empties and the stream dies")
