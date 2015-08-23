import queue
import glob
import os
import threading
import configparser
import traceback
import types
import time
import signal
import pickle
import multiprocessing as mp
from multiprocessing import queues as mpq


def EmptyFunc():
    pass

class BaseInterface:
    """Base interface class: You should inherit from this"""

    #: List of config options which must be present for this interface to successfully initialise
    MANDATORY_CONFIG_OPTIONS = []

    #: Name of current instance. Set by __init__
    id = ""
    #: Dictionary of this instance's configured options. Set by __init__
    config = {}
    #: Our own queue of messages to be sent. Set by __init__
    send_queue = None
    #: Shared queue for incoming messages. Set by __init__
    recv_queue = None

    def __init__(self, id, config):
        self.id = id
        self.config = config
        self.validate_config()
        self._running = True


    def __del__(self):
        self._running = False


    def _wait_on_queue(self):
        while not self.send_queue.empty():
            time.sleep(0.1)


    def run(self, recv_queue, int_pipe):
        # we're in our own process now; monkeypatch `print`
        print = lambda *args, **kwargs: self.print(*args, **kwargs)
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        self.recv_queue = recv_queue
        self.send_queue = queue.Queue()
        self.init_hooks()

        for target in [self.recv, self.send]:
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()

        while self._running:
            req_attr = int_pipe.recv()
            args = int_pipe.recv()
            try:
                if args is None:
                    int_pipe.send(getattr(self, req_attr))
                else:
                    int_pipe.send(getattr(self, req_attr)(*args))
            except pickle.PicklingError:
                int_pipe.send(EmptyFunc)
            except Exception as e:
                int_pipe.send(e)

        self._wait_on_queue()
        self.del_hooks()
        print("Requesting destruction...")
        int_pipe.send("DONE")


    def validate_config(self):
        for option in self.MANDATORY_CONFIG_OPTIONS:
            if not option in self.config:
                raise Exception("Mandatory option missing in config for '{}': {}".format(self.id, option))


    def print(self, *text, **kwargs):
        __builtins__["print"]("{} !!! ".format(self.id), end="")
        __builtins__["print"](*text, **kwargs)


    def queue_raw(self, text):
        """
            Write raw message directly to send_queue.
            Avoid overriding this if you can.
        """
        self.send_queue.put(str(text) + "\r\n", True)


    def queue(self, text, dest):
        """Generic queuing interface. This will be called directly by modules"""
        pass


    def del_hooks(self):
        """__del__ hook: Override this to close sockets, logout etc"""
        pass


    def init_hooks(self):
        """__init__ hook: Override this to set up sockets etc"""
        pass


    def recv(self):
        """
            Read from socket and write to recv_queue.

            .. NOTE:: This will be started automatically in a new thread by __init__
        """
        pass


    def send(self):
        """
            Read from send_queue and write to socket

            .. NOTE:: This will be started automatically in a new thread by __init__
        """
        pass


class PipeProxy:
    def __init__(self, main_pipe, process):
        self._pipe = main_pipe
        self._process = process
        self._lock = threading.Lock()

    def _send(self, name, args=None):
        with self._lock:
            self._pipe.send(name)
            self._pipe.send(args)
            r = self._pipe.recv()
        if isinstance(r, Exception):
            raise r
        return r

    def __getattr__(self, name):
        r = self._send(name)
        if r == EmptyFunc:
            def r(*args):
                return self._send(name, args)
        return r

    def __setattr__(self, name, value):
        if not name.startswith('_'):
            raise Exception("Can't assign values to members of PipeProxy")
        self.__dict__[name] = value

    def _cleanup(self):
        self.__getattr__("__del__")()
        with self._lock:
            # wait until cleanup done
            self._pipe.recv()
            self._process.terminate()


class LockableQueue(mpq.Queue):
    _lock = False

    def put(self, *args, **kwargs):
        if not self._lock:
            super().put(*args, **kwargs)

def _queue(self, maxsize=0):
    return LockableQueue(maxsize, ctx=self.get_context())
mp.Queue = types.MethodType(_queue, mp)


interfaces = {}
interface_instances = {}

#: Shared queue for incoming messages
recv_queue = mp.Queue()

def register(cls):
    """Register new interface type"""
    if cls.__name__ in interfaces:
        raise Exception("Interface with this name already loaded: {}".format(cls.__name__))
    interfaces[cls.__name__] = cls

modules = glob.glob(os.path.dirname(__file__)+"/*.py")
__all__ = [os.path.basename(f)[:-3] for f in modules]
from . import *


def main():
    # Initialise interfaces as per configuration
    config = configparser.ConfigParser()
    config.read("{}/../configs/interfaces.ini".format(os.path.dirname(__file__)))

    if len(config.sections()) == 0:
        raise Exception("No interfaces configured")

    for instance in config.sections():
        interface, name = instance.split(":")
        if name in interface_instances:
            raise Exception("Cannot have more than one interface of the same name: {}".format(name))
        ni = interfaces[interface](id=name, config=config[instance])
        main_pipe, int_pipe = mp.Pipe()
        p = mp.Process(target=ni.run, args=(recv_queue, int_pipe), name=name)
        p.daemon = True
        p.start()
        interface_instances[name] = PipeProxy(main_pipe, p)
