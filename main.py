#!/usr/bin/env python3
# coding: utf-8
import os
import sys
import time
import re
import traceback
import unicodedata
import signal
import atexit
import threading

import watchdog.events
import watchdog.observers

import connect
import load
import permsman
import configman
import logger


#load config
confman = configman.ConfigMan("global")

#init logger
sys.stdout = logger.stdoutLog(confman.get("MISC", "LOG", True))

lock = threading.Lock()

#initialize plugin manager and load plugins
conman = connect.ConnectionMan(confman)
permsman = permsman.PermsMan(confman)
plugman = load.PluginMan(conman, confman, permsman)
#TODO: Reimplement
#servman = load.ServiceMan(conman, plugman, thread_types)

def bye(txt):
    conman.privmsg(txt)
    conman.broadcast("Going down for core libs update")


class inot_handler(watchdog.events.FileSystemEventHandler):
    def __init__(self):
        self.invoke = []

    def clear_invoke(self, path):
        time.sleep(60)
        self.invoke.remove(path)

    def on_any_event(self, event):
        lock.acquire()
        path = event.src_path
        if not event.is_directory:
            if event.event_type == "modified" or event.event_type == "deleted" or event.event_type == "moved":
                if not "/configs" in path and not "/." in path and not "~" in path and not "4913" in path and not "/logs" in path and not path in self.invoke:
                    if "/modules" in path:
                        path = "/modules" # don't reload for every single module
                        rel = not "/modules" in self.invoke
                    t = threading.Thread(target=self.clear_invoke, args=(path,))
                    self.invoke.append(path)
                    t.start()
                    if path == "/modules":
                        if rel:
                            time.sleep(10) # hopefully module updates are done by now
                            conman.privmsg("Update to modules detected")
                            plugman.execute_command({"msg": ".reload", "type": "PRIVMSG", "chan": confman.get("IRC", "HOME_CHANNEL")})
                    else:
                        print("Core update detected")
                        bye("Update to core libs detected")
                        time.sleep(10) # wait for remaining messages to be sent
                        conman.s.close()
                        os.execv(__file__, sys.argv)
        lock.release()

observer = watchdog.observers.Observer()
observer.schedule(inot_handler(), "./", recursive=True)
observer.start()

def close_inot():
    observer.stop()
    observer.join()

atexit.register(close_inot)


def SIGHUPhandle(_, __):
    conman.privmsg("Received SIGHUP! Reloading modules")
    plugman.execute_command({"msg": ".reload", "type": "PRIVMSG", "chan": confman.get("IRC", "HOME_CHANNEL")})

def SIGTERMhandle(_, __):
    bye("Received SIGTERM! Going down")
    time.sleep(10) # wait for remaining messages to be sent
    sys.exit(0)

signal.signal(signal.SIGHUP, SIGHUPhandle)
signal.signal(signal.SIGTERM, SIGTERMhandle)


#Main active loop
while 1:
    try:
        # receive and format line for parsing
        line = conman.s.recv()

        if line == None:
            print("*** Ping timeout. Waiting 60 seconds and trying again ***")
            time.sleep(60)
            conman.reconnect_irc()

        else:
            if line.startswith(":"):
                line = line[1:]

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
                # strip out non-printable chars. See http://www.unicode.org/reports/tr44/tr44-6.html#Code_Point_Labels
                for char in line[line.index(msginfo["chan"] + " :")+len(msginfo["chan"])+2:]:
                    if not unicodedata.category(char).startswith("C"):
                        msginfo["msg"] += char
                msginfo["msg"] = msginfo["msg"].strip()

                if msginfo["msg"].lower().startswith(confman.get("IRC", "NICK").lower()):
                    msginfo["msg"] = msginfo["msg"][len(confman.get("IRC", "NICK")):]
                    msginfo["msg"] = re.sub("[,:\s]*", "", msginfo["msg"])

                # if this is an IM, set chan to the offending nick so the response can be properly directed
                if msginfo["chan"] == confman.get("IRC", "NICK"):
                    msginfo["chan"] = msginfo["nick"]
                    # if not authorized, notify the user
                    if not permsman.get_msg_perms(msginfo["hostname"]):
                        conman.gen_send("You do not have adequate permissions for IM", msginfo)
                        continue

                # if msg is a command, execute
                if msginfo["msg"].startswith("."):
                    # check whether its an actual command
                    if msginfo["msg"].split(" ")[0].replace(".", "") in plugman.commandlist.keys():
                        # ensure adequate permssions (move this to load.py to enabled perms checking on regex functions?)
                        if permsman.get_perms(msginfo["hostname"], msginfo["msg"].split(" ")[0][1:]):
                            msginfo["type"] = "PRIVMSG"
                            plugman.execute_command(msginfo)
                        else:
                            conman.gen_send("You do not have high enough permissions to execute that command", msginfo)

                # check whether message matches any mapped regex strings
                matches = list(pattern for pattern in plugman.regex_cache if not re.match(pattern, msginfo["msg"]) == None)
                if len(matches) > 0:
                    msginfo["type"] = "regex"
                    for match in matches:
                        msginfo["pattern"] = match
                        plugman.execute_command(msginfo)

            # irc connection lost; time to reconnect
            elif line == "":
                conman.reconnect_irc()

            # allow modules to hook for other commands
            else:
                command = line.split(" ")[1]
                if "!" + command in plugman.commandlist.keys():
                    # offload all parsing to module
                    msginfo = {"strg": line, "type": "regex", "pattern": "!" + command} # reg as regex for simplicity
                    msginfo["chan"] = confman.get("IRC", "HOME_CHANNEL") # so error handlers know where to spit msgs
                    plugman.execute_command(msginfo)
    except Exception as e:
        if not type(e) == InterruptedError:
            traceback.print_exc()
