namespace Tp {
    public const string CONNECTION_MANAGER =
        "org.freedesktop.Telepathy.ConnectionManager";

    [Flags]
    public enum ProtocolParameterFlags {
        REQUIRED,
        REGISTER,
        HAS_DEFAULT,
        SECRET,
        DBUS_PROPERTY
    }

    public struct ProtocolParameter {
        string name;
        ProtocolParameterFlags flags;
        string signature;
        Variant default_value;
    }

    [DBus (name = "org.freedesktop.Telepathy.ConnectionManager")]
    public interface ConnectionManager : DBusProxy {
        public abstract async ProtocolParameter[] get_parameters(
            string protocol) throws Error;
        public abstract async string[] list_protocols() throws IOError;

        [DBus (visible = false)]
        public string get_cm_name() {
            return this.g_name.split(".")[4];
        }

        [DBus (visible = false)]
        public static async ConnectionManager get_manager(string name)
            throws Error
        {
            var bus_name = "%s.%s".printf(CONNECTION_MANAGER, name);
            return yield Bus.get_proxy<ConnectionManager>(BusType.SESSION,
                bus_name, path_from_name(bus_name));
        }
    }

    public async ConnectionManager[] list_connection_managers()
        throws Error
    {
        var bus = yield Bus.get(BusType.SESSION);
        var names = new GenericSet<string>(str_hash, str_equal);

        foreach (var f in new string[] {"ListNames", "ListActivatableNames"}) {
            var variant = yield bus.call("org.freedesktop.DBus", "/",
                "org.freedesktop.DBus", f, null, new VariantType("(as)"),
                DBusCallFlags.NONE, -1);
            foreach (var name in variant.get_child_value(0).get_strv())
                names.add(name);
        }

        ConnectionManager[] ret = {};

        foreach (var name in names.get_values())
            if (name.has_prefix(@"$(CONNECTION_MANAGER)."))
                ret += yield ConnectionManager.get_manager(name.split(".")[4]);

        return ret;
    }
}
