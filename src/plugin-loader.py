import sys
import time
import traceback
import importlib
from gi.repository import GObject


class PluginLoader(GObject.Object):
    __gtype_name__ = "PluginLoader"

    def __init__(self):
        self.modules = {}

    def load(self, module_dir, module_name):
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)

        try:
            if module_name in self.modules and self.modules[module_name] is not None:
                importlib.reload(self.modules[module_name])
            self.modules[module_name] = importlib.import_module(module_name)
            return True
        except:
            traceback.print_exc()
            self.modules[module_name] = None
            return False

    def get_types(self, gtype):
        types = []

        for name, module in self.modules.items():
            if module is not None:
                for obj in module.__dict__.values():
                    try:
                        if GObject.type_is_a(obj.__gtype__, gtype):
                            types.append(obj)
                            types.append(name)
                    except AttributeError:
                        pass

        return types


loader = PluginLoader()
