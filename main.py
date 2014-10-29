#!/usr/bin/env python3
# coding: utf-8
import os
import sys
import time
import re
import traceback

import connect
import load
import permsman
import configman
import jr_webd
import logger


#Load config file from config.py
exec(open(os.path.join(os.path.dirname(__file__), "configs" + os.sep + "config.py"), "r").read())

#init logger
sys.stdout = logger.stdoutLog()

#initialize plugin manager and load plugins
confman = configman.ConfigMan("global")
conman = connect.ConnectionMan(confman)
#TODO: Reimplement
#permsman = permsman.PermsMan()
plugman = load.PluginMan(conman, confman)
#TODO: Reimplement
#servman = load.ServiceMan(conman, plugman, thread_types)

#Main active loop
while 1:
    try:
        if IRC:
            # receive and format line for parsing
            try:
                line = conman.s.recv(2048).decode("UTF-8")
            except UnicodeDecodeError:
                continue
            line = line.replace("\r\n", "")
            if line.startswith(":"):
                line = line[1:]

            # log
            print("%s <<< %s" % (time.strftime("%Y-%m-%d %H:%M", time.localtime()), line))

            # respond to pings
            if "PING" in line and not "PRIVMSG" in line:
                # line[6:] strips out "PING: "
                conman.queue_raw("PONG :" + line[6:])
            elif "PRIVMSG" in line and "PING" in line:           
                # what? I really have no idea whats going on here, but it seems to work
                msg = "".join(line.split()[3:])[1:]   
                sender = line.split(":")[1].split('!')[0]
                conman.queue_raw("NOTICE %s :%s" % (sender, msg))

            # we have a message! Parse it
            elif "PRIVMSG" in line and not "NOTICE" in line and not "PING" in line:
                # create struct for passing message info
                # include original message + info parsed from it and other contextual data
                # may also include values 'type' and 'pattern'; see below
                msginfo = {
                        "strg": line,
                        "msg": "", # parsing requires values in this struct
                        "chan": line[line.index(" PRIVMSG ") + 9 : line.index(" :")],
                        "nick": line[:line.index("!")],
                        "user": line[line.index("!")+1:line.index("@")].replace("~", ""),
                        "hostname": line[line.index("@")+1:line.index(" ")],
                        "timestamp": time.time()}
                msginfo["msg"] = line[line.index(msginfo["chan"] + " :") + len(msginfo["chan"])+2: ]

                # if this is an IM, set chan to the offending nick so the response can be properly directed
                if msginfo["chan"] == NICK:
                    #TODO: Uncomment following line and implement PermsMan verification
                    #msginfo["chan"] = msginfo["nick"]
                    continue

                # if msg is a command, execute
                if msginfo["msg"].startswith("."):
                    msginfo["type"] = "PRIVMSG"
                    # get the first word following the '.' and execute the mapped command
                    plugman.execute_command(msginfo)
                else:
                    # check whether message matches any mapped regex strings
                    patterns = (pattern for pattern in plugman.commandlist.keys() if plugman.commandlist[pattern]["type"] == load.MAPTYPE_REGEX)
                    matches = list(pattern for pattern in patterns if not re.match(pattern, msginfo["msg"]) == None)
                    if len(matches) > 0:
                        msginfo["type"] = "regex"
                        for match in matches:
                            msginfo["pattern"] = match
                            plugman.execute_command(msginfo)

            # if we've been invited to a channel
            elif "INVITE" in line:
                nick = line[:line.index("!")]
                chan = line[line.index(" :")+2:]
                conman.join_irc(chan, nick)

            # if we've been kicked from a channel
            elif "KICK" in line and " %s " % NICK in line:
                chan = line[line.index("KICK ") + 5 : line.index(NICK)-1]
                nick = line[:line.index("!")]
                conman.leave_irc(chan, nick, True)

            # irc connection lost; time to reconnect
            elif line == "":
                conman.reconnect_irc()

        else:
            time.sleep(10)
    except Exception as e:
        traceback.print_exc()
