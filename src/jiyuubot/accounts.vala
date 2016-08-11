class AccountManager : Object {
    public KeyFile config {construct; get;}

    TelepathyGLib.AccountManager account_manager;
    GenericSet<TelepathyGLib.Account> accounts =
        new GenericSet<TelepathyGLib.Account>(direct_hash, direct_equal);

    const string[] ignore_keys = {"connection-manager", "protocol", "rooms"};

    public async void create_accounts() {
        foreach (var display_name in config.get_groups()) {
            TelepathyGLib.AccountRequest acc_req;
            string[] rooms = {};

            try {
                acc_req = new TelepathyGLib.AccountRequest(
                    account_manager,
                    config.get_string(display_name, "connection-manager"),
                    config.get_string(display_name, "protocol"),
                    display_name);

                var conman = new TelepathyGLib.ConnectionManager(
                    account_manager.dbus_daemon, acc_req.connection_manager,
                    null);
                yield conman.prepare_async(null);

                TelepathyGLib.Protocol? _proto =
                    conman.get_protocol_object(acc_req.protocol);
                if (_proto == null)
                    throw new TelepathyGLib.Error.INVALID_ARGUMENT(
                        "Protocol '%s' on connection manager '%s' %s",
                        acc_req.protocol, acc_req.connection_manager, "doesn't exist");
                var proto = (!) _proto;

                foreach (var key in config.get_keys(display_name)) {
                    if (key in ignore_keys)
                        continue;

                    if (!proto.has_param(key))
                        throw new TelepathyGLib.Error.INVALID_ARGUMENT(
                            "Protocol '%s' does not have parameter '%s'",
                            acc_req.protocol, key);

                    var tp_param = proto.get_param(key);
                    var variant = Variant.parse(tp_param.dup_variant_type(),
                        config.get_string(display_name, key));

                    acc_req.set_parameter(key, variant);
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
                var dict = new VariantDict(acc_req.parameters);
                if (!dict.contains("fullname"))
                    acc_req.set_parameter("fullname", "Jiyuu Bot");
                if (!dict.contains("username"))
                    acc_req.set_parameter("username", "JiyuuBot");
            }

            acc_req.set_enabled(true);
            acc_req.set_connect_automatically(true);

            TelepathyGLib.Account account;
            try {
                account = yield acc_req.create_account_async();
                accounts.add(account);
            } catch (Error e) {
                JiyuuBot.fatal("Failed to create account '%s': %s",
                    acc_req.display_name, e.message);
            }

            foreach (var room in rooms) {
                var chan_req =
                    new TelepathyGLib.AccountChannelRequest.text(account,
                    TelepathyGLib.USER_ACTION_TIME_NOT_USER_ACTION);
                chan_req.set_target_id(TelepathyGLib.HandleType.ROOM, room);

                // we don't want to yield, but we want to notify on error
                chan_req.ensure_channel_async.begin((string) null, null,
                    (obj, res) => {
                        try {
                            chan_req.ensure_channel_async.end(res);
                        } catch (Error e) {
                            warning("Failed to join room '%s': %s", room,
                                e.message);
                        }
                    });
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
                yield account.remove_async();
            } catch (Error e) {
                warning("Failed tear-down of account '%s': %s",
                    account.display_name, e.message);
            }
    }

    public AccountManager(KeyFile config) {
        Object(config: config);

        TelepathyGLib.AccountManager? accman =
            TelepathyGLib.AccountManager.dup();
        if (accman == null)
            JiyuuBot.fatal("Failed to obtain account manager reference");
        account_manager = (!) accman;
    }
}
