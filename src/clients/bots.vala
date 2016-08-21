class Bots : DBusProxy, JiyuuBot.Client {
    public async void handle_message(JiyuuBot.MessageContext context)
        throws Error
    {
        if ((!) context.message.to_text() == ".bots")
            yield context.reply("Reporting in! [Vala/C] https://github.com/Bob131/JiyuuBot");
    }
}

static int main(string[] args) {
    var app = new JiyuuBot.ClientApp();
    app.register(new Bots());
    return app.run(args);
}
