using JiyuuBot;

static int main(string[] args) {
    var client = new CommandClient<CommandOptions>({"bots"});
    client.description =
        "Client implementing https://git.teknik.io/Teknikode/IBIP";
    client.command_invoked.connect((context) => {
        context.reply.begin(
            "Reporting in! [Vala/C] https://github.com/Bob131/JiyuuBot");
    });

    var app = new ClientApp();
    app.register(client);

    return app.run(args);
}
