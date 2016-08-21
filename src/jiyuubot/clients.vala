class Handler : DBusProxy, Tp.Handler {
    public class Client : DBusProxy, Tp.Client {
        public string[] interfaces {owned get {
            return {Tp.HANDLER};
        }}
    }

    public HashTable<string, Variant?>[] handler_channel_filter {owned get {
        var table = new HashTable<string, Variant?>(str_hash, str_equal);
        table[@"$(Tp.CHANNEL).ChannelType"] = new Variant("s", Tp.TEXT_CHANNEL);
        return {table};
    }}
    public bool bypass_approval {owned get {return false;}}
    public string[] capabilities {owned get {return {};}}

    ObjectPath[] _handled_channels = {};
    public ObjectPath[] handled_channels {owned get {return _handled_channels;}}

    async void message_signal(
        ObjectPath connection,
        ObjectPath channel,
        Variant @params)
    {
        if (@params.n_children() != 1)
            return;
        var message_variant = @params.get_child_value(0);
        if (!message_variant.is_of_type(new VariantType("aa{sv}")))
            return;

        JiyuuBot.Client[] clients;
        try {
            clients = yield JiyuuBot.list_clients();
        } catch (Error e) {
            warning("Failed to acquire client list: %s", e.message);
            return;
        }

        Tp.Message message = {(HashTable<string, Variant?>[]) message_variant};

        foreach (var client in clients)
            try {
                yield client.handle_message({connection, channel, message});
            } catch (Error e) {
                warning(e.message);
            }
    }

    // TODO: ack pending messages
    // TODO: handle Tp.Channel.closed()
    public async void handle_channels(
        ObjectPath account,
        ObjectPath connection,
        Tp.ChannelDetails[] channels,
        ObjectPath[] requests_satisifed,
        uint64 user_action_time,
        HashTable<string, Variant?> handler_info) throws Error
    {
        foreach (var chan_info in channels) {
            var bus = yield Bus.get(BusType.SESSION);
            bus.signal_subscribe(null, Tp.MESSAGE_CHANNEL, "MessageReceived",
                chan_info.path, null, DBusSignalFlags.NONE,
                (conn, sender, path, iface, sig, @params) => {
                    message_signal.begin(connection, chan_info.path, @params);
                });
            _handled_channels += chan_info.path;
        }
    }
}
