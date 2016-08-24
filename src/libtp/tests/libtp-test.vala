const string TEST_MESSAGE = """
[
    {
        "pending-message-id": <uint32 2>,
        "message-sender-id": <"bob131">,
        "message-received": <int64 1471977110>,
        "message-sender": <uint32 2>
    },
    {
        "content": <"this is a test message">,
        "content-type": <"text/plain">
    }
]
""";


public static int main(string[] args) {
    Test.init(ref args);
    Test.set_nonfatal_assertions();

    Test.add_func("/libtp/constants-test", () => {
#if TP_GLIB_TEST
        // accounts.vala
        assert (Tp.ACCOUNT_MANAGER == TelepathyGLib.IFACE_ACCOUNT_MANAGER);
        assert (Tp.ACCOUNT == TelepathyGLib.IFACE_ACCOUNT);

        // channels.vala
        assert (Tp.CHANNEL == TelepathyGLib.IFACE_CHANNEL);
        assert (Tp.MESSAGE_CHANNEL
            == TelepathyGLib.IFACE_CHANNEL_INTERFACE_MESSAGES);
        assert (Tp.TEXT_CHANNEL == TelepathyGLib.IFACE_CHANNEL_TYPE_TEXT);
        assert (Tp.CHANNEL_DISPATCHER
            == TelepathyGLib.IFACE_CHANNEL_DISPATCHER);

        // clients.vala
        assert (Tp.CLIENT == TelepathyGLib.IFACE_CLIENT);
        assert (Tp.HANDLER == TelepathyGLib.IFACE_CLIENT_HANDLER);

        // connections.vala
        assert (Tp.CONNECTION_MANAGER
            == TelepathyGLib.IFACE_CONNECTION_MANAGER);
#else
        Test.skip("Telepathy-GLib required for this test");
#endif
    });

    Test.add_func("/libtp/message/segfault-test", () => {
        var pattern = new PatternSpec(
            "tp_message_get_*: assertion '*length1 > 0' failed");
        Test.log_set_fatal_handler((domain, flags, message) => {
            if (domain == null && LogLevelFlags.LEVEL_CRITICAL in flags
                    && pattern.match_string(message))
                return false;
            return true;
        });

        Func do_nothing = (data) => {};
        Tp.Message message = {};

        do_nothing(message.token);
        do_nothing(message.received_timestamp);
        do_nothing(message.sender_nick);
        do_nothing((void*) message.message_type);
        do_nothing(message.scrollback);
        do_nothing(message.rescued);

        assert (message.to_text() == null);
    });

    Test.add_func("/libtp/message/parse-test", () => {
        Variant message_variant;
        try {
            message_variant = Variant.parse(null, TEST_MESSAGE);
        } catch (VariantParseError e) {
            Test.message("Message parse failed: %s", e.message);
            Test.fail();
            return;
        }

        Tp.Message message = {(HashTable<string, Variant?>[]) message_variant};

        assert (message.token == null);
        assert (message.received_timestamp == 1471977110);
        assert (message.sender_nick == null);
        assert (message.message_type == Tp.MessageType.NORMAL);
        assert (message.scrollback == false);
        assert (message.rescued == false);

        assert ((!) message.to_text() == "this is a test message");
    });

    Test.add_func("/libtp/connection-manager/list", () => {
        var cm_names = new GenericSet<string>(str_hash, str_equal);

        TestDBus.unset();
        var bus = new TestDBus(TestDBusFlags.NONE);

        var xdg_paths = Environment.get_system_data_dirs();
        xdg_paths += Environment.get_user_data_dir();

        foreach (var path in xdg_paths) {
            path = Path.build_filename(path, "dbus-1", "services");

            bus.add_service_dir(path);

            Dir service_dir;
            try {
                service_dir = Dir.open(path);
            } catch {
                continue;
            }

            string? name = null;
            while ((name = service_dir.read_name()) != null)
                if (((!) name).has_prefix(Tp.CONNECTION_MANAGER))
                    cm_names.add(((!) name).replace(".service", ""));
        }

        bus.up();

        Tp.ConnectionManager[]? cms = null;
        Tp.list_connection_managers.begin((obj, res) => {
            try {
                cms = Tp.list_connection_managers.end(res);
            } catch (Error e) {
                error("Failed to list connection managers: %s", e.message);
            }
        });

        while (cms == null)
            MainContext.default().iteration(true);

        assert (((!) cms).length == cm_names.length);

        foreach (var cm in (!) cms)
            assert (cm.g_name in cm_names);

        // we have to free all DBusProxies before the bus gets torn down, else
        // we segfault
        cms = null;
    });

    Test.run();
    return 0;
}
