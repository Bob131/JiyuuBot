namespace JiyuuBot {
    public const string CLIENT = "so.bob131.JiyuuBot.Client";

    [DBus (name = "so.bob131.JiyuuBot.Client")]
    public interface Client : DBusProxy {
        public abstract async void handle_message(
            MessageContext context) throws Error;
    }

    internal class RegistrarApp : Application {
        internal Client[] clients = {};

        internal override void activate() {
            this.hold();
        }

        internal override bool dbus_register(
            DBusConnection connection,
            string object_path) throws Error
        {
            foreach (var client in clients) {
                var client_name = client.get_type().name();
                try {
                    connection.register_object(
                        Tp.path_from_name(@"$(application_id).$(client_name)"),
                        client);
                } catch (IOError e) {
                    fatal("Failed to register client '%s': %s", client_name,
                        e.message);
                }
            }

            return base.dbus_register(connection, object_path);
        }

        internal new int run(string[] args) {
            assert (args.length > 0);
            this.set_application_id(@"$(CLIENT).$(Path.get_basename(args[0]))");
            return base.run(args);
        }
    }

    public class ClientApp : Object {
        internal RegistrarApp app = new RegistrarApp();

        public void register(Client client) {
            app.clients += client;
        }

        public int run(string[] args) {
            return app.run(args);
        }
    }

    [DBus (name = "org.freedesktop.DBus.Introspectable")]
    internal interface Introspectable : DBusProxy {
        public abstract async string introspect() throws IOError;
    }

    internal class RecurseContext : Object {
        public DBusConnection bus {construct; get;}
        public string name {construct; get;}

        public string[] object_paths = {};

        public async void introspect(string path) throws Error {
            Introspectable iface = yield bus.get_proxy(name, path);
            var info = new DBusNodeInfo.for_xml(yield iface.introspect());
            if ((DBusInterfaceInfo?) info.lookup_interface(CLIENT) != null)
                object_paths += path;
            foreach (var node in info.nodes)
                yield introspect(@"$(path)/$(node.path)");
        }

        public RecurseContext(DBusConnection bus, string name) {
            Object(bus: bus, name: name);
        }
    }

    public async Client[] list_clients() throws Error {
        var bus = yield Bus.get(BusType.SESSION);
        var names = new GenericSet<string>(str_hash, str_equal);

        foreach (var f in new string[] {"ListNames", "ListActivatableNames"}) {
            var variant = yield bus.call("org.freedesktop.DBus", "/",
                "org.freedesktop.DBus", f, null, new VariantType("(as)"),
                DBusCallFlags.NONE, -1);
            foreach (var name in variant.get_child_value(0).get_strv())
                names.add(name);
        }

        Client[] ret = {};

        foreach (var name in names.get_values())
            if (name.has_prefix(@"$(CLIENT).")) {
                var context = new RecurseContext(bus, name);
                yield context.introspect(Tp.path_from_name(CLIENT));
                foreach (var path in context.object_paths)
                    ret += yield bus.get_proxy<Client>(name, path);
            }

        return ret;
    }
}
