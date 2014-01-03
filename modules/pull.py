def pull(self, command):
    import subprocess
    output = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in output.stdout:
        self.conman.privmsg("***Git output: %s" % line)
    for line in output.stderr:
        self.conman.privmsg("***Git error: %s" % line)

self._map("command", "pull", pull)
