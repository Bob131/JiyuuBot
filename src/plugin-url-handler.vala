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

            private string? get_mime(string? content_type) {
                if (content_type == null)
                    return null;
                return /;\s*/.split(content_type)[0];
            }

            private string? headers_to_readable(Soup.MessageHeaders headers, out double length) {
                var readable = "";
                if (headers.get_one("content-type") == null)
                    return null;
                readable += headers.get_one("content-type");
                readable = get_mime(headers.get_one("content-type"));
                if (!double.try_parse(headers.get_one("content-length") ?? "not a double", out length) || length == 0)
                    return readable;
                readable += readable_size(length);
                return readable;
            }

            public override void exec(Prpl.Message msg) {
                var session = new Soup.Session();
                var rx = new Regex(regex, RegexCompileFlags.CASELESS);
                MatchInfo mi;
                rx.match(msg.text, 0, out mi);
                foreach (var url in mi.fetch_all()) {
                    var message = new Soup.Message("HEAD", url);
                    session.queue_message(message, (_who, __dontcare) => {
                        if (message.status_code == 200) {
                            double? length;
                            var readable = headers_to_readable(message.response_headers, out length);
                            if (readable == null)
                                return;
                            if (get_mime(message.response_headers.get_one("content-type")) == "text/html") {
                                message = new Soup.Message("GET", url);
                                size_t recv_length = 0;
                                message.got_chunk.connect((buf) => {
                                    recv_length += buf.length;
                                    if (recv_length > 1048576)
                                        session.cancel_message(message, 400);
                                });
                                session.queue_message(message, (_, __) => {
                                    var text = (string) message.response_body.flatten().data;
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
                                    msg.send(readable);
                                });
                            } else
                                msg.send(readable);
                        }
                    });
                }
            }
        }
    }
}
