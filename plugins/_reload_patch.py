import gc
import importlib


class ExtensionCacheWrapper(dict):
    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

class ModuleDictWrapper:
    actual_dict = {}

    def __getitem__(self, key):
        if key in self.actual_dict:
            self.extension_cache[self.actual_dict[key]] = {}
            mod = importlib.reload(self.actual_dict[key])
            self.actual_dict[key] = mod
            self.extension_cache[mod] = {}
            return mod
        raise KeyError

    def __setitem__(self, key, item):
        self.actual_dict[key] = item

    def __init__(self, orig_dict, ext_cache):
        self.actual_dict = orig_dict
        self.extension_cache = ext_cache


for obj in gc.get_objects():
    if obj.__class__.__name__ == "Hooks":
        # we've got libpeas' internal Python class!
        if not obj._Hooks__module_cache.__class__ == ModuleDictWrapper:
            print("** Patching libpeas...")
            wrapper = ExtensionCacheWrapper()
            obj._Hooks__extension_cache = wrapper
            obj._Hooks__module_cache = ModuleDictWrapper(obj._Hooks__module_cache, wrapper)
