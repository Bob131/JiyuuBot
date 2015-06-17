import queue
import glob
import os
import threading
import configparser
import traceback


class BaseInterface:
    MANDATORY_OPTIONS = []

    def __init__(self, id, config, recv_queue):
        self.id = id
        self.config = config
        self.recv_queue = recv_queue
        self.send_queue = queue.Queue()

        self.validate_config()
        self.init_hooks()

        for target in [self.recv, self.send]:
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()


    def validate_config(self):
        for option in self.MANDATORY_OPTIONS:
            if not option in self.config:
                raise Exception("Mandatory option missing in config for '{}': {}".format(self.id, option))


    def print(self, text):
        print("{} !!! {}".format(self.id, text))


    def queue_raw(self, text):
        self.send_queue.put(str(text) + "\r\n", True)


    # easy queue interface
    def queue(self, text, dest):
        pass


    # setup sockets and whatnot
    def init_hooks(self):
        pass


    # read from socket write to self.recv_queue
    def recv(self):
        pass


    # read from self.send_queue and write to socket
    def send(self):
        pass



interfaces = {}
interface_instances = {}


def register(cls):
    if cls.__name__ in interfaces:
        raise Exception("Interface with this name already loaded: {}".format(cls.__name__))
    interfaces[cls.__name__] = cls


modules = glob.glob(os.path.dirname(__file__)+"/*.py")
__all__ = [os.path.basename(f)[:-3] for f in modules]
from . import *

recv_queue = queue.Queue()

config = configparser.ConfigParser()
config.read("{}/../configs/interfaces.ini".format(os.path.dirname(__file__)))

if len(config.sections()) == 0:
    raise Exception("No interfaces configured")

for instance in config.sections():
    interface, name = instance.split(":")
    if name in interface_instances:
        raise Exception("Cannot have more than one interface of the same name: {}".format(name))
    interface_instances[name] = interfaces[interface](id=name, config=config[instance], recv_queue=recv_queue)
