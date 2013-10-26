# coding: utf-8
import connect
import load
import os
import sys

#Load config file from config.py
exec(open(os.path.join(os.path.dirname(__file__), "configs" + os.sep + "config.py"), "r").read())

#initialize plugin manager and load plugins
conman = connect.ConnectionMan()
plugman = load.PluginMan(conman)
servman = load.ServiceMan(conman, plugman)

#Main active loop
while 1:
    try:
        line = conman.s.recv(2048)
        line = line.strip("\r\n")
        print line
        if "PING" in line:
            conman.s.send("PONG :" + line[6 : ])
        elif "PRIVMSG" in line and not "NOTICE" in line and HOME_CHANNEL in line:
            command = line[line.rindex(HOME_CHANNEL + " :") + len(HOME_CHANNEL) + 2 : ]
            if command.startswith("."):
                plugman.execute_command(command[1:])
    except KeyboardInterrupt:
        sys.exit()
