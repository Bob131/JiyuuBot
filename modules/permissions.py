#Define Permissions Manager
def accesslvl(self, command, nick):
    auth = int(self.confman.get_value("permissions", nick, 100))
    authreq = int(self.confman.get_value("command_levels", command, 100))
    if auth >= authreq:
        return True
    elif auth < authreq:
       return False

def addAccess(self, nick, level=100):
    self.confman.set_value("permissions", nick, str(level))

def rmAccess(self, nick):
    self.confman.set_value("permissions", nick, "0")

def cmdLevel(self, command):
    command = command.split(" ")
    if not command[1].startswith("."):
        command[1] = ".%s" % command[1]
    self.confman.set_value("command_levels", command[0], str(command[1]))

def access(self, arg):
    arg = arg.split(" ")
    if arg[0] == "add":
        self.addAccess(self, arg[1], arg[2])
    elif arg == "rm":
        self.rmAccess(self, arg[1])
    else:
        return "Invalid sub-command"


self.accesslvl = accesslvl
self.rmAccess = rmAccess
self.addAccess = addAccess
self.map_command("access", access)
self.map_command("commandlevel", cmdLevel)
self.map_help("access", ".access: add - adds a user with specified access level. rm - sets specified user's access to 0")
self.map_help("commandlevel", ".commandlevel - sets specified command's required auth level")
