from . import command, send, help_messages

@command("displays help. Syntax: .help [command]")
def help(msginfo):
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
                send(".{} - {}".format(arg, help_messages[arg]))
            else:
                send("Help for \x02{}\x02 not available".format(arg))
