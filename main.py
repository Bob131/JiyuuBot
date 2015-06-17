#!/usr/bin/env python3

import traceback
import importlib


#initialize plugin manager and load plugins
interfaces = importlib.import_module("interfaces")
plugman = importlib.import_module("modules")
plugman.setup(interfaces.interface_instances)

#Main active loop
while 1:
    try:
        # receive and format line for parsing
        msg = interfaces.recv_queue.get(True)
        plugman.threadman(msg.copy())
    except Exception as e:
        if not type(e) == InterruptedError:
            traceback.print_exc()
