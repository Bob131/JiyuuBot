namespace JiyuuBot {
    namespace Plugins {
        private class ModuleWrapper : Object {
            public Module module;

            public ModuleWrapper(owned Module module) {
                this.module = (owned) module;
            }
        }

        public class Manager : Object {
            private BasePlugin[] extensions_store;
            private ModuleWrapper[] c_modules;
            private Config.PluginConfigStore configs;
            private bool deinit_python = false;

            private FileMonitor plugins_monitor;
            private Python.Object python_loader;

            private FinalURLHandler url_handler;

            public virtual signal void incoming_message(Prpl.Message msg) {
                int execed = 0;
                foreach (var ext in extensions_store) {
                    if (ext.should_exec(msg)) {
                        ext.exec(msg);
                        execed++;
                    }
                }
                if (execed == 0 && url_handler.should_exec(msg))
                    url_handler.exec(msg);
            }

            private void load_plugins() {
                var plugin_path = Path.build_filename(root_dir, "plugins");
                assert(FileUtils.test(plugin_path, FileTest.EXISTS) &&
                    FileUtils.test(plugin_path, FileTest.IS_DIR));

                extensions_store = {};
                c_modules = {};

                var loaded = 0;
                var failed_to_load = 0;
                Posix.Glob paths = {};

                // load Python plugins
                var wrapped_type = PyGObject.type_wrapper_new(typeof(BasePlugin));
                paths.glob(Path.build_filename(plugin_path, "*.py"));
                foreach (var path in paths.pathv) {
                    path = Path.get_basename(path).replace(".py", "");
                    var success = python_loader.call_method("load", "ss", plugin_path, path);
                    if (success.is_true())
                        loaded++;
                    else
                        failed_to_load++;
                }

                var init_types = (Python.List) python_loader.call_method("get_types", "O", wrapped_type);
                for (var i = 0; i < init_types.length; i++) {
                    var type = PyGObject.type_from_object(init_types[i]);
                    i++;
                    var name = ((Python.String) init_types[i]).to_string();
                    var instance = (BasePlugin) Object.new(type);
                    extensions_store += instance;
                    instance.activate(configs.get_group(name));
                }

                // load C plugins
                var can_load = true;
                if (Module.supported() == false) {
                    message("Error loading modules: Dynamic modules are not supported on this system");
                    can_load = false;
                }
                paths.glob(Path.build_filename(plugin_path, "*.la"));
                foreach (var path in paths.pathv) {
                    failed_to_load++;
                    if (!can_load)
                        continue;
                    var base_name = Path.get_basename(path);
                    var module_wrapper = new ModuleWrapper(Module.open(path, ModuleFlags.BIND_LAZY));
                    c_modules += module_wrapper;
                    unowned Module module = module_wrapper.module;
                    if (module == null) {
                        var error = Module.error().split(": ")[1];
                        message(@"Error loading $base_name: $error");
                        continue;
                    }
                    void* register;
                    module.symbol("register_plugin", out register);
                    if (register == null) {
                        message(@"Error loading $base_name: symbol register_plugin() not found");
                        continue;
                    }
                    RegisterPlugin func = (RegisterPlugin) register;
                    var types = func();
                    var success = true;
                    foreach (var type in types) {
                        if (!type.is_a(typeof(BasePlugin))) {
                            message(@"Error loading $base_name: Type '$(type.name())' does not derive from BasePlugin");
                            success = false;
                            break;
                        }
                        var instance = (BasePlugin) Object.new(type);
                        extensions_store += instance;
                        instance.activate(configs.get_group(base_name.replace(".la", "")));
                    }
                    if (!success)
                        continue;
                    failed_to_load--;
                    loaded++;
                }

                string loaded_plugins_msg = @"Successfully loaded $(loaded) plugin";
                if (loaded != 1)
                    loaded_plugins_msg += "s";
                if (failed_to_load > 0) {
                    loaded_plugins_msg += @"; $(failed_to_load) plugin";
                    if (failed_to_load != 1)
                        loaded_plugins_msg += "s";
                    loaded_plugins_msg += " failed";
                }
                message(loaded_plugins_msg, null);
            }

            public Manager() {
                Object();

                var gi_path = Path.build_filename(root_dir, "src");
                Environment.set_variable("GI_TYPELIB_PATH", gi_path, true);
                Environment.set_variable("LD_LIBRARY_PATH", gi_path, true);

                var plugin_path = Path.build_filename(root_dir, "plugins");
                var plugin_path_file = File.new_for_path(plugin_path);

                configs = new Config.PluginConfigStore();

                url_handler = new FinalURLHandler();

                if (!Python.is_initialized()) {
                    Python.initialize_ex(false);
                    deinit_python = true;
                }

                PyGObject.init();

                PyGObject.enable_threads();
                Python.init_threads();

                var loader_module = new Python.Module("jiyuubot-plugin-loader");
                loader_module.add_string_constant("__file__", "plugin-loader.py");
                loader_module.add_object("__builtins__", new Python.Import("builtins"));

                var code = Python.Code.from_file(Path.build_filename(gi_path, "plugin-loader.py"));
                var dict = loader_module.get_dict();
                code.eval(dict, dict);
                python_loader = loader_module.get_dict().get_item_string("loader");

                load_plugins();

                plugins_monitor = plugin_path_file.monitor_directory(FileMonitorFlags.NONE);
                plugins_monitor.changed.connect((file, _, ev) => {
                    if (file.get_path().has_suffix(".py") || file.get_path().has_suffix(".la"))
                        if (ev == FileMonitorEvent.CHANGES_DONE_HINT)
                            load_plugins();
                });
            }

            ~Manager() {
                extensions_store = null;
                python_loader = null;
                if (deinit_python)
                    Python.finalize();
            }
        }
    }
}
