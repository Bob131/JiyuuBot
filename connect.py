import socket
import mpd
import ssl
import os

#Load config file from config.py
exec(open(os.path.join(os.path.dirname(__file__), "configs" + os.sep + "config.py"), "r").read())

#Define connection class
class ConnectionMan:
    def __init__(self):
	#connect to mpd server
        self.mpc = mpd.MPDClient()
        self.mpc.connect(MPD_HOST, MPD_PORT)

	#If SSL is enabled use ssl
        if(SSL):
            self.s = ssl.wrap_socket(socket.socket( ))
        else:
            self.s = socket.socket( )
        self.s.connect((HOST, PORT))
        self.s.send("USER " + NICK + " " + NICK + " " + NICK + " :" + NICK + "\n")
        self.s.send("NICK " + NICK + "\r\n")
        self.s.send("JOIN " + HOME_CHANNEL + "\r\n")

        print "*** Connecting... ***"
        while 1:
            line = self.s.recv(2048)
            line = line.strip("\r\n")
            if("End of /NAMES list." in line):
	        print "\n*** Connected! ***\n"
	        break
            else:
	        print line

	#Define private message function
    def privmsg(self, text):
        self.s.send("PRIVMSG " + HOME_CHANNEL + " :\r\n")
        #can only send 5 lines at a time on Rizon before being kicked for flood
        text=str(text)
        for msg in text.split("\n"):
            self.s.send("PRIVMSG " + HOME_CHANNEL + " :" + str(msg) + "\r\n")
	
	#Define reconnect function
    def reconnect_mpd(self):
        try:
            self.mpc.disconnect()
        except mpd.ConnectionError:
            pass
        self.mpc.connect(MPD_HOST, MPD_PORT)
