def pull(self, command):
    import subprocess
    output = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in output.stdout:
        self.conman.gen_send("***Git output: %s" % line.decode("UTF-8"))
    for line in output.stderr:
        self.conman.gen_send("***Git error: %s" % line.decode("UTF-8"))

self._map("command", "pull", pull)
