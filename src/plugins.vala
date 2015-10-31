namespace JiyuuBot {
    namespace Plugins {
        private class FinalURLHandler : Object, BasePlugin {
            private const string regex = "\\b(https?://[^\\s]+)\\b";

            public void activate(Config.PluginConfig _) {}

            public bool should_exec(Prpl.Message msg) {
                return msg.regex(regex);
            }

            private string readable_size(double size) {
                string[] units = {"B", "kiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"};
                var i = 0;
                while (size > 1024 && i < units.length) {
                    size /= 1024;
                    i++;
                }
                return ", %.*f %s".printf(i, size, units[i]);
            }

            private string? headers_to_readable(Soup.MessageHeaders headers, out double length) {
                var readable = "";
                if (headers.get_one("content-type") == null)
                    return null;
                readable += headers.get_one("content-type");
                readable = /;\s*/.split(readable)[0];
                if (!double.try_parse(headers.get_one("content-length") ?? "not a double", out length))
                    return readable;
                readable += readable_size(length);
                return readable;
            }

            public void exec(Prpl.Message msg) {
                var session = new Soup.Session();
                var rx = new Regex(regex, RegexCompileFlags.CASELESS);
                MatchInfo mi;
                rx.match(msg.text, 0, out mi);
                do {
                    var url = mi.fetch(0);
                    var message = new Soup.Message("HEAD", url);
                    session.send_message(message);
                    if (message.status_code == 200) {
                        double? length;
                        var readable = headers_to_readable(message.response_headers, out length);
                        if (readable == null)
                            continue;
                        if ((message.response_headers.get_one("content-type") ?? "not html") == "text/html" &&
                                (length ?? 999999999) < 1048576) {
                            message = new Soup.Message("GET", url);
                            session.send_message(message);
                            var text = (string) message.response_body.flatten().data;
                            // anger the regex gods
                            MatchInfo title_stuff;
                            var _ = /(?<=\<title\>).*?(?=\<.title\>)/i.match(text, 0, out title_stuff);
                            var title = title_stuff.fetch(0);
                            if (title != null)
                                readable = @"$(title) [$(readable)]";
                        }
                        msg.send(readable);
                    }
                } while (mi.next());
            }
        }


        public class Manager : Object {
            private Peas.Engine engine;
            private BasePlugin[] extensions_store;
            private Config.PluginConfigStore configs;

            private FileMonitor plugins_monitor;
            private Python.Code code;

            private FinalURLHandler url_handler;

            private void thread_kickoff(BasePlugin ext, Prpl.Message msg) {
                ThreadFunc<void*> t = () => {
                    ext.exec(msg);
                    return null;
                };
                new Thread<void*>(null, t);
            }

            public virtual signal void incoming_message(Prpl.Message msg) {
                int execed = 0;
                foreach (var ext in extensions_store) {
                    if (ext.should_exec(msg)) {
                        thread_kickoff(ext, msg);
                        execed++;
                    }
                }
                if (execed == 0 && url_handler.should_exec(msg))
                    thread_kickoff(url_handler, msg);
            }

            private void load_plugins() {
                var plugin_path = Path.build_filename(root_dir, "plugins");
                assert(FileUtils.test(plugin_path, FileTest.EXISTS) &&
                    FileUtils.test(plugin_path, FileTest.IS_DIR));

                extensions_store = {};

                engine.set_loaded_plugins(null);
                engine.rescan_plugins();

                var extensions = new Peas.ExtensionSet(engine, typeof(BasePlugin));
                extensions.extension_added.connect((info, ext) => {
                    var typed_ext = (BasePlugin) ext;
                    extensions_store += typed_ext;
                    typed_ext.activate(configs.get_group(info.get_name()));
                });

                var loaded = 0;
                var failed_to_load = 0;
                foreach (var plugin in engine.get_plugin_list()) {
                    if (engine.try_load_plugin(plugin))
                        loaded++;
                    else
                        failed_to_load++;
                }

                string loaded_plugins_msg = @"Successfully loaded $(loaded) plugins";
                if (failed_to_load > 0)
                    loaded_plugins_msg += @"; $(failed_to_load) modules plugins";
                message(loaded_plugins_msg, null);
            }

            public Manager() {
                Object();

                var gi_path = Path.build_filename(root_dir, "src");
                Environment.set_variable("GI_TYPELIB_PATH", gi_path, true);
                Environment.set_variable("LD_LIBRARY_PATH", gi_path, true);

                var plugin_path = Path.build_filename(root_dir, "plugins");
                var plugin_path_file = File.new_for_path(plugin_path);

                engine = new Peas.Engine();
                engine.add_search_path(plugin_path, null);
                engine.enable_loader("python3");

                configs = new Config.PluginConfigStore();

                url_handler = new FinalURLHandler();

                load_plugins();

                var state = Python.GIL.lock();

                var patch = new Python.Module("libpeas-internal-patch");
                patch.add_string_constant("__file__", "_reload_patch.py");
                patch.add_object("__builtins__", new Python.Import("builtins"));

                code = Python.Code.from_file(Path.build_filename(plugin_path, "_reload_patch.py"));
                var dict = patch.get_dict();
                code.eval(dict, dict);

                Python.GIL.release(state);

                plugins_monitor = plugin_path_file.monitor_directory(FileMonitorFlags.NONE);
                plugins_monitor.changed.connect((file, _, ev) => {
                    if (file.get_path().has_suffix(".py") || file.get_path().has_suffix(".plugin"))
                        if (ev == FileMonitorEvent.CHANGES_DONE_HINT)
                            load_plugins();
                });
            }
        }
    }
}
