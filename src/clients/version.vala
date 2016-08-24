using JiyuuBot;

extern const string VERSION;

static int main(string[] args) {
    var client = new CommandClient<CommandOptions>({"version"});
    client.description = "Print JiyuuBot version";
    client.command_invoked.connect((context) => {
        context.reply.begin(
            @"JiyuuBot v$VERSION | https://github.com/Bob131/JiyuuBot");
    });

    var app = new ClientApp();
    app.register(client);

    return app.run(args);
}
