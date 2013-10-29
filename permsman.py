

from configman import *

class PermsMan:
    def __init__(self):
        self.confman = ConfigMan("perms")

    def set_cmd_perms(self, cmd, value):
        try:
            value = int(value)
            if value < 0 or value > 999:
                raise Exception()
            self.confman.set_value("command", cmd, value)
        except:
            raise Exception("Permissions level must be an integer between 0 and 999")

    def set_nick_perms(self, nick, value):
        try:
            value = int(value)
            if value < 0 or value > 999:
                raise Exception()
            self.confman.set_value("nick", nick, value)
        except:
            raise Exception("Permissions level must be an integer between 0 and 999")

    def get_perms(self, nick, command):
        try:
            userlvl = self.get_nick_perms(nick)
            cmdlvl = self.get_cmd_perms(command)
            print userlvl
            print cmdlvl
            if userlvl >= cmdlvl:
                return True
            else:
                return False
        except:
            Exception("Permissions config files malformed: Permission values must be integers in between 0 and 999")

    def get_cmd_perms(self, command):
        return self.conman.get_value("command", command, 100, False)

    def get_nick_perms(self, nick):
        return self.conman.get_value("nick", nick, 100, False)
