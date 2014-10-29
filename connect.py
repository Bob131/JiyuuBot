import socket
import ssl
import os
import queue
import threading
import time


#Load config file from config.py
exec(open(os.path.join(os.path.dirname(__file__), "configs" + os.sep + "config.py"), "r").read())


if MPD:
    import mpd


#Define connection class
class ConnectionMan:
    def __init__(self, global_confman):
        self.confman = global_confman

	#connect to mpd server
        if MPD:
            self.mpc = mpd.MPDClient()
            self.mpc.connect(MPD_HOST, MPD_PORT)

        if IRC:
            self.queue = queue.Queue()
            self.connect_irc()


    # message management functions ###
    def queue_raw(self, text):
        self.queue.put(str(text) + "\r\n", True)


    # You may bypass the queue, if needed.
    def send_raw(self, text):
        self.lock.acquire()
        print("%s >>> %s" % (time.strftime("%Y-%m-%d %H:%M", time.localtime()), text.strip()))
        self.s.send(bytes(text, "UTF-8"))
        self.lock.release()


    def queue_tick(self):
        while True:
            self.send_raw(self.queue.get(True))
            time.sleep(OUTGOING_DELAY / 1000.0)
    ##################################


    # function for joining channels
    def join_irc(self, chan, nick=None, record=True):
        self.queue_raw("JOIN " + chan)

        while 1:
            try:
                line = self.s.recv(2048).decode("UTF-8")
            except UnicodeDecodeError:
                continue
            line = line.strip("\r\n")
            if "End of /NAMES list." in line:
                print("\n*** %s joined! ***\n" % chan)
                break
            else:
                print(line)
                
        time.sleep(1) # allows chan join to complete before messages are sent

        if not nick == None:
            self.privmsg("Invited by %s" % nick, chan)
            self.privmsg("Home channel: %s" % HOME_CHANNEL, chan)
            self.privmsg("Joined %s, invited by %s" % (chan, nick), HOME_CHANNEL)
	
        self.joined_chans.append(chan)

        if record:
            self.confman.set_value("IRC", "CHANS", list(chan for chan in self.joined_chans if not chan == HOME_CHANNEL))


    # parting channels
    def leave_irc(self, chan, nick, kicked=False):
        if chan == HOME_CHANNEL and kicked:
            del self.joined_chans[self.joined_chans.index(chan)]
            self.join_irc(HOME_CHANNEL, None, False)
        elif chan == HOME_CHANNEL:
            self.privmsg("Can't be PART'd from home channel")
        else:
            if kicked:
                self.privmsg("Kicked from %s by %s" % (chan, nick))
            else:
                partmsg = ("PART'd from %s by %s" % (chan, nick))
                self.queue_raw("PART %s %s" % (chan, partmsg))
                self.privmsg(partmsg)

            del self.joined_chans[self.joined_chans.index(chan)]
            self.confman.set_value("IRC", "CHANS", list(set(chan for chan in self.joined_chans if not chan == HOME_CHANNEL)))

            print("\n*** %s left! ***\n" % chan)


    # connect to IRC server, join HOME_CHANNEL
    def connect_irc(self):
	#If SSL is enabled use ssl
        if SSL:
            self.s = ssl.wrap_socket(socket.socket())
        else:
            self.s = socket.socket()

        self.s.connect((HOST, PORT))
        self.lock = threading.Lock()
        self.joined_chans = []

        thread = threading.Thread(target = self.queue_tick)
        thread.daemon = True
        thread.start()

        global NICK
        # As of RFC 2812, USER message params are: <user> <mode> <unused> <realname>
        self.queue_raw("USER " + NICK + " 0 * :" + NICK)
        self.queue_raw("NICK " + NICK)

        print("*** Connecting... ***")

        while 1:
            try:
                line = self.s.recv(2048).decode("UTF-8")
            except UnicodeDecodeError:
                continue
            line = line.strip("\r\n")
            if "Nickname is already in use" in line:
                NICK+="_"
                self.queue_raw("NICK " + NICK)
            elif "PING" in line:
                self.queue_raw("PONG :%s" % line[6:])
            elif "End of /MOTD command." in line:
                break
            print(line)

        self.join_irc(chan = HOME_CHANNEL, record = False)
        for channel in self.confman.get_value("IRC", "CHANS", []):
            self.join_irc(chan = channel, record = False)


    # reconnect to MPD
    def reconnect_mpd(self):
        try:
            self.mpc.disconnect()
        except mpd.ConnectionError:
            pass
        self.mpc.connect(MPD_HOST, MPD_PORT)


    # reconnect to IRC
    def reconnect_irc(self):
        try:
            self.s.close()
        except:
            pass
        self.s = None
        self.connect_irc()


    # generic send function
    def gen_send(self, text, msginfo):
        try:
            self.privmsg("%s: %s" % (msginfo["prefix"], text), msginfo["chan"])
        except KeyError:
            self.privmsg(text, msginfo["chan"])


    #Define private message function
    # Splitting is something that should be taken care of beforehand.
    def privmsg(self, text, channel=HOME_CHANNEL):
        if "\n" in text:
            raise Exception("connect.py:privmsg() no longer accepts multi-line messages")
        else:
            if IRC:
                self.queue_raw("PRIVMSG " + channel + " :" + text)
            else:
                print(prefix + text)
