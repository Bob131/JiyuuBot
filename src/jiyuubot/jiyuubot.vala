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
    bool print_version = false;

    protected override void activate() {
        this.hold();

        SourceFunc signal_callback = () => {
            this.quit();
            return false;
        };
        Unix.signal_add(ProcessSignal.INT, (owned) signal_callback);
        Unix.signal_add(ProcessSignal.TERM, (owned) signal_callback);

        Unix.signal_add(ProcessSignal.HUP, () => {
            message("Config reload stub");
            return Source.CONTINUE;
        });
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

        if (print_version) {
            stdout.printf("Library version: %s\n", "STUB");
            stdout.printf("Daemon version:  %s\n", DAEMON_VERSION);
            return 0;
        }

        return -1;
    }

    public App() {
        Object(application_id: "so.bob131.JiyuuBot");

        var options = new OptionEntry[4];
        options[0] = {"config", 'c', 0, OptionArg.FILENAME, ref config_path,
                        "Path to configuration file", "path"};
        options[1] = {"list-protocols", 'l', 0, OptionArg.NONE, ref list_proto,
                        "List available protocols", null};
        options[2] = {"version", 0, 0, OptionArg.NONE, ref print_version,
                        "Print version"};
        options[3] = {(string) null};
        this.add_main_option_entries(options);
    }

#if !TEST
    public static int main(string[] args) {
        return new App().run(args);
    }
#endif
}
