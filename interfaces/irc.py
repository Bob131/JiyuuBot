import socket
import ssl
import os
import queue
import threading
import time
import sys
import select
import unicodedata
import re
import traceback

from . import BaseInterface, register


@register
class IRC(BaseInterface):
    MANDATORY_CONFIG_OPTIONS = ['HOST', 'NICK']

    def init_hooks(self):
        self.s = socket.socket()
        #If SSL is enabled use ssl
        if self.config.get("SSL", True):
            self.s = ssl.wrap_socket(self.s)

        self.print("Connecting to {}:{}".format(self.config["HOST"], self.config.get("PORT", 6697)))

        self.s.connect((self.config["HOST"], self.config.get("PORT", 6697)))
        self.s.settimeout(2)

        while True:
            try:
                line = self.s.recv().decode("UTF-8").strip()
            except socket.timeout:
                break

        # RFC 2812: USER message params are: <user> <mode> <unused> <realname>
        self.s.send(bytes("USER " + self.config["NICK"] + " 0 * :" + self.config["NICK"] + "\r\n", "UTF-8"))
        self.s.send(bytes("NICK " + self.config["NICK"] + "\r\n", "UTF-8"))

        while True:
            try:
                line = self.s.recv().decode("UTF-8").strip()
            except socket.timeout:
                break
            if "Nickname is already in use" in line:
                self.config["NICK"] += "_"
                self.print("Nick taken; trying {}".format(self.config["NICK"]))
                self.s.send(bytes("NICK " + self.config["NICK"] + "\r\n", "UTF-8"))
            elif "PING" in line:
                self.s.send(bytes("PONG :" + line[6:] + "\r\n", "UTF-8"))

        self.s.settimeout(250)

        self.joined_chans = set()
        for channel in self.config.get("CHANS", "").split(","):
            if not channel.strip() == "":
                self.join_irc(channel)


    def del_hooks(self):
        self.queue_raw("QUIT :Bot shutdown requested")
        self._wait_on_queue()
        self.s.close()


    def send(self):
        OUTGOING_DELAY = self.config.get("OUTGOING_DELAY", 300)
        while True:
            msg = self.send_queue.get(True)
            try:
                self.s.send(bytes(msg, "UTF-8"))
                print("{} >>> {}".format(self.id, msg.strip()))
            except:
                pass
            time.sleep(OUTGOING_DELAY / 1000)

    def recv(self):
        while True:
            try:
                try:
                    line = self.s.recv().decode("UTF-8").strip()
                except socket.timeout:
                    self.print("Ping timeout")
                    time.sleep(10)
                    self.reconnect()
                    continue
                print("{} <<< {}".format(self.id, line))
                if line.startswith(":"):
                    line = line[1:]
                msg = {
                        "raw": line,
                        "id": self.id,
                        "iface": self.__class__.__name__
                        }
                command = self.get_command(line)
                # respond to pings
                if command == "PING":
                    # line[6:] strips out "PING: "
                    self.queue_raw("PONG :" + line[6:])
                elif command == "JOIN":
                    chan = line.split(":")[1]
                    self.joined_chans.add(chan)
                # we have a message! Parse it
                elif command == "PRIVMSG":
                    # create dict for passing message info
                    # include original message + info parsed from it and other contextual data
                    msg.update({
                            "msg": "", # parsing requires values in this struct
                            "dest": line.split(" ")[2],
                            "src": line[:line.index("!")],
                            "tag": line.split(" ")[0],
                            })
                    # correct dest
                    if msg["dest"] == self.config["NICK"]:
                        msg["dest"] = msg["src"]
                    # strip out non-printable chars. See http://www.unicode.org/reports/tr44/tr44-6.html#Code_Point_Labels
                    for char in line.split(":", 1)[1]:
                        if not unicodedata.category(char).startswith("C"):
                            msg["msg"] += char
                    msg["msg"] = msg["msg"].strip()

                self.recv_queue.put(msg)
            except:
                traceback.print_exc()


    def get_command(self, line):
        return (line.split(" ")[1] if len(line.split(" ")) > 2 else line.split(" ")[0]).upper()


    # function for joining channels
    def join_irc(self, chan):
        self.queue_raw("JOIN " + chan)
        time.sleep(2)


    # parting channels
    def leave_irc(self, chan):
        self.joined_chans.remove(chan)


    # reconnect to IRC
    def reconnect_irc(self):
        pass


    # generic send function
    def queue(self, text, dest):
        self.queue_raw("PRIVMSG " + dest + " :" + text)
