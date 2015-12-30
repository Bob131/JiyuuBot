// override GLib.message
void message(string text, void* _) {
    stdout.printf(@"** $(text)\n");
}


namespace JiyuuBot {
    // some helpers
    namespace Misc {
        // use with libsoup, requests etc.
        public const string UA = "JiyuuBot (http://github.com/Bob131/JiyuuBot-ng; bob@bob131.so) ";

        public string get_gitrev() {
            return git_rev;
        }

        [Compact]
        public class SaneDoc : Html.Doc {
            public static SaneDoc* read_doc(string cur) {
                return (SaneDoc) Html.Doc.read_doc(cur, "", null,
                    Html.ParserOption.RECOVER|Html.ParserOption.NOERROR|Html.ParserOption.NOWARNING);
            }

            public Xml.Node*[] find_all(string xpath) {
                var context = new Xml.XPath.Context(this);
                var obj = context.eval(xpath);
                Xml.Node*[] nodes = {};
                for (var i = 0; i < obj->nodesetval->length(); i++) {
                    nodes += obj->nodesetval->item(i);
                }
                return nodes;
            }
        }

        namespace CssToXPath {
            public string class(string cls) {
                return @"//*[contains(concat(\" \", @class, \" \"), \" $cls \")]";
            }

            public string tag(string t) {
                return @"//$t";
            }
        }
    }


    namespace Prpl {
        public string get_version() {
            return Purple.Core.get_version();
        }

        public class Context : Object {
            public unowned Purple.Conversation conv {construct; private get;}

            public string protocol {get {
                return this.conv.get_account().get_protocol_name();
            }}
            public string username {get {
                return this.conv.get_account().get_username();
            }}
            public string display_name {get {
                return this.conv.get_gc().get_display_name();
            }}
            public string chat {get {
                return this.conv.get_name();
            }}

            public Context(Purple.Conversation conv) {
                Object(conv: conv);
            }
        }

        public class Message : Object {
            public string sender {construct; get;}
            public string raw_text {construct; get;}
            public string text {private set; get;}
            public bool at_us {private set; get;}
            public Context context {construct; get;}

            private unowned Purple.Conversation conv;

            public Message(string sender, string ptext, string raw, Purple.Conversation conv) {
                Object(sender: sender, raw_text: raw, context: new Context(conv));
                this.conv = conv;

                text = ptext.dup();
                var texts = Regex.split_simple(@"^$(context.display_name)[:,\\s]", text, RegexCompileFlags.CASELESS);
                if (texts.length > 1) {
                    texts = texts[1:texts.length];
                    text = string.joinv(context.display_name, texts).strip();
                    at_us = true;
                }

                string log;
                if (sender == "")
                    log = @"$(context.chat): $(text)";
                else
                    log = @"$(sender): $(text)";
                message(log, null);
            }


            public void send(owned string new_message) {
                Idle.add(() => {
                    message(@">$(context.chat): $(new_message)", null);
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

            public static bool same_context(Message a, Message b) {
                return a.context.protocol == b.context.protocol &&
                    a.context.username == b.context.username &&
                    a.context.display_name == b.context.display_name &&
                    a.context.chat == b.context.chat;
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

        public interface HelpInfoRegistrar : Object {
            public abstract void add(string command, string help_info);
        }

        public abstract class BasePlugin : Object {
            public Soup.Session session {construct; protected get;}
            public HelpInfoRegistrar help {construct; protected get;}
            public Config.PluginConfig config {construct; protected get;}

            // runs on plugin load; optional
            public virtual void activate() {}
            // test whether plugin should exec
            // true to call exec, false to do otherwise
            public abstract bool should_exec(Prpl.Message msg);
            // plugin run
            public abstract void exec(Prpl.Message msg);
        }
    }
}
