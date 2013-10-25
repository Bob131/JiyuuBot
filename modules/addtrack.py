def add_tracks(self, arg):
    self.conman.mpc.searchadd("any", arg)

self.map_command("add", add_tracks)
self.map_help("add", ".add - adds tracks to the queue")
