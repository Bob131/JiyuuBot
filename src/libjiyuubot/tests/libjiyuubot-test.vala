public static int main(string[] args) {
    Test.init(ref args);
    Test.set_nonfatal_assertions();

    Test.add_func("/libjiyuubot/fatal-function", () => {
        if (!Test.subprocess()) {
            Test.trap_subprocess((string) null, 0, 0);
            Test.trap_assert_stderr(
                "?? FATAL: libjiyuubot-test.vala:*: Example error message\n");
            Test.trap_assert_stdout("Post-shutdown hook successful\n");
            Test.trap_assert_failed();
            return;
        }

        var app = new Application(null, 0);
        app.activate.connect(() => {
            JiyuuBot.fatal("Example error message");
        });
        app.activate.connect_after(() => {
            stdout.printf("Test failed to exit\n");
        });
        app.shutdown.connect_after(() => {
            stdout.printf("Post-shutdown hook successful\n");
        });
        app.run();
    });

    Test.run();
    return 0;
}
