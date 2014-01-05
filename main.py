# coding: utf-8
import os
import sys

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
servman = load.ServiceMan(conman, plugman)
httpd = http.httpd_api(plugman, http_responses)

#Main active loop
while 1:
    try:
        line = conman.s.recv(2048)
        line = line.strip("\r\n")
        print line
        if "PING" in line:
            conman.queue_raw("PONG :" + line[6 : ])
        elif "PRIVMSG" in line and not "NOTICE" in line and HOME_CHANNEL in line:
            command = line[line.rindex(HOME_CHANNEL + " :") + len(HOME_CHANNEL) + 2 : ]
            nick = line[1:line.index("!")]
            cmd = command.split(" ")
            permitted = True
            if command.startswith("."):
                try:
                    permitted = permsman.get_perms(nick, cmd[0][1:])
                except Exception as e:
                    conman.privmsg(str(e))
                    conman.privmsg("Assuming user is authorized")
                    permitted = True
                if permitted:
                    plugman.execute_command(command[1:], "PRIVMSG")
                elif not permitted:
                    conman.privmsg("You are not permitted to execute this command")
        elif line == "":
            conman.reconnect_irc()
    except KeyboardInterrupt:
        sys.exit()
