@self.command(help="broadcast message on every channel this bot serves", perm=900)
def broadcast(self, msginfo):
    arg = msginfo["msg"][msginfo["msg"].index(" ")+1:]
    self.conman.broadcast(arg)
