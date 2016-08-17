namespace Tp {
    public const string CHANNEL = "org.freedesktop.Telepathy.Channel";
    public const string MESSAGE_CHANNEL =
        "org.freedesktop.Telepathy.Channel.Interface.Messages";
    public const string TEXT_CHANNEL =
        "org.freedesktop.Telepathy.Channel.Type.Text";
    public const string CHANNEL_DISPATCHER =
        "org.freedesktop.Telepathy.ChannelDispatcher";

    [DBus (name = "org.freedesktop.Telepathy.Channel")]
    public interface Channel : DBusProxy {
        public abstract string channel_type {owned get;}

        public abstract async void close() throws Error;
        public signal void closed();

        [DBus (visible = false)]
        public static async T from_path<T>(
            ObjectPath connection,
            ObjectPath channel) throws Error
        {
            return yield Bus.get_proxy(BusType.SESSION,
                name_from_path(connection), channel);
        }
    }

    [DBus (name = "org.freedesktop.Telepathy.Channel.Interface.Messages")]
    public interface MessageChannel : DBusProxy {
        public abstract async string send_message(
            HashTable<string, Variant?>[] message,
            MessageSendFlags flags) throws Error;
    }

    [DBus (name = "org.freedesktop.Telepathy.Channel.Type.Text")]
    public interface TextChannel : DBusProxy {
        public abstract async void acknowledge_pending_messages(
            uint32[] message_IDs) throws Error;
    }

    public class ChannelRequestProperties : HashTable<string, Variant?> {
        public string? channel_type {
            set {
                return_if_fail(value != null);
                this[@"$(Tp.CHANNEL).ChannelType"] = new Variant("s", value);
            }
            get {
                var variant = this[@"$(Tp.CHANNEL).ChannelType"];
                if (variant == null)
                    return null;
                return ((!) variant).get_string();
            }
        }

        public void set_target(HandleType handle, string target) {
            this[@"$(Tp.CHANNEL).TargetHandleType"] = new Variant("u", handle);
            this[@"$(Tp.CHANNEL).TargetID"] = new Variant("s", target);
        }

        public ChannelRequestProperties() {
            base.full(str_hash, str_equal, null, null);
        }
    }

    [DBus (name = "org.freedesktop.Telepathy.ChannelRequest")]
    public interface ChannelRequest : DBusProxy {
        public abstract async void proceed() throws Error;
        public abstract async void cancel() throws IOError;

        public signal void failed(string error, string message);
        public signal void succeeded();
        public signal void succeeded_with_channel(
            ObjectPath connection,
            HashTable<string, Variant?> connection_properties,
            ObjectPath channel,
            HashTable<string, Variant?> channel_properties);

        [DBus (visible = false)]
        public static async ChannelRequest from_path(string path)
            throws Error
        {
            return yield Bus.get_proxy(BusType.SESSION, CHANNEL_DISPATCHER,
                path);
        }
    }

    [DBus (name = "org.freedesktop.Telepathy.ChannelDispatcher")]
    public interface ChannelDispatcher : DBusProxy {
        public abstract async ObjectPath ensure_channel(
            ObjectPath account,
            HashTable<string, Variant?> requested_properties,
            int64 user_action_time = 0,
            string preferred_handler = "") throws Error;

        [DBus (visible = false)]
        public static async ChannelDispatcher dup() throws Error {
            return yield Bus.get_proxy(BusType.SESSION, CHANNEL_DISPATCHER,
                path_from_name(CHANNEL_DISPATCHER));
        }
    }
}
