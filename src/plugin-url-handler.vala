namespace JiyuuBot {
    namespace Plugins {
        private class FinalURLHandler : BasePlugin {
            private const string regex = "\\b(https?://[^\\s]+)\\b";

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

            private string? headers_to_readable(Soup.MessageHeaders headers, out double length) {
                var readable = "";
                if (headers.get_one("content-type") == null)
                    return null;
                readable += headers.get_one("content-type");
                readable = /;\s*/.split(readable)[0];
                if (!double.try_parse(headers.get_one("content-length") ?? "not a double", out length))
                    return readable;
                readable += readable_size(length);
                return readable;
            }

            public override void exec(Prpl.Message msg) {
                var session = new Soup.Session();
                var rx = new Regex(regex, RegexCompileFlags.CASELESS);
                MatchInfo mi;
                rx.match(msg.text, 0, out mi);
                do {
                    var url = mi.fetch(0);
                    var message = new Soup.Message("HEAD", url);
                    session.send_message(message);
                    if (message.status_code == 200) {
                        double? length;
                        var readable = headers_to_readable(message.response_headers, out length);
                        if (readable == null)
                            continue;
                        if ((message.response_headers.get_one("content-type") ?? "not html") == "text/html" &&
                                (length ?? 999999999) < 1048576) {
                            message = new Soup.Message("GET", url);
                            session.send_message(message);
                            var text = (string) message.response_body.flatten().data;
                            // anger the regex gods
                            MatchInfo title_stuff;
                            var _ = /(?<=\<title\>).*?(?=\<.title\>)/i.match(text, 0, out title_stuff);
                            var title = title_stuff.fetch(0);
                            if (title != null)
                                readable = @"$(title) [$(readable)]";
                        }
                        msg.send(readable);
                    }
                } while (mi.next());
            }
        }
    }
}
