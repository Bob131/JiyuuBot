import os
import sys
import glob
import threading
import json
import re
import traceback
import types
import io
import importlib
import inspect
import configparser

_print = print

def print(*args, **kwargs):
    class hack(io.TextIOWrapper):
        def write(b):
            if b.strip():
                sys.stdout.write(" !!! ")
            sys.stdout.write(b)
    kwargs["file"] = hack
    _print(*args, **kwargs)


class ThreadManager:
    def trywrapper(self, f, msginfo):
        msginfo["_function_id"] = f.__name__
        thread_details[threading.get_ident()] = msginfo.copy()
        try:
            if len(inspect.signature(f).parameters) > 0:
                f(msginfo)
            else:
                f()
        except Exception as e:
            traceback.print_exc()
            if msginfo.get("msg"):
                send("Error executing {}: {}".format(command, e))
        del thread_details[threading.get_ident()]

    def __call__(self, msginfo):
        if msginfo.get("msg"):
            for f in [regex_handlers[regex] for regex in regex_handlers if re.match(regex, msginfo["msg"])]:
                if self.subscribed(msginfo, f.__name__):
                    t = threading.Thread(target=self.trywrapper, args=(f, msginfo))
                    t.daemon = 1
                    t.start()
        else:
            for f in raw_handlers:
                if self.subscribed(msginfo, f.__name__):
                    t = threading.Thread(target=self.trywrapper, args=(f, msginfo))
                    t.daemon = 1
                    t.start()

    def subscribed(self, msginfo, name=None):
        if msginfo["iface"] in subscribers.get(name or msginfo["_function_id"], [msginfo["iface"]]):
            return True
        return False

    # PluginMan constructor
    def __init__(self, interfaces):
        self.interfaces = interfaces


class FunctionMapper:
    def __init__(self):
        self._functions = {}

    def __call__(self, f):
        self._functions[f.__name__] = f
        return f

    def __getattr__(self, key):
        return self._functions[key]

    def __contains__(self, key):
        if self._functions.get(key):
            return True
        return False

# don't import me!
global threadman

#: Decorator to register functions as well as object from which
#: registered functions can be accessed
functions = FunctionMapper()

subscribers = {}
raw_handlers = []
regex_handlers = {}
help_messages = {}

thread_details = {}

_config = configparser.ConfigParser()
_config.read("{}/../configs/modules.ini".format(os.path.dirname(__file__)))

def require(name):
    """Test whether required function has been loaded"""
    if not name in functions:
        raise Exception("Required function %s not loaded" % name)

def subscribe(*ifaces):
    """Subscribe to receive messages only from specific interface types"""
    def decorator(f):
        subscribers[f.__name__] = ifaces
        return f
    return decorator

def raw_handler(f):
    """
        Register function to handle raw messages.
        Use with the `subscribe()` decorator.
    """
    raw_handlers.append(f)
    return f

def regex_handler(pattern):
    """Call decorated function if `pattern` matches a parsed message"""
    def decorator(f):
        regex_handlers[re.compile(pattern, re.IGNORECASE)] = f
        return f
    return decorator

def command(*aliases):
    """
        Convenience function for command-like functionality

        Registers decorated function to handle regexes for lines
        starting with .<function-name> (or an optional list of
        aliases) and registers the function's docstring as a help
        message
    """
    def decorator(f):
        _aliases = aliases
        if callable(aliases[0]):
            _aliases = [f.__name__]
        for cmd in _aliases:
            regex_handler("^\.{}.*".format(cmd))(f)
        if inspect.getdoc(f):
            help_messages[f.__name__] = inspect.getdoc(f)
        return f
    if callable(aliases[0]):
        return decorator(aliases[0])
    else:
        return decorator

def config():
    """
        Access this module's config

        Returns a dictionary corresponding to the config section headed
        by the calling function's __name__
    """
    id = thread_details[threading.get_ident()]["_function_id"]
    if _config.has_section(id):
        return _config[id]
    return {}

def get_interface():
    """
        Get invoking interface

        Returns a reference to the interface that generated the message
        currently being handled. The calling function must be explicitly
        subscribed to handle messages from this interface
    """
    msg = thread_details[threading.get_ident()]
    # make sure the module knows what its doing
    if threadman.subscribed(msg):
        return threadman.interfaces[msg["id"]]
    raise Exception("Must be subscribed to access interface: "+msg["_function_id"])

def send(text, dest=None, interface=None):
    """
        Send a message. Defaults to sending to the same destination of
        the message currently being handled on the same interface
    """
    id = threading.get_ident()
    msg = thread_details[id]
    if not interface:
        interface = thread_details[id]["id"]
    if msg.get("msg"):
        if not dest:
            dest = thread_details[id]["dest"]
        threadman.interfaces[interface].queue(text, dest)
    else:
        threadman.interfaces[interface].queue_raw(text)

def setup(interfaces):
    global threadman
    threadman = ThreadManager(interfaces)

def load():
    plugincount = 0
    failcount = 0
    blockcount = 0
    modules = glob.glob(os.path.dirname(__file__)+"/*.py")
    blacklist = [m.strip() for m in _config.get("DEFAULT", "blacklist", fallback="").split(",")]
    blacklist += ["__init__"] # make sure we don't load ourselves
    for module in modules:
        module = os.path.basename(module)[:-3]
        if not module in blacklist:
            try:
                importlib.import_module("."+module, "modules")
                plugincount += 1
            except:
                traceback.print_exc()
                failcount += 1
        elif not module == "__init__":
            blockcount += 1
    loaded_modules = "Successfully loaded {} modules".format(plugincount)
    if failcount > 0:
        loaded_modules += " | {} modules failed".format(failcount)
    if blockcount > 0:
        loaded_modules += " | {} modules blocked".format(blockcount)
    print(loaded_modules)


load()
