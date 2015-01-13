import queue
import glob
import traceback
import pkgutil


class ConnectionMan:
    def __init__(self, global_confman, permsman):
        self.queue = queue.Queue()

        self.instances = {}

        # load backends
        for _, backend, _ in pkgutil.iter_modules(path=['backends/']):
            print("Initialising backend {}".format(backend))
            mod = __import__("backends."+backend, fromlist=[backend])
            c = getattr(mod, backend)
            try:
                self.instances[backend] = c(global_confman, self, permsman)
            except:
                traceback.print_exc()
                print("Loading {} failed".format(backend))

    def read(self):
        return self.queue.get(True)

    def gen_send(self, *args, **kwargs):
        self.write(*args, **kwargs)

    def privmsg(self, text):
        self.instances["irc"].privmsg(text)

    def broadcast(self, string):
        for backend in self.instances.keys():
            self.instances[backend].broadcast(string)

    def write(self, string, data):
        data = data.copy()
        self.instances[(data.get("backend", None) or "irc")].write(string, data)
