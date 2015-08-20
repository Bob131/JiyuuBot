#!/usr/bin/env python3

import os
import time
import traceback
import importlib
import threading
from contextlib import contextmanager

import watchdog.events
import watchdog.observers


#initialize plugin manager and load plugins
interfaces = importlib.import_module("interfaces")
interfaces.main()
plugman = importlib.import_module("modules")
plugman.setup(interfaces.interface_instances)


class ModuleReloader(watchdog.events.FileSystemEventHandler):
    """
        Reload modules after FS changes to modules subdirectory.

        Employs two synchronisation strategies:
            1. Prevent more than one FS event being processed at a time
               (eg if many files are being changed via git pull)
            2. Halt message processing for the duration of the reload
    """

    @contextmanager
    def acquire_lock(self, *args, **kwargs):
        def release():
            # wait an arbitrary amount of time to achieve the effect of
            # ignoring semi-simultaneous changes
            time.sleep(2)
            self.lock.release()
        success = self.lock.acquire(*args, **kwargs)
        yield success
        if success:
            t = threading.Thread(target=release)
            t.daemon = 1
            t.start()

    def __init__(self, *args, **kwargs):
        self.lock = threading.Lock()
        super().__init__(*args, **kwargs)

    def dispatch(self, event):
        if ("modules/" in event.src_path and \
                event.src_path.endswith(".py")) or event.is_directory:
            super().dispatch(event)

    def on_any_event(self, _):
        with self.acquire_lock(False) as success:
            if not success:
                return
            with plugman.threadman.lock:
                importlib.reload(plugman)
                plugman.setup(interfaces.interface_instances)


observer = watchdog.observers.Observer()
observer.schedule(ModuleReloader(), os.path.dirname(plugman.__file__), \
        recursive=True)
observer.start()

#Main active loop
while 1:
    try:
        # receive and format line for parsing
        msg = interfaces.recv_queue.get(True)
        with plugman.threadman.lock:
            plugman.threadman(msg.copy())
    except Exception as e:
        if not type(e) == InterruptedError:
            traceback.print_exc()
        else:
            observer.stop()
            observer.join()
