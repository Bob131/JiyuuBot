class ConversionOptions : JiyuuBot.CommandOptions {
    construct {
        this.allow_extra_args = true;
    }
}

const string QUERY_PREFIX = "convert";
const string API_URL = "https://api.duckduckgo.com";
const string ANSWER_MEMBER = "Answer";

int main(string[] args) {
    var client = new JiyuuBot.CommandClient<ConversionOptions>({"convert"});
    client.description = "Perform unit conversions";
    client.command_invoked.connect((context, options) => {
        string[] query;

        if (options.positional_arguments[0] == "convert")
            query = options.positional_arguments;
        else {
            query = {"convert"};
            foreach (var arg in options.positional_arguments)
                query += arg;
        }

        var call = new Rest.Proxy("https://api.duckduckgo.com", false)
            .new_call();
        call.add_params(
            "q", string.joinv(" ", (string?[]?) query),
            "format", "json",
            "t", "JiyuuBot");

        // work in a new thread since librest's async API is broken
        new Thread<void*>("request", () => {
            try {
                call.run();
            } catch (Error e) {
                context.reply.begin(@"Request failed: $(e.message)");
                return null;
            }

            var parser = new Json.Parser();
            try {
                parser.load_from_data(call.get_payload(),
                    (ssize_t) call.get_payload_length());
            } catch (Error e) {
                context.reply.begin(@"Failed to parse response: $(e.message)");
                return null;
            }

            var _root = parser.get_root();
            return_if_fail(_root != null);
            var root = (!) _root;

            return_if_fail(root.get_node_type() == Json.NodeType.OBJECT);
            var object = root.get_object();

            string answer = "";
            if (!object.has_member(ANSWER_MEMBER)
                    || (answer = object.get_string_member(ANSWER_MEMBER)) == "")
                context.reply.begin("Unknown conversion");
            else
                context.reply.begin(@"$answer (Results from DuckDuckGo)");

            return null;
        });
    });

    var app = new JiyuuBot.ClientApp();
    app.register(client);

    return app.run(args);
}
