from configman import *

class PermsMan:
    def __init__(self, glob_confman):
        self.confman = ConfigMan("perms")
        self.glob_confman = glob_confman

    def set_cmd_perms(self, cmd, value):
        value = int(value)
        if value < 0 or value > 999:
            raise Exception("Permissions level must be an integer between 0 and 999")
        self.confman.setv("command", cmd, value)

    def set_host_perms(self, host, value):
        value = int(value)
        if value < 0 or value > 999:
            raise Exception("Permissions level must be an integer between 0 and 999")
        self.confman.setv("host", host, value)

    def set_msg_perms(self, host, value):
        if not type(value) == bool:
            value = (value == 1 or value == "1" or value.lower() == "true")
        self.confman.setv("msg", host, value)

    def suggest_cmd_perms(self, command, level):
        # if auth level not set
        if self.confman.get("command", command, None, False) == None:
            self.set_cmd_perms(command, level)

    def get_perms(self, host, command):
        if host == None:
            return True
        else:
            userlvl = self.get_host_perms(host)
            cmdlvl = self.get_cmd_perms(command)
            if userlvl >= cmdlvl:
                return True
            else:
                return False

    def get_msg_perms(self, host):
        return self.confman.get("msg", host, False, False)

    def get_cmd_perms(self, command):
        return self.confman.get("command", command, self.glob_confman.get("PERMS", "CMD_DEFAULT", 100), False)

    def get_host_perms(self, host):
        return self.confman.get("host", host, self.glob_confman.get("PERMS", "HOST_DEFAULT", 100), False)
