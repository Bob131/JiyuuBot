import queue
import glob
import os
import threading
import configparser
import traceback


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

    def __init__(self, id, config):
        self.id = id
        self.config = config
        self.send_queue = queue.Queue()

        self.validate_config()
        self.init_hooks()

        for target in [self.recv, self.send]:
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()


    def validate_config(self):
        for option in self.MANDATORY_CONFIG_OPTIONS:
            if not option in self.config:
                raise Exception("Mandatory option missing in config for '{}': {}".format(self.id, option))


    def print(self, text):
        """Simple pretty-print override to make debug output and the like easier to read"""
        print("{} !!! {}".format(self.id, text))


    def queue_raw(self, text):
        """Write raw message directly to send_queue"""
        self.send_queue.put(str(text) + "\r\n", True)


    def queue(self, text, dest):
        """Generic queuing interface. This will be called directly by modules"""
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



interfaces = {}
interface_instances = {}

#: Shared queue for incoming messages
recv_queue = queue.Queue()

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
        interface_instances[name] = interfaces[interface](id=name, config=config[instance])
