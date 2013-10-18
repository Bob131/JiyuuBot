import socket
import mpd
import ssl

MPD_HOST = "127.0.0.1"
MPD_PORT = 6600

HOST = "irc.rizon.net"
HOME_CHANNEL = "#AcuallyOS"
NICK = "JiyuuRadio"
PORT = 9999
SSL = True

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


def parse_command(command):
    if command.startswith("add"):
        args = command[4:]
        mpc.searchadd("any", args)
    elif command == "last":
        # should detect last song id and play that, but this'll do for the time being
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
    elif command == "help":
        #print help
        pass

def return_output(text):
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
    line = s.recv(2048)
    line = line.strip("\r\n")
    print line
    if "PING" in line:
        s.send("PONG :"+line[6:])
    elif "PRIVMSG" in line and not "NOTICE" in line and HOME_CHANNEL in line:
        command = line[line.rindex(":")+1:]
        if "*" in command:
            return_output("NOPE")
        elif command.startswith("."):
            parse_command(command[1:])
