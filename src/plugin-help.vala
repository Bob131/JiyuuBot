namespace JiyuuBot {
    namespace Plugins {
        private class Help : BasePlugin, HelpInfoRegistrar {
            private Gee.HashMap<string, string> infos;

            public override bool should_exec(Prpl.Message msg) {
                return msg.command("help");
            }

            public override void exec(Prpl.Message msg) {
                var args = msg.get_args();
                if (args.length > 0) {
                    foreach (var cmd in args) {
                        cmd = cmd.replace(".", "").strip();
                        if (infos.has_key(cmd))
                            msg.send(@".$cmd - $(infos[cmd])");
                        else
                            msg.send(@"Command '$cmd' unknown");
                    }
                } else
                    msg.send("Available commands: %s".printf(string.joinv(" ", infos.keys.to_array())));
            }

            public void add(string command, string help_info) {
                assert (!infos.has_key(command));
                infos[command] = help_info;
            }

            construct {
                infos = new Gee.HashMap<string, string>();
            }
        }
    }
}
