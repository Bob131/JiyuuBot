import socket
import mpd
import ssl
import os
import Queue
import threading
import time

#Load config file from config.py
exec(open(os.path.join(os.path.dirname(__file__), "configs" + os.sep + "config.py"), "r").read())

#Define connection class
class ConnectionMan:
    def __init__(self):
	#connect to mpd server
        self.mpc = mpd.MPDClient()
        self.mpc.connect(MPD_HOST, MPD_PORT)

        # Could impose a limit, but not doing it yet
        self.queue = Queue.Queue()

        self.connect_irc()

    # Trifecta of evil. Do with these as you please, but try not to break the functionality.
    def queue_raw(self, text):
        self.queue.put(str(text) + "\r\n", True)
    
    # You may bypass the queue, if needed.
    def send_raw(self, text):
        lock.acquire()
        self.s.send(str(text))
        lock.release()

    def queue_tick(self):
        while True:
            self.send_raw(self.queue.get(True))
            time.sleep(OUTGOING_DELAY / 1000.0)

    
    def connect_irc(self):
	#If SSL is enabled use ssl
        if(SSL):
            self.s = ssl.wrap_socket(socket.socket( ))
        else:
            self.s = socket.socket( )

        self.s.connect((HOST, PORT))
        
        self.lock = threading.Lock()

        thread = threading.Thread(target = self.queue_tick)
        thread.daemon = True
        thread.start()

        # As of RFC 2812, USER message params are: <user> <mode> <unused> <realname>
        self.queue_raw("USER " + NICK + " 0 * :" + NICK)
        self.queue_raw("NICK " + NICK)

        print "*** Connecting... ***"

        while 1:
            line = self.s.recv(2048)
            line = line.strip("\r\n")
            if("End of /MOTD command." in line):
	        break
            else:
	        print line

        self.queue_raw("JOIN " + HOME_CHANNEL)

        while 1:
            line = self.s.recv(2048)
            line = line.strip("\r\n")
            if("End of /NAMES list." in line):
	        print "\n*** Connected! ***\n"
	        break
            else:
	        print line

	time.sleep(1) # allows chan join to complete before messages are sent

	#Define reconnect function
    def reconnect_mpd(self):
        try:
            self.mpc.disconnect()
        except mpd.ConnectionError:
            pass
        self.mpc.connect(MPD_HOST, MPD_PORT)

    def reconnect_irc(self):
        try:
            self.s.close()
        except:
            pass
        self.s = None
        self.connect_irc()

    #Define private message function
    # Splitting is something that should be taken care of beforehand.
    def privmsg(self, text):
        for msg in str(text).split("\n"):
            self.queue_raw("PRIVMSG " + HOME_CHANNEL + " :" + str(msg))

