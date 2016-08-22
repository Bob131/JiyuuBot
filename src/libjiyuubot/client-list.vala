namespace JiyuuBot {
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
