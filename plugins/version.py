import gi
from gi.repository import GObject
gi.require_version('JiyuuBot', '1.0')
from gi.repository import JiyuuBot


class version(JiyuuBot.PluginsBasePlugin):
    def do_should_exec(self, msg):
        return msg.command('version') or msg.regex("CTCP 'VERSION'", False)

    def do_exec(self, msg):
        tosend = "Commit hash: {} (libpurple v{})".format(JiyuuBot.get_gitrev(), JiyuuBot.prpl_get_version())
        tosend += " - http://github.com/Bob131/JiyuuBot-ng"
        msg.send(tosend)
