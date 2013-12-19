import os
import json

class ConfigMan:
    def __init__(self, conftype):
        if conftype == "module" or conftype == "service" or conftype == "perms":
            self.configpath = os.path.join(os.path.dirname(__file__), "configs" + os.sep + conftype + ".json")
            self.values = {}
        else:
            raise Exception("Invalid config type")

    # def get_value(self, modname, valname, default="", writeDefault=True):
    #     try:
    #         config = open(self.configpath, "r")
    #         json_blocks = config.read()
    #         config.close()
    #         value = json.loads(json_blocks)
    #         return value[modname][valname]
    #     except:
    #         if writeDefault:
    #             self.set_value(modname, valname, default)
    #         return default

    def get_value(self, modname, valname, default="", writeDefault=True):
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

    # def set_value(self, modname, valname, value):
    #     json_blocks = ""
    #     try:
    #         config = open(self.configpath, "r")
    #         json_blocks = config.read()
    #         config.close()
    #     except:
    #         json_blocks = "{}"
    #     config = open(self.configpath, "w")
    #     json_parsed = json.loads(json_blocks)
    #     json_parsed[modname][valname] = value
    #     config.write(json.dumps(json_parsed, sort_keys=True, indent=4, separators=(',', ': ')))
    #     config.flush()
    #     config.close()
