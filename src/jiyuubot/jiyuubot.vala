[CCode (cname = "VERSION")]
extern const string DAEMON_VERSION;

// Don't use [NoReturn], execution should return to the mainloop for shutdown
[Diagnostics]
void fatal(string message, ...) {
    stderr.printf("** FATAL: ");
    stderr.vprintf(message, va_list());
    stderr.printf("\n");
    Process.raise(ProcessSignal.TERM);
}

class JiyuuBot.App : Application {
    string config_path = "";
    bool list_proto = false;
    string? qconfig;
    bool print_version = false;

    KeyFile config;
    TelepathyGLib.AccountManager account_manager;
    GenericSet<TelepathyGLib.Account> accounts =
        new GenericSet<TelepathyGLib.Account>(direct_hash, direct_equal);

    void load_config() {
        config = new KeyFile();
        try {
            config.load_from_file(config_path, 0);
        } catch (Error e) {
            fatal("Failed to load config: %s", e.message);
            return;
        }
    }

    async void create_accounts() {
        foreach (var display_name in config.get_groups()) {
            TelepathyGLib.AccountRequest req;

            try {
                req = new TelepathyGLib.AccountRequest(
                    account_manager,
                    config.get_string(display_name, "connection-manager"),
                    config.get_string(display_name, "protocol"),
                    display_name);

                var conman = new TelepathyGLib.ConnectionManager(
                    account_manager.dbus_daemon, req.connection_manager, null);
                yield conman.prepare_async(null);

                TelepathyGLib.Protocol? _proto =
                    conman.get_protocol_object(req.protocol);
                if (_proto == null)
                    throw new TelepathyGLib.Error.INVALID_ARGUMENT(
                        "Protocol '%s' on connection manager '%s' %s",
                        req.protocol, req.connection_manager, "doesn't exist");
                var proto = (!) _proto;

                foreach (var key in config.get_keys(display_name)) {
                    if (key == "connection-manager" || key == "protocol")
                        continue;

                    if (!proto.has_param(key))
                        throw new TelepathyGLib.Error.INVALID_ARGUMENT(
                            "Protocol '%s' does not have parameter '%s'",
                            req.protocol, key);

                    var tp_param = proto.get_param(key);
                    var variant = Variant.parse(tp_param.dup_variant_type(),
                        config.get_string(display_name, key));

                    req.set_parameter(key, variant);
                }
            } catch (Error e) {
                fatal("Couldn't set up account '%s': %s", display_name,
                    e.message);
                return;
            }

            // https://bugs.freedesktop.org/show_bug.cgi?id=97210
            if (req.connection_manager == "idle" && req.protocol == "irc") {
                var dict = new VariantDict(req.parameters);
                if (!dict.contains("fullname"))
                    req.set_parameter("fullname", "Jiyuu Bot");
                if (!dict.contains("username"))
                    req.set_parameter("username", "JiyuuBot");
            }

            req.set_enabled(true);
            req.set_connect_automatically(true);

            try {
                accounts.add(yield req.create_account_async());
            } catch (Error e) {
                fatal("Failed to create account '%s': %s", req.display_name,
                    e.message);
                return;
            }
        }

        if (accounts.length == 0)
            fatal("No accounts were set-up. Exiting");
        else
            message("Connected %u account%s!", accounts.length,
                accounts.length != 1 ? "s" : "");
    }

    async void tear_down_accounts() {
        if (accounts.length == 0)
            return;

        message("Disconnecting accounts...");

        foreach (var account in accounts.get_values())
            try {
                yield account.remove_async();
            } catch (Error e) {
                warning("Failed tear-down of account '%s': %s",
                    account.display_name, e.message);
            }
    }

    protected override void activate() {
        this.hold();

        SourceFunc signal_callback = () => {
            tear_down_accounts.begin(() => {this.quit();});
            return Source.REMOVE;
        };
        Unix.signal_add(ProcessSignal.INT, (owned) signal_callback);
        Unix.signal_add(ProcessSignal.TERM, (owned) signal_callback);

        Unix.signal_add(ProcessSignal.HUP, () => {
            tear_down_accounts.begin(() => {
                load_config();
                create_accounts.begin();
            });
            return Source.CONTINUE;
        });

        // TODO: implement config-finding logic
        if (config_path == "") {
            fatal("Config file path required");
            return;
        }

        load_config();

        TelepathyGLib.AccountManager? accman =
            TelepathyGLib.AccountManager.dup();
        if (accman == null) {
            fatal("Failed to obtain account manager reference");
            return;
        }
        account_manager = (!) accman;

        create_accounts.begin();
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
                        this.release();
                        return;
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
            stdout.printf("Library version: %s\n", "STUB");
            stdout.printf("Daemon version:  %s\n", DAEMON_VERSION);
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
