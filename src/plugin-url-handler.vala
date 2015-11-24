namespace JiyuuBot {
    namespace Plugins {
        private class FinalURLHandler : BasePlugin {
            private const string regex = "\\bhttps?://[^\\s]+\\b";
            private const uint[] good_statuses = {
                Soup.Status.CANCELLED,
                Soup.Status.OK
            };

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

            private string? get_title(Xml.Node* data) {
                for (var node = data->children; node != null; node = node->next) {
                    if (node->type == Xml.ElementType.ELEMENT_NODE) {
                        if (node->name == "title")
                            return node->get_content();
                        else if (node->children != null) {
                            var result = get_title(node);
                            if (result != null)
                                return result;
                        }
                    }
                }
                return null;
            }

            public override void exec(Prpl.Message msg) {
                var sniffer = new Soup.ContentSniffer();
                var rx = new Regex(regex, RegexCompileFlags.CASELESS);
                MatchInfo mi;
                rx.match(msg.text, 0, out mi);
                foreach (var url in mi.fetch_all()) {
                    var uri = new Soup.URI(url);
                    this.session.prefetch_dns(uri.get_host(), null, (addr, status) => {
                        if (status == Soup.Status.OK) {
                            var inet_addr = (addr.get_gsockaddr() as InetSocketAddress).get_address();
                            if (!(inet_addr.is_link_local ||
                                  inet_addr.is_loopback ||
                                  inet_addr.is_multicast ||
                                  inet_addr.is_site_local ||
                                  inet_addr.is_any)) {
                                var message = new Soup.Message("GET", url);
                                size_t recv_length = 0;
                                message.got_chunk.connect((buf) => {
                                    recv_length += buf.length;
                                    if (recv_length > 40960)
                                        this.session.cancel_message(message, Soup.Status.CANCELLED);
                                });
                                this.session.queue_message(message, (_, __) => {
                                    if (message.status_code in good_statuses) {
                                        var data = message.response_body.flatten();
                                        var type = sniffer.sniff(message, data, null);
                                        var readable = type.dup();
                                        if (message.status_code == 200)
                                            readable += readable_size(data.length);
                                        else if (message.response_headers.get_one("content-length") != null)
                                            readable += readable_size(double.parse(message.response_headers.get_one("content-length")));
                                        if (type == "text/html") {
                                            var text = (string) data.data;
                                            string? title = null;
                                            var doc = Html.Doc.read_doc(text, "", null,
                                                Html.ParserOption.RECOVER|Html.ParserOption.NOERROR|Html.ParserOption.NOWARNING);
                                            if (doc != null) {
                                                var doc_root = doc->get_root_element();
                                                if (doc_root != null)
                                                    title = get_title(doc_root);
                                            }
                                            if (title != null) {
                                                title = /\s+/s.replace(title, -1, 0, " ").strip();
                                                readable = @"$(title) [$(readable)]";
                                            }
                                        }
                                        msg.send(readable);
                                    }
                                });
                            }
                        }
                    });
                }
            }
        }
    }
}
