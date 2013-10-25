def play_queue(self, command):
    self.conman.mpc.play()

self.map_command("play", play_queue)
self.map_help("play", ".play - starts playing. Useful for if the queue empties and the stream dies")
