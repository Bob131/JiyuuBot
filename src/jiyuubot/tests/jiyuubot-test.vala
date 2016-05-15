public static int main(string[] args) {
    Test.init(ref args);
    Test.set_nonfatal_assertions();

    Test.add_func("/jiyuubot/cli/list-protocols", () => {
        foreach (var arg in new string[] {"-l", "--list-protocols"}) {
            var app = new JiyuuBot.App();
            Test.expect_message(null, LogLevelFlags.LEVEL_DEBUG,
                "*Probing for available protocols...");
            assert (app.run({"jiyuubot", arg}) == 0);
            Test.assert_expected_messages();
        }
    });

    Test.add_func("/jiyuubot/cli/version", () => {
        if (!Test.subprocess()) {
            Test.trap_subprocess((string) null, 0, 0);
            Test.trap_assert_stdout("Library version*\nDaemon version*");
            return;
        }

        var app = new JiyuuBot.App();
        assert (app.run({"jiyuubot", "--version"}) == 0);
    });

    Test.run();
    return 0;
}
