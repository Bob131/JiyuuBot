const string IDLE_QUERY_CONFIG = """account
  Type:     s
  Required: true
server
  Type:     s
  Required: true
fullname
  Type:     s
  Required: false
username
  Type:     s
  Required: false
port
  Type:     q
  Required: false
  Default:  6667
charset
  Type:     s
  Required: false
  Default:  'UTF-8'
keepalive-interval
  Type:     u
  Required: false
  Default:  30
quit-message
  Type:     s
  Required: false
use-ssl
  Type:     b
  Required: false
  Default:  false
password-prompt
  Type:     b
  Required: false
  Default:  false
""";


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

    Test.add_func("/jiyuubot/cli/query-config", () => {
        if (!Test.subprocess()) {
            Test.trap_subprocess((string) null, 0, 0);
            Test.trap_assert_stdout(IDLE_QUERY_CONFIG + IDLE_QUERY_CONFIG);
            return;
        }

        foreach (var arg in new string[] {"-q", "--query-config"})
            assert (new JiyuuBot.App().run({"jiyuubot", arg, "idle:irc"}) == 0);
    });

    Test.add_func("/jiyuubot/cli/query-config/wrong-format", () => {
        if (!Test.subprocess()) {
            Test.trap_subprocess((string) null, 0, 0);
            Test.trap_assert_stderr(
                "Protocol must be in the format connection-manager:protocol*");
            return;
        }

        assert (new JiyuuBot.App().run({"jiyuubot", "-q", "invalid"}) == 1);
    });

    Test.add_func("/jiyuubot/cli/query-config/unknown-cm", () => {
        if (!Test.subprocess()) {
            Test.trap_subprocess((string) null, 0, 0);
            Test.trap_assert_stderr(
                "Unknown connection manager 'unk'. Use -l to list protocols\n");
            return;
        }

        assert (new JiyuuBot.App().run({"jiyuubot", "-q", "unk:unk"}) == 1);
    });

    Test.add_func("/jiyuubot/cli/query-config/unknown-protocol", () => {
        if (!Test.subprocess()) {
            Test.trap_subprocess((string) null, 0, 0);
            Test.trap_assert_stderr(
                "Unknown protocol 'unk'. Use -l to list protocols\n");
            return;
        }

        assert (new JiyuuBot.App().run({"jiyuubot", "-q", "idle:unk"}) == 1);
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
