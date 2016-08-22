class AccountManager : Object {
    public KeyFile config {construct; get;}
    public Tp.AccountManager tp_am {construct; get;}

    GenericSet<Tp.Account> accounts =
        new GenericSet<Tp.Account>(direct_hash, direct_equal);

    const string[] ignore_keys = {"connection-manager", "protocol", "rooms"};

    public async void create_accounts() {
        foreach (var display_name in config.get_groups()) {
            Tp.AccountRequest acc_req;
            string[] rooms = {};

            try {
                acc_req = new Tp.AccountRequest(
                    config.get_string(display_name, "connection-manager"),
                    config.get_string(display_name, "protocol"));

                acc_req.display_name = display_name;

                var cm = yield Tp.ConnectionManager.get_manager(
                    acc_req.connection_manager);
                var @params = yield cm.get_parameters(acc_req.protocol);
                var config_keys = config.get_keys(display_name);

                foreach (var param in @params) {
                    if (!(param.name in config_keys))
                        continue;
                    var variant = Variant.parse(
                        new VariantType(param.signature),
                        config.get_string(display_name, param.name));
                    acc_req.parameters[param.name] = variant;
                }

                if (config.has_key(display_name, "rooms"))
                    rooms = config.get_string_list(display_name, "rooms");
            } catch (Error e) {
                JiyuuBot.fatal("Couldn't set up account '%s': %s", display_name,
                    e.message);
            }

            // https://bugs.freedesktop.org/show_bug.cgi?id=97210
            if (acc_req.connection_manager == "idle" &&
                    acc_req.protocol == "irc") {
                if (!acc_req.parameters.contains("fullname"))
                    acc_req.parameters["fullname"] = "Jiyuu Bot";
                if (!acc_req.parameters.contains("username"))
                    acc_req.parameters["username"] = "JiyuuBot";
            }

            acc_req.enabled = true;
            acc_req.connect_automatically = true;

            Tp.Account account;
            try {
                account = yield acc_req.create(tp_am);
                accounts.add(account);
            } catch (Error e) {
                JiyuuBot.fatal("Failed to create account '%s': %s",
                    acc_req.display_name, e.message);
            }

            Tp.ChannelDispatcher chan_dispatch;
            try {
                chan_dispatch = yield Tp.ChannelDispatcher.dup();
            } catch (Error e) {
                JiyuuBot.fatal("Failed to acquire channel dispatcher: %s",
                    e.message);
            }

            foreach (var room in rooms) {
                var props = new Tp.ChannelRequestProperties();
                props.set_target(Tp.HandleType.ROOM, room.strip());
                props.channel_type = Tp.TEXT_CHANNEL;

                Tp.ChannelRequest chan_req;

                try {
                    var chan_req_path = yield chan_dispatch.ensure_channel(
                        new ObjectPath(account.g_object_path), props);
                    chan_req = yield Tp.ChannelRequest.from_path(chan_req_path);
                } catch (Error e) {
                    warning("Failed to create channel request for '%s': %s",
                        room, e.message);
                    continue;
                }

                chan_req.failed.connect((error, message) => {
                    warning("Failed to join room '%s': %s", room, message);
                });

                try {
                    yield chan_req.proceed();
                } catch (Error e) {
                    warning(e.message);
                }
            }
        }

        if (accounts.length == 0)
            JiyuuBot.fatal("No accounts were set-up. Exiting");
        else
            message("Connected %u account%s!", accounts.length,
                accounts.length != 1 ? "s" : "");
    }

    public async void tear_down_accounts() {
        if (accounts.length == 0)
            return;

        message("Disconnecting accounts...");

        foreach (var account in accounts.get_values())
            try {
                yield account.remove();
            } catch (Error e) {
                warning("Failed tear-down of account '%s': %s",
                    account.display_name, e.message);
            }
    }

    public AccountManager(KeyFile config) {
        Tp.AccountManager accman;
        try {
            accman = Tp.AccountManager.dup();
        } catch (Error e) {
            JiyuuBot.fatal("Failed to obtain account manager reference: %s",
                e.message);
        }

        Object(config: config, tp_am: (!) accman);
    }
}
