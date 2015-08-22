import re
from . import get_interface, raw_handler, subscribe, send, functions

@subscribe("IRC")
@functions.command
def chans(msg):
    """.chans - shows channels we're serving"""
    chan_list = get_interface().joined_chans
    send("Serving {} channel{}: {}".format(len(chan_list), "s" if len(chan_list) > 1 else "", ", ".join(chan_list)))


@subscribe("IRC")
@raw_handler
def invite(msg):
    if get_interface().get_command(msg["raw"]) == "INVITE":
        chan = msg["raw"][msg["raw"].index(" :")+2:]
        get_interface().join_irc(chan)


@subscribe("IRC")
@raw_handler
def kick(msg):
    if get_interface().get_command(msg["raw"]) == "KICK":
        beingkicked = msg["raw"][msg["raw"].rindex(":")+1:]
        NICK = get_interface().config["nick"]
        if beingkicked == NICK:
            chan = re.findall("(#[^\s,]+)", msg["raw"])[0]
            nick = msg["raw"][:msg["raw"].index("!")]
            get_interface().leave_irc(chan)
