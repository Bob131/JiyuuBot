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

thread_types = {}
http_responses = {}

#initialize plugin manager and load plugins
confman = configman.ConfigMan("global")
conman = connect.ConnectionMan(thread_types, http_responses, confman)
permsman = permsman.PermsMan()
plugman = load.PluginMan(conman, permsman, confman, thread_types)
servman = load.ServiceMan(conman, plugman, thread_types)
if HTTPD:
    httpd = jr_webd.httpd_api(plugman, http_responses)

#Main active loop
while 1:
    try:
        if IRC:
            try:
                line = conman.s.recv(2048).decode("UTF-8")
            except UnicodeDecodeError:
                break
            line = line.replace("\r\n", "")
            if line.startswith(":"):
                line = line[1:]
            print("%s <<< %s" % (time.strftime("%Y-%m-%d %H:%M", time.localtime()), line))
            if "PING" in line:
                conman.queue_raw("PONG :" + line[6 : ])
            elif "PRIVMSG" in line and not "NOTICE" in line:
                chan = line[line.index(" PRIVMSG ") + 9 : line.index(" :")]
                nick = line[:line.index("!")]
                command = line[line.index(chan + " :") + len(chan) + 2 : ]
                if chan == NICK:
                    chan = nick
                cmd = command.split(" ")
                permitted = True
                if command.startswith("."):
                    if chan.startswith("#"):
                        permitted = permsman.get_perms(nick, cmd[0][1:])
                        if permitted:
                            plugman.execute_command(command[1:], {"type": "PRIVMSG", "source": chan, "nick": nick})
                        else:
                            conman.privmsg("You are not permitted to execute this command", chan)
                    else:
                        if permsman.get_msg_perms(nick):
                            if permsman.get_perms(nick, cmd[0][1:]):
                                plugman.execute_command(command[1:], {"type": "PRIVMSG", "source": chan, "nick": nick})
                            else:
                                conman.privmsg("You are not permitted to execute this command", chan)
                        else:
                            conman.privmsg("You are not permitted to message", chan)
                else:
                    permitted = True
                    if not chan.startswith("#"):
                        permitted = permsman.get_msg_perms(nick)
                    if permitted:
                        matches = list(pattern for pattern in plugman.regex.keys() if not re.match(pattern, command) == None)
                        if len(matches) > 0:
                            for match in matches:
                                plugman.execute_command(command, {"type": "regex", "source": chan, "pattern": match, "nick": nick})
                    else:
                        conman.privmsg("You are not permitted to message", chan)
            elif "INVITE" in line:
                nick = line[:line.index("!")]
                chan = line[line.index(" :")+2:]
                if permsman.get_msg_perms(nick):
                    conman.join_irc(chan, nick)
                else:
                    conman.privmsg("You are not permitted to invite", nick)
            elif "KICK" in line and " %s " % NICK in line:
                chan = line[line.index("KICK ") + 5 : line.index(NICK)-1]
                nick = line[:line.index("!")]
                conman.leave_irc(chan, nick, True)
            elif line == "":
                conman.reconnect_irc()
        else:
            time.sleep(10)
    except Exception as e:
        traceback.print_exc()
