# coding: utf-8
import load
import os
import sys

#Load config file from config.py
exec(open(os.path.join(os.path.dirname(__file__), "config.py"), "r").read())

#initialize plugin manager and load plugins
plugman = load.PluginMan()

#connect to irc server
print "*** Connecting... ***"
while 1:
    line = plugman.conman.s.recv(2048)
    line = line.strip("\r\n")
    if("End of /NAMES list." in line):
	print "\n*** Connected! ***\n"
	break
    else:
	print line

#Main active loop
while 1:
    try:
        line = plugman.conman.s.recv(2048)
        line = line.strip("\r\n")
        print line
        if "PING" in line:
            plugman.conman.s.send("PONG :" + line[6 : ])
        elif "PRIVMSG" in line and not "NOTICE" in line and HOME_CHANNEL in line:
            command = line[line.rindex(HOME_CHANNEL + " :") + len(HOME_CHANNEL) + 2 : ]
            if command.startswith("."):
                plugman.execute_command(command[1:])
    except KeyboardInterrupt:
        sys.exit()
