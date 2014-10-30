#NOTE: designed to work in tandem with https://github.com/Bob131/finna-be-octo-ninja/blob/master/downloadd.py

def download(self, msginfo):
    import time
    import socket
    args = msginfo["msg"].split(" ")[1:]
    for arg in args:
        s = socket.socket()
        self.conman.gen_send("Contacting server...", msginfo)
        tosend = {
                "action": "download",
                "uri": arg,
                "allowed_mimetypes": "^audio/.*"
                }
        s.connect((self.glob_confman.get("MPD", "HOST"), 4411))
        s.send(json.dumps(tosend).encode("UTF-8"))
        recv = json.loads(s.recv(4096).decode("UTF-8"))
        if recv["state"] == "error":
            raise Exception(recv["error"])
        else:
            self.conman.gen_send("REMOTE: Downloading '%s'" % recv["filename"], msginfo)
            recv = json.loads(s.recv(4096).decode("UTF-8"))
            if recv["state"] == "error":
                raise Exception(recv["error"])
            else:
                self.conman.gen_send("REMOTE: Status OK. File '%s' downloaded" % recv["filename"], msginfo)
                s.close()
                self.conman.mpc.update()
                time.sleep(5)
                self.conman.mpc.add(self.conman.mpc.search("file", recv["filename"])[0])
                self.conman.gen_send(recv["filename"] + " queued", msginfo)

self.commandlist["download"] = {
        "type": MAPTYPE_COMMAND,
        "function": download,
        "help": "downloads track and queues for playback"
        }
self.commandlist["dl"] = {
        "type": MAPTYPE_ALIAS,
        "pointer": "download"
        }
