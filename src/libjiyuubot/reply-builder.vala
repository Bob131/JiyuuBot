namespace JiyuuBot {
    internal class Sentence {
        public Array<string> words = new Array<string>();
        public bool note;
        public string parens;
    }

    public class ReplyBuilder : Object {
        public string prefix {construct; get;}
        public string word_delimiter {set; get; default=" ";}
        public string sentence_delimiter {set; get; default=" | ";}
        public bool capitalize_sentences {set; get; default=true;}

        internal Array<Sentence> sentences = new Array<Sentence>();
        internal Sentence current_sentence = new Sentence();

        [PrintfFormat]
        public void add(string word, ...) {
            current_sentence.words.append_val(word.vprintf(va_list()));
        }

        public void new_sentence() {
            if (current_sentence.words.length == 0)
                return;

            sentences.append_val(current_sentence);
            current_sentence = new Sentence();
        }

        public void new_note(string parens = "()")
            requires (parens.char_count() == 2)
        {
            new_sentence();
            current_sentence.note = true;
            current_sentence.parens = parens;
        }

        public string build_reply() {
            if (current_sentence.words.length > 0)
                new_sentence();

            string[] built_sentences = {};
            foreach (var sentence in sentences.data) {
                var built_sentence = string.joinv(word_delimiter,
                    (string?[]?) sentence.words.data);

                if (built_sentence.length == 0)
                    continue;

                if (capitalize_sentences) {
                    unichar lead;
                    int index = 0;
                    while (built_sentence.get_next_char(ref index, out lead)
                        && !lead.isalnum()) {}

                    if (lead.isalpha()) {
                        var title_case = lead.totitle().to_string();
                        return_if_fail(title_case != null);

                        built_sentence = built_sentence.splice(
                            built_sentence.index_of_char(lead), index,
                            (!) title_case);
                    }
                }

                if (sentence.note)
                    built_sentence =
                        (!) sentence.parens.get_char(0).to_string()
                        + built_sentence
                        + (!) sentence.parens.get_char(1).to_string();

                built_sentences += built_sentence;
            }

            var ret = "";
            for (var i = 0; i < built_sentences.length; i++) {
                ret += built_sentences[i];
                if ((string?) built_sentences[i + 1] != null)
                    if (sentences.data[i + 1].note)
                        ret += word_delimiter;
                    else
                        ret += sentence_delimiter;
            }

            sentences = new Array<Sentence*>();

            return prefix + ret;
        }

        public ReplyBuilder() {
            Object(prefix: "");
        }

        [PrintfFormat]
        public ReplyBuilder.with_prefix(string prefix, ...) {
            Object(prefix: prefix.vprintf(va_list()));
        }
    }
}
