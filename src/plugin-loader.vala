namespace JiyuuBot {
    namespace Plugins {
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
