import os
import json

class ConfigMan:
    def __init__(self, conftype):
        self.configpath = os.path.join(os.path.dirname(__file__), "configs" + os.sep + conftype + ".json")
        self.load_values()

    def get_value(self, modname, valname, default="", writeDefault=True):
        self.load_values()
        if self.values.has_key(modname) and self.values[modname].has_key(valname):
            return self.values[modname][valname]
        else:
            if writeDefault:
                self.set_value(modname, valname, default)
            return default

    def set_value(self, modname, valname, value):
        if not self.values.has_key(modname):
            self.values[modname] = {}
        self.values[modname][valname] = value
        self.save_values()

    def load_values(self):
        try:
            config = open(self.configpath, "r")
            json_blocks = config.read()
            config.close()
            self.values = json.loads(json_blocks)
        except:
            self.values = {}

    def save_values(self):
        config = open(self.configpath, "w")
        config.write(json.dumps(self.values, sort_keys=True, indent=4, separators=(',', ': ')))
        config.flush()
        config.close()
