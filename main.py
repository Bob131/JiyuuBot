import socket
import mpd
import ssl
import os
import urllib2
import thread

MPD_HOST = "127.0.0.1"
MPD_PORT = 6600

HOST = "irc.rizon.net"
HOME_CHANNEL = "#AcuallyOS"
NICK = "JiyuuRadio"
PORT = 9999
SSL = True

MUSIC_PATH = "/media/music/Music"

mpc = mpd.MPDClient()
mpc.connect(MPD_HOST, MPD_PORT)

if(SSL):
    s = ssl.wrap_socket(socket.socket( ))
else:
    s = socket.socket( )
s.connect((HOST, PORT))
s.send("USER "+ NICK +" "+ NICK +" "+ NICK +" :"+NICK+"\n")
s.send("NICK "+ NICK +"\r\n")
s.send("JOIN "+ HOME_CHANNEL +"\r\n")

if not os.path.exists(os.path.join(MUSIC_PATH, NICK+"_downloaded_music")):
    os.mkdir(os.path.join(MUSIC_PATH, NICK+"_downloaded_music"))


def parse_command(command):
    if command.startswith("download") or command.startswith("dl"):
        args = command[command.index(" ")+1:]
        return_output("Fetching track "+args)
        track = open(os.path.join(os.path.join(MUSIC_PATH, NICK+"_downloaded_music"), args[args.rindex("/")+1:]), "wb")
        dl = urllib2.urlopen(args)
        track.write(dl.read())
        track.close()
        return_output(args+" fetched")
        mpc.update()
    elif command.startswith("add"):
        args = command[4:]
        mpc.searchadd("any", args)
    elif command == "play":
        mpc.play()
    elif command == "next":
        mpc.next()
    elif command == "current":
        return_output(mpc.currentsong())
    elif command == "queue":
        queue = "Next 4 tracks:\n"
        for track in mpc.playlist()[:4]:
            queue += str(track)+"\n"
        return_output(queue)
    elif command == "stats":
        return_output(mpc.stats())
    elif command == "clear":
        mpc.clear()
    elif command.startswith("help"):
        return_output("Available commands: .add .play .next .current .queue .stats .clear .download")

        try:
            args = command[5:]
            if args.startswith("."):
                args = args[1:]

            if args == "add":
                return_output(".add - adds tracks")
            elif args == "play":
                return_output(".play - starts playing (useful for when the stream dies due to lack of queued tracks")
            elif args == "next":
                return_output(".next - next track")
            elif args == "current":
                return_output(".current - prints infor about current track")
            elif args == "queue":
                return_output(".queue - shows next 4 songs")
            elif args == "stats":
                return_output(".stats - shows stats")
            elif args == "clear":
                return_output(".clear - clears curent queue")
            elif args == "download" or "dl":
                return_output(".download | .dl - downloads track from URL and updates db")
        except:
            pass

def return_output(text):
    #can only send 5 lines at a time on Rizon before being kicked for flood
    text=str(text)
    for msg in text.split("\n"):
        s.send("PRIVMSG "+HOME_CHANNEL+" :"+str(msg)+"\r\n")



print "*** Connecting... ***"
while 1:
    line = s.recv(2048)
    line = line.strip("\r\n")
    if("End of /NAMES list." in line):
	print "\n*** Connected! ***\n"
	break
    else:
	print line

while 1:
    try:
        line = s.recv(2048)
        line = line.strip("\r\n")
        print line
        if "PING" in line:
            s.send("PONG :"+line[6:])
        elif "PRIVMSG" in line and not "NOTICE" in line and HOME_CHANNEL in line:
            command = line[line.rindex(HOME_CHANNEL+" :")+len(HOME_CHANNEL)+2:]
            if "*" in command:
                return_output("NOPE")
            elif command.startswith("."):
                print command
                thread.start_new_thread(parse_command, command[1:])
    except Exception, e:
        return_output(e)
        return_output("I dun goofed, soz aye m80.")
