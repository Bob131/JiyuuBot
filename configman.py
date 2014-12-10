import os
import json
import threading


class ConfigMan:
    def __init__(self, conftype):
        self.configpath = os.path.join(os.path.dirname(__file__), "configs" + os.sep + conftype + ".json")
        self.lock = threading.Lock()
        self.load(True)
        # if global.json, ensure the required values are present
        if conftype == "global":
            try:
                _ = self.values["IRC"]["HOST"]
                _ = self.values["IRC"]["HOME_CHANNEL"]
                _ = self.values["IRC"]["NICK"]
                _ = self.values["IRC"]["BUFFER_SIZE"]

                _ = self.values["MPD"]["ENABLED"]
                if _ == True:
                    _ = self.values["MPD"]["HOST"]
                    _ = self.values["MPD"]["PORT"]
            except KeyError:
                raise Exception("configs/global.json missing values. See configs/global.json.example for help")


    def get(self, modname, valname, default="", writeDefault=True, allowTemp=True):
        self.load()
        if allowTemp and modname in self.tvalues and valname in self.tvalues[modname]:
            return self.tvalues[modname][valname]
        elif modname in self.values and valname in self.values[modname]:
            return self.values[modname][valname]
        else:
            if writeDefault:
                self.setv(modname, valname, default)
            return default


    def setv(self, modname, valname, value, temp=False):
        if temp:
            self.lock.acquire()
            if modname not in self.tvalues:
                self.tvalues[modname] = {}
            self.tvalues[modname][valname] = value
            self.lock.release()
        else:
            self.lock.acquire()
            if modname not in self.values:
                self.values[modname] = {}
            self.values[modname][valname] = value
            self.lock.release()
            self.save()


    def load(self, setTempVals=False):
        self.lock.acquire()
        try:
            config = open(self.configpath, "r")
            json_blocks = config.read()
            config.close()
            self.values = json.loads(json_blocks)
        except:
            self.values = {}
        if setTempVals:
            self.tvalues = {}
        self.lock.release()


    def save(self):
        self.lock.acquire()
        config = open(self.configpath, "w")
        config.write(json.dumps(self.values, sort_keys=True, indent=4, separators=(',', ': ')))
        config.flush()
        config.close()
        self.lock.release()
