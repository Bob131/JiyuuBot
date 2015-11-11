// override GLib.message
void message(string text, void* _) {
    stdout.printf(@"** $(text)\n");
}


namespace JiyuuBot {
    namespace Misc {
        // use with libsoup, requests etc.
        public const string UA = "JiyuuBot (http://github.com/Bob131/JiyuuBot-ng; bob@bob131.so) ";

        public string get_gitrev() {
            return git_rev;
        }
    }


    namespace Prpl {
        public string get_version() {
            return Purple.Core.get_version();
        }

        public class Message : Object {
            public string sender {construct; get;}
            public string text {construct; get;}

            public weak Purple.Conversation conv {construct; private get;}

            public unowned string protocol {get {
                return this.conv.get_account().get_protocol_name();
            }}
            public unowned string chat {get {
                return this.conv.get_name();
            }}
            public unowned string us {get {
                return this.conv.get_gc().get_display_name();
            }}


            public Message(string sender, string text, Purple.Conversation conv) {
                Object(sender: sender, text: text, conv: conv);
            }

            construct {
                string log;
                if (sender == "")
                    log = @"$(chat): $(text)";
                else
                    log = @"$(sender): $(text)";
                message(log, null);
            }


            public void send(owned string new_message) {
                Idle.add(() => {
                    message(@"$(us): $(new_message)", null);
                    new_message = Purple.markup_escape_text(new_message, new_message.length);
                    weak Purple.ConvChat chat = conv.get_chat_data();
                    if (chat == null) {
                        weak Purple.ConvIm im = conv.get_im_data();
                        im.send(new_message);
                        return false;
                    }
                    chat.send(new_message);
                    return false;
                });
            }


            // convenience functions
            public bool regex(string regex_string, bool force = false) throws RegexError {
                var regex = new Regex(regex_string, RegexCompileFlags.CASELESS);
                if (regex.match(this.text) && (!/^\./.match(this.text) || force))
                    return true;
                return false;
            }

            public bool command(string cmd) {
                return regex(@"^\\.$(cmd)", true);
            }

            public string[] get_args() {
                var args = /\s+/.split(text);
                if (args[0].has_prefix("."))
                    args = args[1:args.length];
                return args;
            }
        }
    }


    namespace Config {
        // implements KeyFile-like API
        public class PluginConfig : Object {
            public Gee.HashMap<string, string> values {construct; private get;}

            public bool has_key(string key) {
                return this.values.has_key(key);
            }

            public string? get_value(string key) {
                if (this.has_key(key))
                    return this.values[key];
                return null;
            }

            public PluginConfig(Gee.HashMap map) {
                Object(values: map);
            }
        }
    }



    namespace Plugins {
        [CCode (has_target = false)]
        public delegate Type[] RegisterPlugin();

        public abstract class BasePlugin : Object {
            public Soup.Session session {construct; protected get;}

            // plugin setup, optional
            public virtual void activate(Config.PluginConfig config) {}
            // test whether plugin should exec
            // true to call exec, false to do otherwise
            public abstract bool should_exec(Prpl.Message msg);
            // plugin run
            public abstract void exec(Prpl.Message msg);
        }
    }
}
