from . import command, send, help_messages

@command
def help(msginfo):
    """.help [command] - display help, optionally for a specific command"""
    args = msginfo["msg"].split(" ")[1:]
    if len(args) == 0:
        cmdlist = []
        for key in help_messages:
            cmdlist.append("."+key)
        send("{} commands available:".format(len(cmdlist)))
        send(" ".join(sorted(cmdlist)))
    else:
        for arg in args:
            if arg.startswith("."):
                arg = arg[1:]
            if arg in help_messages:
                messages = help_messages[arg].split("\n")
                messages = [messages[0]] + ["  "+msg for msg in messages if not msg == messages[0] and msg.strip()]
                for msg in messages:
                    send(msg)
            else:
                send("Help for \x02{}\x02 not available".format(arg))
