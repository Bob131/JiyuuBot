import os

class ConfigMan:
    def __init__(self, conftype):
        if conftype == "module" or conftype == "service" or conftype == "perms":
            self.configpath = os.path.join(os.path.dirname(__file__), "configs" + os.sep + conftype)
        else:
            raise Exception("Invalid config type")

    def get_value(self, modname, valname, default="", writeDefault=True):
        try:
            config = open("%s%s%s.py" % (self.configpath, os.sep, modname), "r")
            value = ""
            for line in config.read().split("\n"):
                if line.startswith("%s = " % valname):
                    value = line
                    break
            if not value == "":
                return value[value.index("=")+1:]
            else:
                raise Exception
        except:
            if writeDefault:
                self.set_value(modname, valname, default)
            return default

    def set_value(self, modname, valname, value):
        newconfig = ""
        try:
            config = open("%s%s%s.py" % (self.configpath, os.sep, modname), "r")
            for line in config.read().split("\n"):
                if not line.startswith("%s = " % valname):
                    newconfig += line + "\n"
            config.close()
        except:
            pass
        config = open("%s%s%s.py" % (self.configpath, os.sep, modname), "w")
        newconfig += "%s = %s\n" % (valname, value)
        config.write(newconfig)
        config.flush()
        config.close()
