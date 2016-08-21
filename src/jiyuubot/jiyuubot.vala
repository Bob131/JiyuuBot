extern const string VERSION;

class JiyuuBot.App : Application {
    string config_path = "";
    bool list_proto = false;
    string? qconfig;
    bool print_version = false;

    KeyFile config;

#if !TEST
    Handler handler;
    AccountManager account_manager;
#endif

    void load_config() {
        config = new KeyFile();
        try {
            config.load_from_file(config_path, 0);
        } catch (Error e) {
            fatal("Failed to load config: %s", e.message);
        }
    }

    protected override void shutdown() {
#if !TEST
        var disconnected = false;
        account_manager.tear_down_accounts.begin(() => {disconnected = true;});
        while (!disconnected)
            MainContext.default().iteration(true);
#endif

        base.shutdown();
    }

    protected override void activate() {
        this.hold();

        SourceFunc signal_callback = () => {
            this.quit();
            return Source.REMOVE;
        };
        Unix.signal_add(ProcessSignal.INT, (owned) signal_callback);
        Unix.signal_add(ProcessSignal.TERM, (owned) signal_callback);

        // TODO: implement config-finding logic
        if (config_path == "")
            fatal("Config file path required");

        load_config();

#if !TEST
        handler = new Handler();
        Bus.own_name(BusType.SESSION, @"$(Tp.CLIENT).JiyuuBot.Handler", 0,
            null, (connection, name) => {
                try {
                    connection.register_object<Tp.Client>(
                        Tp.path_from_name(name), new Handler.Client());
                    connection.register_object<Tp.Handler>(
                        Tp.path_from_name(name), handler);
                } catch (Error e) {
                    fatal("Failed to register handler: %s", e.message);
                }
            });

        account_manager = new AccountManager(config);
        account_manager.create_accounts.begin();
#endif
    }

    protected override int handle_local_options(VariantDict _) {
        if (list_proto) {
            debug("Probing for available protocols...");
            this.hold();
            Tp.list_connection_managers.begin((obj, res) => {
                Tp.ConnectionManager[] managers;
                try {
                    managers = Tp.list_connection_managers.end(res);
                } catch (Error e) {
                    fatal("DBus probing failed: %s", e.message);
                }
                foreach (var manager in managers) {
                    stdout.printf("%s:\n", manager.get_cm_name());
                    this.hold();
                    manager.list_protocols.begin((obj, res) => {
                        string[] protocols = {};
                        try {
                            manager.list_protocols.end(res);
                        } catch (IOError e) {
                            fatal("Failed to fetch protocol list: %s",
                                e.message);
                        }
                        foreach (var protocol in protocols)
                            stdout.printf("  %s\n", protocol);
                        this.release();
                    });
                }
                this.release();
            });
            return 0;
        }

        if (qconfig != null) {
            var query_config = (!) qconfig;

            if (!query_config.contains(":")) {
                stderr.printf("Protocol must be in the format %s\n",
                    "connection-manager:protocol. Use -l to list protocols");
                return 1;
            }

            var input = query_config.split(":");
            var connman_name = input[0];
            var proto_name = input[1];

            Tp.ConnectionManager? connman = null;
            Tp.ConnectionManager.get_manager.begin(connman_name, (obj, res) => {
                try {
                    connman = Tp.ConnectionManager.get_manager.end(res);
                } catch (Error e) {
                    stderr.printf("Failed to obtain %s: %s\n",
                        "connection manager reference", e.message);
                    Process.exit(1);
                }
            });

            var mc = MainContext.default();
            while (connman == null)
                mc.iteration(true);

            Tp.ProtocolParameter[]? @params = null;
            ((!) connman).get_parameters.begin(proto_name, (obj, res) => {
                try {
                    @params = ((!) connman).get_parameters.end(res);
                } catch (Error e) {
                    stderr.printf("Failed to get protocol %s '%s': %s\n",
                        "parameters for", proto_name, e.message);
                    Process.exit(1);
                }
            });

            while (@params == null)
                mc.iteration(true);

            if (@params.length > 0)
                foreach (var param in @params) {
                    stdout.printf("%s\n", param.name);
                    stdout.printf("  Type:     %s\n", param.signature);
                    stdout.printf("  Required: %s\n",
                        (Tp.ProtocolParameterFlags.REQUIRED in param.flags).to_string());

                    if (Tp.ProtocolParameterFlags.HAS_DEFAULT in param.flags)
                        stdout.printf("  Default:  %s\n",
                            param.default_value.print(false));
                }
            else
                stderr.printf("No parameters for this protocol\n");

            return 0;
        }

        if (print_version) {
            stdout.printf("jiyuubot %s\n", VERSION);
            return 0;
        }

        return -1;
    }

    public App() {
        Object(application_id: "so.bob131.JiyuuBot");

        var options = new OptionEntry[5];
        options[0] = {"config", 'c', 0, OptionArg.FILENAME, ref config_path,
                        "Path to configuration file", "path"};
        options[1] = {"list-protocols", 'l', 0, OptionArg.NONE, ref list_proto,
                        "List available protocols", null};
        options[2] = {"query-config", 'q', 0, OptionArg.STRING, ref qconfig,
                        "List config options for connection-manager:protocol",
                        null};
        options[3] = {"version", 0, 0, OptionArg.NONE, ref print_version,
                        "Print version"};
        options[4] = {(string) null};
        this.add_main_option_entries(options);
    }

#if !TEST
    public static int main(string[] args) {
        return new App().run(args);
    }
#endif
}
