def pull(self, command):
    import subprocess
    output = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
    self.conman.privmsg(output.stdout)
