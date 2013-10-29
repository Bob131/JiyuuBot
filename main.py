# coding: utf-8
import os
import sys

import connect
import load
import permsman


#Load config file from config.py
exec(open(os.path.join(os.path.dirname(__file__), "configs" + os.sep + "config.py"), "r").read())

#initialize plugin manager and load plugins
conman = connect.ConnectionMan()
permsman = permsman.PermsMan()
plugman = load.PluginMan(conman, permsman)
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
            nick = line[1:line.index("!")]
            cmd = command.split(" ")
            permitted = True
            try:
                permitted = permsman.get_perms(nick, cmd[0])
            except Exception as e:
                if str(e) == "Permissions config files malformed: Permission values must be integers in between 0 and 999":
                    conman.privmsg("Permissions config files malformed: Permission values must be integers in between 0 and 999")
                    conman.privmsg("Assuming user is authorized")
            if command.startswith(".") and permitted:
                plugman.execute_command(command[1:])
            elif command.startswith(".") and not permitted:
                conman.privmsg("You are not permitted to execute this command")
    except KeyboardInterrupt:
        sys.exit()
