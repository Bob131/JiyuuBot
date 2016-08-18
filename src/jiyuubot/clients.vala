class Client : DBusProxy, Tp.Client {
    public string[] interfaces {owned get {
        return {Tp.HANDLER};
    }}
}

class Handler: DBusProxy, Tp.Handler {
    public HashTable<string, Variant?>[] handler_channel_filter {owned get {
        var table = new HashTable<string, Variant?>(str_hash, str_equal);
        table[@"$(Tp.CHANNEL).ChannelType"] = new Variant("s", Tp.TEXT_CHANNEL);
        return {table};
    }}
    public bool bypass_approval {owned get {return false;}}
    public string[] capabilities {owned get {return {};}}

    ObjectPath[] _handled_channels = {};
    public ObjectPath[] handled_channels {owned get {return _handled_channels;}}

    public async void handle_channels(
        ObjectPath account,
        ObjectPath connection,
        Tp.ChannelDetails[] channels,
        ObjectPath[] requests_satisifed,
        uint64 user_action_time,
        HashTable<string, Variant?> handler_info) throws Error
    {
        foreach (var channel in channels) {
            message("Handling %s", channel.path);
            _handled_channels += channel.path;
        }
    }
}
