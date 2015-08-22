import re
import inspect
from . import functions, regex_handler, send, _dispatch_ready

commands = {}
help_messages = {}


@functions
def command(*aliases):
    """
        Convenience decorator for command-like functionality

        Registers decorated function to handle lines
        starting with .<function-name> (or an optional list of
        aliases) and registers the function's docstring as a help
        message
    """
    def decorator(f):
        _aliases = aliases
        if callable(aliases[0]):
            _aliases = []
        _aliases += (f.__name__,)
        for cmd in _aliases:
            commands[cmd] = _dispatch_ready(f)
        if inspect.getdoc(f):
            help_messages[f.__name__] = inspect.getdoc(f)
        return f
    if callable(aliases[0]):
        return decorator(aliases[0])
    else:
        return decorator


@regex_handler("^\.\w+")
def command_dispatch(msg):
    cmd = re.findall("^\.(\w+)", msg['msg'])[0]
    if cmd in commands:
        commands[cmd](msg=msg, args=msg['msg'].split(" "))


@command
def help(args):
    """.help [command] - display help, optionally for a specific command"""
    args = args[1:]
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
