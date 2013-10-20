import socket
import mpd
import ssl
import os
import urllib2
import urllib
import threading
import time
import sys
import random

MPD_HOST = "127.0.0.1"
MPD_PORT = 6600

HOST = "irc.rizon.net"
HOME_CHANNEL = "#JiyuuRadio"
NICK = "JiyuuRadio"
PORT = 9999
SSL = True

MUSIC_PATH = "/media/music/Music"

ANNOUNCE = True
ANNOUNCE_INTERVAL = 900

HELP_DICT = {"add": ".add [search term] - queues tracks for playback", "play": ".play - starts playing (useful for when the stream dies due to lack of queued tracks", "next": ".next - next track", "current": ".current - prints infor about current track", "queue": ".queue - shows next 4 songs", "stats": ".stats - shows stats", "download": "<.download | .dl> [url] - downloads track from URL and queues it", "dl": "<.download | .dl> [url] - downloads track from URL and queues it"}


mpc = mpd.MPDClient()
mpc.connect(MPD_HOST, MPD_PORT)

if(SSL):
    s = ssl.wrap_socket(socket.socket( ))
else:
    s = socket.socket( )
s.connect((HOST, PORT))
s.send("USER " + NICK + " " + NICK + " " + NICK + " :" + NICK + "\n")
s.send("NICK " + NICK + "\r\n")
s.send("JOIN " + HOME_CHANNEL + "\r\n")

if not os.path.exists(os.path.join(MUSIC_PATH, NICK+"_downloaded_music")):
    os.mkdir(os.path.join(MUSIC_PATH, NICK+"_downloaded_music"))



def reconnect_mpd():
    try:
        mpc.disconnect()
    except mpd.ConnectionError:
        pass
    mpc.connect(MPD_HOST, MPD_PORT)


def announce_wait():
    while 1:
        time.sleep(ANNOUNCE_INTERVAL)
        announce()

def announce():
    filelist = os.listdir(os.path.join(MUSIC_PATH, NICK + "_intros"))
    filepath = filelist[random.randint(0, len(filelist)-1)]
    filepath = os.path.join(NICK + "_intros", filepath)
    mpc.addid(filepath, 1)

def cmd_play(command):
    mpc.play()

def cmd_next(command):
    mpc.next()

def cmd_download(command):
    try:
        args = command[command.index(" ") + 1 : ]
        return_output("Fetching track " + args)
        dl = urllib2.urlopen(args)
        fnameline=""
        for line in str(dl.info()).split("\r\n"):
            if "filename=" in line:
                fnameline = line
                break
        if dl.info().maintype == "audio":
            fname = urllib.url2pathname(args[args.rindex("/") + 1 : ])
            if not fnameline == "":
                fname = fnameline[fnameline.index("filename=") + 10 : fnameline.rindex("\"")]
            track = open(os.path.join(os.path.join(MUSIC_PATH, NICK + "_downloaded_music"), fname), "wb")
            track.write(dl.read())
            track.close()
            mpc.update()
            time.sleep(5)
            mpc.searchadd("file", fname)
            return_output(fname + " fetched and queued")
        else:
            return_output("Mime type " + dl.info().type + " not allowed.")
    except Exception, e:
        return_output(e)
        return_output("I dun goofed, soz aye m80.")

def cmd_add(command):
    args = command[4 : ]
    mpc.searchadd("any", args)

def cmd_current(command):
    song_info = ""
    return_output(mpc.currentsong())

def cmd_queue(command):
    queue = mpc.playlist()
    queuestr = "Next 4 of %s tracks:\n" % len(queue)
    for track in queue[ : 4]:
        queuestr += str(track)+"\n"
    return_output(queuestr)

def cmd_stats(command):
    return_output(mpc.stats())

def cmd_help(command):
    return_output("Available commands: .add .play .next .current .queue .stats .download")
    try:
        args = command[5:]
        if args.startswith("."):
            args = args[1:]
        return_output(HELP_DICT[args])
    except:
        pass

def return_output(text):
    #hopefully fixes issue where the first line of a message is sometimes dropped
    s.send("PRIVMSG " + HOME_CHANNEL + " :\r\n")
    #can only send 5 lines at a time on Rizon before being kicked for flood
    text=str(text)
    for msg in text.split("\n"):
        s.send("PRIVMSG " + HOME_CHANNEL + " :" + str(msg) + "\r\n")


def parse_command(command):
    try:
        mapped = command[:command.index(" ")]
    except ValueError:
        mapped = command
    try:
        COMMAND_MAPPING[mapped](command)
    except (KeyError, mpd.ConnectionError) as e:
        if type(e) == mpd.ConnectionError:
            reconnect_mpd()
            COMMAND_MAPPING[mapped](command)
        else:
            pass



COMMAND_MAPPING = {"dl": cmd_download, "download": cmd_download, "add": cmd_add, "play": cmd_play, "next": cmd_next, "current": cmd_current, "queue": cmd_queue, "stats": cmd_stats, "help": cmd_help}

print "*** Connecting... ***"
while 1:
    line = s.recv(2048)
    line = line.strip("\r\n")
    if("End of /NAMES list." in line):
	print "\n*** Connected! ***\n"
	break
    else:
	print line

if ANNOUNCE:
    t = threading.Thread(target = announce_wait, args=())
    t.daemon = 1
    t.start()

while 1:
    try:
        line = s.recv(2048)
        line = line.strip("\r\n")
        print line
        if "PING" in line:
            s.send("PONG :" + line[6 : ])
        elif "PRIVMSG" in line and not "NOTICE" in line and HOME_CHANNEL in line:
            command = line[line.rindex(HOME_CHANNEL + " :") + len(HOME_CHANNEL) + 2 : ]
            if "*" in command:
                return_output("NOPE")
            elif command.startswith("."):
                t = threading.Thread(target = parse_command, args=(command[1 : ],))
                t.daemon = 1
                t.start()
    except KeyboardInterrupt:
        sys.exit()
