#!/usr/bin/env python3
# coding: utf-8
import os
import sys
import time
import re
import traceback
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
permsman = permsman.PermsMan(confman)
conman = connect.ConnectionMan(confman, permsman)
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
                        bye("Update to core libs detected")
                        time.sleep(10) # wait for remaining messages to be sent
                        conman.instances["irc"].s.close()
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
        msginfo = conman.read()
        # if msg is a command, execute
        if msginfo.get("msg", "").startswith("."):
            msginfo["type"] = "PRIVMSG"
            plugman.execute_command(msginfo.copy())

        # check whether message matches any mapped regex strings
        if msginfo.get("command", "PRIVMSG") == "PRIVMSG":
            matches = list(pattern for pattern in plugman.regex_cache if not re.match(pattern, msginfo.get("msg", "")) == None)
            if len(matches) > 0:
                msginfo["type"] = "regex"
                for match in matches:
                    msginfo["pattern"] = match
                    plugman.execute_command(msginfo.copy())

        if "!"+msginfo.get("command", "") in plugman.commandlist.keys():
            # offload all parsing to module
            msginfo.update({"type": "regex", "pattern": "!" + msginfo["command"]}) # reg as regex for simplicity
            msginfo["chan"] = confman.get("IRC", "HOME_CHANNEL") # so error handlers know where to spit msgs
            plugman.execute_command(msginfo)
    except Exception as e:
        if not type(e) == InterruptedError:
            traceback.print_exc()
