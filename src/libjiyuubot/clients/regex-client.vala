namespace JiyuuBot {
    public class RegexClient : Object, Client {
        public Regex trigger {construct; get;}

        public signal void regex_match(MessageContext context, MatchInfo match);

        internal async void handle_message(MessageContext context)
            throws Error
        {
            string text;
            if (!context.is_normal(out text))
                return;

            MatchInfo match;
            if (trigger.match(text, 0, out match))
                regex_match(context, match);
        }

        public RegexClient(Regex trigger) {
            Object(trigger: trigger);
        }
    }
}
