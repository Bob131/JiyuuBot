namespace Tp {
    public const string CLIENT = "org.freedesktop.Telepathy.Client";
    public const string HANDLER = "org.freedesktop.Telepathy.Client.Handler";

    [DBus (name = "org.freedesktop.Telepathy.Client")]
    public interface Client : DBusProxy {
        public abstract string[] interfaces {owned get;}
    }

    public struct ChannelDetails {
        ObjectPath path;
        HashTable<string, Variant?> properties;
    }

    [DBus (name = "org.freedesktop.Telepathy.Client.Handler")]
    public interface Handler : DBusProxy {
        public abstract HashTable<string, Variant?>[] handler_channel_filter {
            owned get;
        }
        public abstract bool bypass_approval {owned get;}
        public abstract string[] capabilities {owned get;}
        public abstract ObjectPath[] handled_channels {owned get;}

        public abstract async void handle_channels(
            ObjectPath account,
            ObjectPath connection,
            ChannelDetails[] channels,
            ObjectPath[] requests_satisifed,
            uint64 user_action_time,
            HashTable<string, Variant?> handler_info) throws Error;
    }
}
