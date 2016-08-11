extern const string VERSION;

class JiyuuBot.App : Application {
    string config_path = "";
    bool list_proto = false;
    string? qconfig;
    bool print_version = false;

    KeyFile config;
#if !TEST
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
        account_manager = new AccountManager(config);
        account_manager.create_accounts.begin();
#endif
    }

    protected override int handle_local_options(VariantDict _) {
        if (list_proto) {
            debug("Probing for available protocols...");
            this.hold();
            TelepathyGLib.list_connection_managers_async.begin(null,
                (obj, res) => {
                    List<TelepathyGLib.ConnectionManager> managers;
                    try {
                        managers = TelepathyGLib.list_connection_managers_async
                            .end(res);
                    } catch (GLib.Error e) {
                        fatal("DBus probing failed: %s", e.message);
                    }
                    foreach (var manager in managers) {
                        stdout.printf("%s:\n", manager.cm_name);
                        foreach (var protocol in manager.dup_protocol_names())
                            stdout.printf("  %s\n", protocol);
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

            TelepathyGLib.ConnectionManager connman;
            try {
                connman = new TelepathyGLib.ConnectionManager(
                    TelepathyGLib.DBusDaemon.dup(), connman_name, null);

                var prepared = false;
                connman.prepare_async.begin(null, () => {prepared = true;});

                var mc = MainContext.default();
                while (!prepared)
                    mc.iteration(true);
            } catch (Error e) {
                stderr.printf("Failed to obtain connection %s: %s\n",
                    "manager reference", e.message);
                return 1;
            }

            if (connman.info_source == TelepathyGLib.CMInfoSource.NONE) {
                stderr.printf("Unknown connection manager '%s'. Use -l to %s\n",
                    connman_name, "list protocols");
                return 1;
            }

            if (!connman.has_protocol(proto_name)) {
                stderr.printf("Unknown protocol '%s'. Use -l to list %s\n",
                    proto_name, "protocols");
                return 1;
            }

            var @params = connman.get_protocol_object(proto_name).dup_params();
            var printed = false;

            foreach (var param in @params) {
                // I don't know what this means, but it's probably a good idea
                // to respect it
                if (param.is_secret())
                    continue;

                printed = true;

                stdout.printf("%s\n", param.get_name());
                stdout.printf("  Type:     %s\n",
                    param.dup_variant_type().dup_string());
                stdout.printf("  Required: %s\n",
                    param.is_required().to_string());

                Variant? default = param.dup_default_variant();
                if (default != null)
                    stdout.printf("  Default:  %s\n",
                        ((!) default).print(false));
            }

            if (!printed)
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
