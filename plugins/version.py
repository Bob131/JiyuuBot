import gi
from gi.repository import GObject
gi.require_version('JiyuuBot', '1.0')
from gi.repository import JiyuuBot


class version(JiyuuBot.PluginsBasePlugin):
    def do_activate(self, help, _):
        help.add('version', 'show what commit hash the JiyuuBot core was built from')

    def do_should_exec(self, msg):
        return msg.command('version') or msg.regex("CTCP 'VERSION'", False)

    def do_exec(self, msg):
        tosend = "Commit hash: {} (libpurple v{})".format(JiyuuBot.misc_get_gitrev(), JiyuuBot.prpl_get_version())
        tosend += " - http://github.com/Bob131/JiyuuBot-ng"
        msg.send(tosend)
