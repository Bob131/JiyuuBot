@self.command(help="Pull new commits from configured origin", perm=999)
def pull(self, msginfo):
    import subprocess
    output = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in output.stdout:
        self.conman.gen_send("***Git output: %s" % line.decode("UTF-8").replace("\n", ""), msginfo)
    for line in output.stderr:
        self.conman.gen_send("***Git error: %s" % line.decode("UTF-8").replace("\n", ""), msginfo) # replace required to not trigger the privmsg() except
