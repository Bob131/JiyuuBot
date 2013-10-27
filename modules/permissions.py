#Define Permissions Manager
def accesslvl(self, command, nick)
    auth = int(self.confman.get_value("permissions", nick))
    authreq = int(self.confman.get_value("command_levels", command))
    if not auth:
        auth = 100
    if not authreq:
        authreq = 100
    if auth >= authreq:
        return True
    elif auth < authreq:
       return False
def addAccess(self, nick, level=100)
    self.confman.set_value("permissions", nick, str(level))
def rmAccess(self, nick)
    self.confman.set_value("permissions", nick, "0")
def cmdLevel(self, command, level)
    self.confman.set_value("command_levels", command, str(level))
def access(self, arg, nick, level="100")
    if arg == "add":
        self.addAccess(nick, level)
    elif arg == "rm":
        self.rmAccess(nick)
    else:
        return "Invalid sub-command"


self.accesslvl = accesslvl
self.rmAccess = rmAccess
self.addAccess = addAccess
self.map_command("access", access)
self.map_command("commandlevel", cmdLevel)
self.map_help("access", ".access: add - adds a user with specified access level. rm - sets specified user's access to 0")
self.map_help("commandlevel", ".commandlevel - sets specified command's required auth level")
