# coding: utf-8
import os
import sys
import time
import re

import connect
import load
import permsman
import http


#Load config file from config.py
exec(open(os.path.join(os.path.dirname(__file__), "configs" + os.sep + "config.py"), "r").read())

thread_types = {}
http_responses = {}

#initialize plugin manager and load plugins
conman = connect.ConnectionMan(thread_types, http_responses)
permsman = permsman.PermsMan()
plugman = load.PluginMan(conman, permsman, thread_types)
servman = load.ServiceMan(conman, plugman, thread_types)
if HTTPD:
    httpd = http.httpd_api(plugman, http_responses)

#Main active loop
while 1:
    try:
        if IRC:
            line = conman.s.recv(2048)
            line = line.strip("\r\n")
            print line
            if "PING" in line:
                conman.queue_raw("PONG :" + line[6 : ])
            elif "PRIVMSG" in line and not "NOTICE" in line:
                chan = line[line.rindex("PRIVMSG ") + 8 : line.rindex(" :")]
                nick = line[1:line.index("!")]
                command = line[line.rindex(chan + " :") + len(chan) + 2 : ]
                if chan == NICK:
                    chan = nick
                cmd = command.split(" ")
                permitted = True
                if command.startswith("."):
                    if chan.startswith("#"):
                        permitted = permsman.get_perms(nick, cmd[0][1:])
                        if permitted:
                            plugman.execute_command(command[1:], "PRIVMSG:"+chan)
                        else:
                            conman.privmsg("You are not permitted to execute this command", chan)
                    else:
                        permitted = permsman.get_msg_perms(nick)
                        if permitted:
                            plugman.execute_command(command[1:], "PRIVMSG:"+chan)
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
                                plugman.execute_regex(match, command, chan)
                    else:
                        conman.privmsg("You are not permitted to message", chan)
            elif "INVITE" in line:
                nick = line[1:line.index("!")]
                chan = line[line.index(" :")+2:]
                if permsman.get_msg_perms(nick):
                    conman.join_irc(chan, nick)
                else:
                    conman.privmsg("You are not permitted to invite", nick)
            elif line == "":
                conman.reconnect_irc()
        else:
            time.sleep(10)
    except Exception as e:
        print "Error occured: %s" % str(e)
        print "Cleaning up..."
        if HTTPD:
            httpd.serv.close()
        print "Bye"
        sys.exit()
