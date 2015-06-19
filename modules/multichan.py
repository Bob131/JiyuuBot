import re
from . import get_interface, command, raw_handler, subscribe, send

@subscribe("IRC")
@command
def chans(msginfo):
    """.chans - shows channels we're serving"""
    chan_list = get_interface().joined_chans
    send("Serving {} channel{}: {}".format(len(chan_list), "s" if len(chan_list) > 1 else "", ", ".join(chan_list)))


@subscribe("IRC")
@raw_handler
def invite(msginfo):
    if get_interface().get_command(msginfo["raw"]) == "INVITE":
        chan = msginfo["raw"][msginfo["raw"].index(" :")+2:]
        get_interface().join_irc(chan)


@subscribe("IRC")
@raw_handler
def kick(msginfo):
    if get_interface().get_command(msginfo["raw"]) == "KICK":
        beingkicked = msginfo["raw"][msginfo["raw"].rindex(":")+1:]
        NICK = get_interface().config["nick"]
        if beingkicked == NICK:
            chan = re.findall("(#[^\s,]+)", msginfo["raw"])[0]
            nick = msginfo["raw"][:msginfo["raw"].index("!")]
            get_interface().leave_irc(chan)
