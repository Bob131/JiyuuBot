def play_queue(self, command):
    self.conman.mpc.play()

self.commandlist["play"] = {
        "type": MAPTYPE_COMMAND,
        "function": play_queue,
        "help": "starts playing. Useful for if the queue empties and the stream dies"
        }
