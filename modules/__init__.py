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

from functools import wraps

def print(*args, **kwargs):
    class hack(io.TextIOWrapper):
        def write(b):
            if b.strip():
                sys.stdout.write(" !!! ")
            sys.stdout.write(b)
    kwargs["file"] = hack
    __builtins__["print"](*args, **kwargs)

def _dispatch_ready(f):
    @wraps(f)
    def dispatch(**kwargs):
        nkwargs = {}
        for arg in inspect.signature(f).parameters.keys():
            if not arg in kwargs:
                raise Exception("Requested arg '{}' not provided: {}".format(arg, f))
            nkwargs[arg] = kwargs[arg]
        return f(**nkwargs)
    return dispatch

class ThreadManager:
    def trywrapper(self, f, msginfo):
        msginfo["_function_id"] = f.__name__
        thread_details[threading.get_ident()] = msginfo.copy()
        try:
            f(msg=msginfo)
        except Exception as e:
            traceback.print_exc()
            if msginfo.get("msg"):
                send("Error executing {}: {}".format(f, e))
        del thread_details[threading.get_ident()]

    def __call__(self, msginfo):
        if msginfo.get("msg") and msginfo.get("dest"):
            for f in [regex_handlers[regex] for regex in regex_handlers if re.search(regex, msginfo["msg"])]:
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
        self.lock = threading.Lock()


class functions(object):
    """
        Decorator to register functions for later use.

        Functions listed below are exported by modules.
    """

    def __new__(self, f):
        setattr(self, f.__name__, f)
        return f


# don't import me!
global threadman

subscribers = {}
raw_handlers = []
regex_handlers = {}

thread_details = {}

_config = configparser.ConfigParser()
_config.read("{}/../configs/modules.ini".format(os.path.dirname(__file__)))

def requires(*names):
    """
        Decorator to indicate function depends on certain `names` being
        loaded in `functions`
    """
    def decorate(f):
        @wraps(f)
        def require(*args, **kwargs):
            for name in names:
                if not getattr(functions, name, None):
                    raise Exception("Required function {} not loaded".format(name))
            return f(*args, **kwargs)
        return require
    return decorate

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
    raw_handlers.append(_dispatch_ready(f))
    return f

def regex_handler(pattern):
    """Call decorated function if `pattern` matches a parsed message"""
    def decorator(f):
        regex_handlers[re.compile(pattern, re.IGNORECASE)] = _dispatch_ready(f)
        return f
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
    modules = sorted(glob.glob(os.path.dirname(__file__)+"/*.py"),
            key=lambda x: (os.path.basename(x)[0]!="_", x))
    blacklist = [m.strip() for m in _config.get("DEFAULT", "blacklist", fallback="").split(",")]
    blacklist += ["__init__"] # make sure we don't load ourselves
    for module in modules:
        module = os.path.basename(module)[:-3]
        if not module in blacklist:
            try:
                _ = importlib.import_module("."+module, "modules")
                importlib.reload(_) # in case of a reload
                plugincount += 1
            except:
                traceback.print_exc()
                failcount += 1
        elif not module == "__init__":
            blockcount += 1
    loaded_modules = "Successfully (re)loaded {} modules".format(plugincount)
    if failcount > 0:
        loaded_modules += " | {} modules failed".format(failcount)
    if blockcount > 0:
        loaded_modules += " | {} modules blocked".format(blockcount)
    print(loaded_modules)


load()
