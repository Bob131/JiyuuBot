using JiyuuBot;

class bots : Plugins.BasePlugin {
    public override bool should_exec(Prpl.Message msg) {
        return msg.command("bots");
    }

    public override void exec(Prpl.Message msg) {
        msg.send("Reporting in! [Vala]");
    }
}

public Type[] register_plugin() {
    return {typeof(bots)};
}