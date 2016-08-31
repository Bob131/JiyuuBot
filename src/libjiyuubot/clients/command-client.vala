namespace JiyuuBot {
    public const string OPTION_REMAINING = "";

    public class CommandOptions : Object {
        public string[] arguments {construct; get;}

        [CCode (array_length = false, array_null_terminated = true)]
        internal string[] remaining_args = {};

        public bool allow_extra_args {set; get; default=false;}
        public string[] positional_arguments {owned get {
            return allow_extra_args ? remaining_args : new string[] {};
        }}

        internal OptionContext option_context;
        internal OptionGroup help_group;
        internal bool show_help = false;

        internal OptionArg? value_to_option_arg<V>(ref V val) {
            switch (typeof(V).name()) {
                case "gboolean":
                    return OptionArg.NONE;
                case "gchararray":
                    return OptionArg.STRING;
                case "gint64":
                    return OptionArg.INT64;
                default:
                    return null;
            }
        }

        public void add_option<V>(
            string long_name,
            ref V arg_data,
            string description = "",
            string? arg_description = null,
            char short_name = 0)
        {
            if (long_name == OPTION_REMAINING) {
                allow_extra_args = true;
                return;
            }

            var option_arg = value_to_option_arg(ref arg_data);
            return_if_fail(option_arg != null);

            var new_options = new OptionEntry[2];
            new_options[0] = {long_name, short_name, 0, (!) option_arg,
                ref arg_data, description, arg_description};
            new_options[1] = {(string) null};

            option_context.get_main_group().add_entries(new_options);

        }

        internal void parse(ref string[] args) throws OptionError {
            option_context.parse_strv(ref args);
            if (remaining_args.length > 0 && !allow_extra_args)
                throw new OptionError.FAILED(
                    "This command does not accept positional arguments ('%s')",
                    string.joinv("', '", (string?[]?) remaining_args));
        }

        construct {
            option_context = new OptionContext(null);
            option_context.set_help_enabled(false);

            remaining_args = {};

            var catch_all = new OptionEntry[2];
            catch_all[0] = {"", 0, 0, OptionArg.STRING_ARRAY,
                ref remaining_args};
            catch_all[1] = {(string) null};
            option_context.add_main_entries(catch_all, null);

            help_group = new OptionGroup("", "", "");

            var help_options = new OptionEntry[2];
            help_options[0] = {"help", 'h', 0, OptionArg.NONE, ref show_help,
                "List options", null};
            help_options[1] = {(string) null};

            help_group.add_entries(help_options);
            option_context.add_group((owned) help_group);
        }
    }

    public class CommandClient<T> : Object, Client {
        public string[] triggers {construct; get;}
        public string? description {set; get; default=null;}

        public signal void command_invoked(
            MessageContext context,
            T options);

        internal async void handle_message(MessageContext context)
            throws Error
        {
            if (context.message.message_type != Tp.MessageType.NORMAL)
                return;

            var _text = context.message.to_text();
            if (_text == null)
                return;
            var text = (!) _text;

            if (text.length < 1)
                return;
            if (!text[0].ispunct())
                return;
            text = text[1:text.length];

            string[] args;
            ShellError? parse_error = null;

            try {
                Shell.parse_argv(text, out args);
            } catch (ShellError e) {
                parse_error = e;
                args = Regex.split_simple("\\s+", text);
            }

            if (!(args[0] in triggers))
                return;

            if (parse_error != null) {
                yield context.reply(@"Error: $(((!) parse_error).message)");
                return;
            }

            var options = (CommandOptions) Object.new(typeof(T),
                arguments: args);

            try {
                options.parse(ref args);
            } catch (OptionError e) {
                yield context.reply(@"Error: $(e.message)");
                return;
            }

            if (options.show_help) {
                var help = @"Usage: .$(options.arguments[0]) [OPTION...]";
                if (description != null)
                    help += @" - $((!) description)";

                var opts_help = options.option_context.get_help(false, null);
                foreach (var line in opts_help.split("\n"))
                    if (line.has_prefix("  -"))
                        help += @"\n$(line)";

                yield context.reply(help);

                return;
            }

            command_invoked(context, options);
        }

        public CommandClient(string[] triggers)
            requires (triggers.length > 0)
            requires (typeof(T) == typeof(CommandOptions)
                || typeof(T).is_a(typeof(CommandOptions)))
        {
            Object(triggers: triggers);
        }
    }
}
