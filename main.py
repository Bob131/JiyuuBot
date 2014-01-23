# coding: utf-8
import os
import sys
import time
import re

import connect
import load
import permsman
import configman
import http


#Load config file from config.py
exec(open(os.path.join(os.path.dirname(__file__), "configs" + os.sep + "config.py"), "r").read())

thread_types = {}
http_responses = {}

#initialize plugin manager and load plugins
confman = configman.ConfigMan("global")
conman = connect.ConnectionMan(thread_types, http_responses, confman)
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
            if line.startswith(":"):
                line = line[1:]
            print line
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
                            plugman.execute_command(command[1:], {"type": "PRIVMSG", "source": chan})
                        else:
                            conman.privmsg("You are not permitted to execute this command", chan)
                    else:
                        if permsman.get_msg_perms(nick):
                            if permsman.get_perms(nick, cmd[0][1:]):
                                plugman.execute_command(command[1:], {"type": "PRIVMSG", "source": chan})
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
                                plugman.execute_command(command, {"type": "regex", "source": chan, "pattern": match})
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
                del conman.joined_chans[conman.joined_chans.index(chan)]
	        chanlist = confman.get_value("IRC", "CHANS", [])
	        del chanlist[chanlist.index(chan)]
	        confman.set_value("IRC", "CHANS", chanlist)
                print "\n*** %s left! ***\n" % chan
                if chan == HOME_CHANNEL:
                    conman.join_irc(chan)
                else:
                    conman.privmsg("Kicked from %s by %s" % (chan, nick), HOME_CHANNEL)
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
