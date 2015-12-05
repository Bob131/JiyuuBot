using JiyuuBot;

class nyaa : Plugins.BasePlugin {
    private const string regex = "https?://[\\w\\.]*nyaa.se/\\?page=view&tid=\\d+";

    public override bool should_exec(Prpl.Message msg) {
        return msg.regex(regex);
    }

    public override void exec(Prpl.Message msg) {
        var rx = new Regex(regex, RegexCompileFlags.CASELESS);
        MatchInfo mi;
        rx.match(msg.text, 0, out mi);
        foreach (var match in mi.fetch_all()) {
            var message = new Soup.Message("GET", match);
            this.session.queue_message(message, (_, __) => {
                if (message.status_code == Soup.Status.OK) {
                    var text = (string) message.response_body.flatten().data;
                    if ("does not appear to be in the database" in text) {
                        msg.send("Error: Torrent ID not found");
                    } else {
                        var doc_root = Misc.SaneDoc.read_doc(text);
                        var name = doc_root->find_all(Misc.CssToXPath.class("viewtorrentname"))[0]->get_content();
                        var _size_array = doc_root->find_all(Misc.CssToXPath.class("vtop"));
                        var size = _size_array[_size_array.length-1]->get_content();
                        var up = doc_root->find_all(Misc.CssToXPath.class("viewsn"))[0]->get_content();
                        var down = doc_root->find_all(Misc.CssToXPath.class("viewln"))[0]->get_content();
                        msg.send(@"$name - Size: $size - Peers: ↑$up/↓$down");
                    }
                } else {
                    msg.send(@"Error fetching $match: $(message.reason_phrase)");
                }
            });
        }
    }
}

Type[] register_plugin() {
    return {typeof(nyaa)};
}
