namespace JiyuuBot {
    public class ReplyBuilder : Object {
        public string prefix {construct; get; default="";}
        public string word_delimiter {set; get; default=" ";}
        public string sentence_delimiter {set; get; default=" | ";}
        public bool capitalize_sentences {set; get; default=true;}

        internal Array<Array<string>> sentences = new Array<Array<string>>();
        internal Array<string> current_sentence = new Array<string>();

        [PrintfFormat]
        public void add(string word, ...) {
            current_sentence.append_val(word.vprintf(va_list()));
        }

        public void end_sentence() {
            if (current_sentence.length == 0)
                return;

            sentences.append_val(current_sentence);
            current_sentence = new Array<string>();
        }

        public string build_reply() {
            if (current_sentence.length > 0)
                end_sentence();

            string[] built_sentences = {};
            foreach (var words in sentences.data) {
                var sentence = string.joinv(word_delimiter,
                    (string?[]?) words.data);

                if (sentence.length == 0)
                    continue;

                if (capitalize_sentences) {
                    unichar lead;
                    int index = 0;
                    while (sentence.get_next_char(ref index, out lead)
                        && !lead.isgraph()) {}

                    if (lead.isalpha()) {
                        var title_case = lead.totitle().to_string();
                        return_if_fail(title_case != null);

                        sentence = sentence.splice(sentence.index_of_char(lead),
                            index, (!) title_case);
                    }
                }

                built_sentences += sentence;
            }

            sentences = new Array<Array<string>>();

            return prefix + string.joinv(sentence_delimiter,
                (string?[]?) built_sentences);
        }

        [PrintfFormat]
        public ReplyBuilder.with_prefix(string prefix, ...) {
            Object(prefix: prefix.vprintf(va_list()));
        }
    }
}
