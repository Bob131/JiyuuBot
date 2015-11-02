using JiyuuBot;

// override GLib.message
public void message(string text, void* _ = null) {
    stdout.printf(@"** $(text)\n");
}


class JiyuuBotApp : Application {
    private Prpl.Interface prpl;
    private Plugins.Manager plugman;

    private JiyuuBotApp() {
        Object(application_id: app_id,
            flags: ApplicationFlags.NON_UNIQUE);
    }

    protected override void shutdown() {
        base.shutdown();
        plugman = null;
        this.release();
        stderr.printf("\n");
    }

    protected override void activate() {
        base.activate();
        this.hold();

        Unix.signal_add(ProcessSignal.INT, () => {
            this.quit();
            return false;
        });
        Unix.signal_add(ProcessSignal.TERM, () => {
            this.quit();
            return false;
        });

        prpl = new Prpl.Interface(new Config.AccountList.load_from_config());
        plugman = new Plugins.Manager();
        prpl.incoming_message.connect((msg) => {plugman.incoming_message(msg);});
    }

    public static int main(string[] args) {
        var app = new JiyuuBotApp();
        return app.run(args);
    }
}
