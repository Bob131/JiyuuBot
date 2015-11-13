namespace JiyuuBot {
    namespace Plugins {
        private class FinalURLHandler : BasePlugin {
            private const string regex = "\\bhttps?://[^\\s]+\\b";

            public override bool should_exec(Prpl.Message msg) {
                return msg.regex(regex);
            }

            private string readable_size(double size) {
                string[] units = {"B", "kiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"};
                var i = 0;
                while (size > 1024 && i < units.length) {
                    size /= 1024;
                    i++;
                }
                return ", %.*f %s".printf(i, size, units[i]);
            }

            public override void exec(Prpl.Message msg) {
                var sniffer = new Soup.ContentSniffer();
                var rx = new Regex(regex, RegexCompileFlags.CASELESS);
                MatchInfo mi;
                rx.match(msg.text, 0, out mi);
                foreach (var url in mi.fetch_all()) {
                    var message = new Soup.Message("GET", url);
                    size_t recv_length = 0;
                    message.got_chunk.connect((buf) => {
                        recv_length += buf.length;
                        if (recv_length > 1048576)
                            this.session.cancel_message(message, 400);
                    });
                    this.session.queue_message(message, (_, __) => {
                        var data = message.response_body.flatten();
                        var type = sniffer.sniff(message, data, null);
                        var readable = type.dup();
                        if (message.status_code == 200)
                            readable += readable_size(data.length);
                        else if (message.status_code == 400 && message.response_headers.get_one("content-length") != null)
                            readable += readable_size(double.parse(message.response_headers.get_one("content-length")));
                        if (type == "text/html") {
                            var text = (string) data.data;
                            // anger the regex gods
                            MatchInfo title_stuff;
                            var ___ = /(?<=\<title\>).*?(?=\<.title\>)/si.match(text, 0, out title_stuff);
                            var title = title_stuff.fetch(0);
                            if (title != null) {
                                title = /\s+/s.replace(title, -1, 0, " ").strip();
                                MatchInfo char_ents;
                                var ____ = /&[\w\d]+?;/i.match(title, 0, out char_ents);
                                foreach (var entity in char_ents.fetch_all()) {
                                    var desc = Html.EntityDesc.lookup(/[&;]/.replace(entity, -1, 0, ""));
                                    if (desc != null)
                                        title = title.replace(entity, ((char) desc->value).to_string());
                                }
                                readable = @"$(title) [$(readable)]";
                            }
                        }
                        msg.send(readable);
                    });
                }
            }
        }
    }
}
