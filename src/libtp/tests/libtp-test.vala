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

    Test.run();
    return 0;
}
