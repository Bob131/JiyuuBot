namespace JiyuuBot {
    public const string CLIENT = "so.bob131.JiyuuBot.Client";

    [DBus (name = "so.bob131.JiyuuBot.Client")]
    public interface Client : Object {
        public abstract async void handle_message(
            MessageContext context) throws Error;
    }
}
