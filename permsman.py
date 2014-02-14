from configman import *

class PermsMan:
    def __init__(self):
        self.confman = ConfigMan("perms")

    def set_cmd_perms(self, cmd, value):
        value = int(value)
        if value < 0 or value > 999:
            raise Exception("Permissions level must be an integer between 0 and 999")
        self.confman.set_value("command", cmd, value)

    def set_nick_perms(self, nick, value):
        value = int(value)
        if value < 0 or value > 999:
            raise Exception("Permissions level must be an integer between 0 and 999")
        self.confman.set_value("nick", nick, value)

    def set_msg_perms(self, nick, value):
        if not type(value) == bool:
            value = (value == 1 or value == "1" or value.lower() == "true")
        self.confman.set_value("msg", nick, value)

    def suggest_cmd_perms(self, command, level):
        # if auth level not set
        if self.confman.get_value("command", command, None, False) == None:
            self.set_cmd_perms(command, level)

    def get_perms(self, nick, command):
        userlvl = self.get_nick_perms(nick)
        cmdlvl = self.get_cmd_perms(command)
        if userlvl >= cmdlvl:
            return True
        else:
            return False

    def get_msg_perms(self, nick):
        return self.confman.get_value("msg", nick, False, False)

    def get_cmd_perms(self, command):
        return self.confman.get_value("command", command, 100, False)

    def get_nick_perms(self, nick):
        return self.confman.get_value("nick", nick, 100, False)
