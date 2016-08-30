extern const string DATADIR;

const string DBUS_CONFIG = """
<!DOCTYPE busconfig PUBLIC "-//freedesktop//DTD D-Bus Bus Configuration 1.0//EN"
 "http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">
<busconfig>
  <type>session</type>

  <servicedir>%s</servicedir>
  <listen>%s</listen>

  <syslog/>

  <policy context="default">
    <allow send_destination="*" eavesdrop="true"/>
    <allow eavesdrop="true"/>
    <allow own="*"/>
  </policy>
</busconfig>
""";

[DBus (name = "org.freedesktop.DBus")]
interface DBusIface : Object {
    public abstract uint32 start_service_by_name(string name, uint32 flags = 0)
        throws Error;
}

[DBus (name = "so.bob131.JiyuuBot.Bus")]
class JiyuuBotBus : Object {
    public string address {construct; get;}
    [DBus (visible = false)]
    public string tmp_dir {construct; get;}

    public JiyuuBotBus() throws FileError {
        var tmp_dir = DirUtils.make_tmp("jiyuubot-XXXXXX");
        Object(tmp_dir: tmp_dir, address:
            "unix:path=%s".printf(Path.build_filename(tmp_dir, "bus")));
    }
}

class JiyuuBot.Launcher : Application {
    public string[] args {construct; get;}

    JiyuuBotBus bus;
    Subprocess dbus_daemon;
    Subprocess bot;

    protected override void activate() {
        this.hold();

        var session_bus = this.get_dbus_connection();

        try {
            bus = new JiyuuBotBus();
        } catch (FileError e) {
            fatal("Failed to create new bus directory: %s", e.message);
        }

        try {
            session_bus.register_object("/so/bob131/JiyuuBot/Bus", bus);
        } catch (IOError e) {
            fatal("Failed to register bus object: %s", e.message);
        }

        var tmp_services_path = Path.build_filename(bus.tmp_dir, "services");
        var dbus_conf_path = Path.build_filename(bus.tmp_dir, "dbus.conf");

        if (DirUtils.create_with_parents(tmp_services_path, 0777) == -1) {
            fatal("Failed to create directory at %s: %s", tmp_services_path,
                strerror(errno));
        }

        var xdg_paths = Environment.get_system_data_dirs();
        xdg_paths += DATADIR;
        xdg_paths += Environment.get_user_data_dir();

        foreach (var path in xdg_paths) {
            var services_path = Path.build_filename(path, "dbus-1", "services");

            Dir services_dir;
            try {
                services_dir = Dir.open(services_path);
            } catch (FileError e) {
                continue;
            }

            string? _service;
            while ((_service = services_dir.read_name()) != null) {
                var service = (!) _service;
                var parts = service.split(".");
                if (parts.length < 4)
                    continue;
                var prefix = string.joinv(".", (string?[]?) parts[0:4]);
                switch (prefix) {
                    case Tp.ACCOUNT_MANAGER:
                    case Tp.CONNECTION_MANAGER:
                    case JiyuuBot.CLIENT:
                        var source =
                            Path.build_filename(services_path, service);
                        var dest =
                            Path.build_filename(tmp_services_path, service);
                        if (FileUtils.symlink(source, dest) == -1
                                && errno != Posix.EEXIST)
                            warning("Failed to symlink %s to %s: %s", source,
                                dest, strerror(errno));
                        break;
                }
            }
        }

        try {
            FileUtils.set_contents(dbus_conf_path,
                DBUS_CONFIG.printf(tmp_services_path, bus.address));
        } catch (FileError e) {
            fatal("Failed to write DBus config to %s: %s", dbus_conf_path,
                e.message);
        }

        // clear $HOME so Mission Control doesn't sync-up with another instance
        var env = new SubprocessLauncher(SubprocessFlags.NONE);
        env.setenv("HOME", "/dev/null", true);

        try {
            dbus_daemon = env.spawnv({"dbus-daemon",
                "--config-file=%s".printf(dbus_conf_path),
                "--nofork"});
        } catch (Error e) {
            fatal("Failed to launch DBus daemon: %s", e.message);
        }

        Environment.set_variable("DBUS_SESSION_BUS_ADDRESS", bus.address, true);
        env.setenv("DBUS_SESSION_BUS_ADDRESS", bus.address, true);

        try {
            assert (BusType.get_address_sync(BusType.SESSION) == bus.address);
            DBusIface bus = GLib.Bus.get_proxy_sync(BusType.SESSION,
                "org.freedesktop.DBus", "/");
            bus.start_service_by_name(Tp.ACCOUNT_MANAGER);
        } catch (Error e) {
            fatal("Failed to start account manager: %s", e.message);
        }

        string[] launch_args = {"jiyuubot"};
        foreach (var arg in args)
            launch_args += arg;

        try {
            bot = env.spawnv(launch_args);
        } catch (Error e) {
            fatal("Failed to start JiyuuBot: %s", e.message);
        }

        Unix.signal_add(ProcessSignal.INT, () => {
            bot.send_signal(ProcessSignal.INT);
            return Source.CONTINUE;
        });
        Unix.signal_add(ProcessSignal.TERM, () => {
            bot.send_signal(ProcessSignal.TERM);
            return Source.CONTINUE;
        });

        bot.wait_async.begin(null, (obj, res) => {
            try {
                bot.wait_async.end(res);
            } catch {}

            if (bot.get_if_signaled()) {
                var sig = (ProcessSignal) bot.get_term_sig();
                if (sig != ProcessSignal.INT && sig != ProcessSignal.TERM)
                    critical(strsignal(sig));
            }

            this.quit();
        });
    }

    void recursive_delete(string path)
        requires (FileUtils.test(path, FileTest.IS_DIR))
    {
        Dir directory;
        try {
            directory = Dir.open(path);
        } catch (FileError e) {
            stderr.printf("Couldn't open %s: %s\n", path, e.message);
            return;
        }
        string? name;
        while ((name = directory.read_name()) != null) {
            var file = Path.build_filename(path, (!) name);
            if (FileUtils.test(file, FileTest.IS_DIR))
                recursive_delete(file);
            else if (FileUtils.unlink(file) == -1)
                stderr.printf("Couldn't delete file %s: %s\n", file,
                    strerror(errno));
        }
        if (DirUtils.remove(path) == -1)
            stderr.printf("Couldn't delete directory %s: %s\n", path,
                strerror(errno));
    }

    protected override void shutdown() {
        var mc = MainContext.default();

        var cont = false;
        dbus_daemon.wait_async.begin(null, (obj, res) => {
            try {
                dbus_daemon.wait_async.end(res);
            } catch {
                dbus_daemon.force_exit();
            }
            cont = true;
        });
        dbus_daemon.send_signal(ProcessSignal.TERM);
        while (!cont)
            mc.iteration(true);

        recursive_delete(bus.tmp_dir);

        base.shutdown();
    }

    Launcher(string[] args) {
        Object(application_id: "so.bob131.JiyuuBot", args: args);
    }

    public static int main(string[] args) {
        return new Launcher(args[1:args.length]).run();
    }
}
