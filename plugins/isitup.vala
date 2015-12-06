using JiyuuBot;

class isitup : Plugins.BasePlugin {
    public override void activate() {
        help.add("isitup", "checks whether supplied domains are responsive");
    }

    public override bool should_exec(Prpl.Message msg) {
        return msg.command("isup") || msg.command("isitup");
    }

    public override void exec(Prpl.Message msg) {
        foreach (var domain in msg.get_args()) {
            domain = /\w+:\/\//.replace(domain, -1, 0, "");
            domain = domain.split("/")[0];
            var message = new Soup.Message("GET", @"https://isitup.org/$domain.json");
            this.session.queue_message(message, (_, __) => {
                var parser = new Json.Parser();
                parser.load_from_data((string) message.response_body.flatten().data);
                var data = parser.get_root().get_object();

                var status_code = data.get_int_member("status_code");
                if (status_code == 1)
                    msg.send("%s (%s) is up - %0.fms".printf(data.get_string_member("domain"),
                                                           data.get_string_member("response_ip"),
                                                           data.get_double_member("response_time")*1000));
                else if (status_code == 2)
                    msg.send("%s (%s) is down".printf(data.get_string_member("domain"),
                                                      data.get_string_member("response_ip")));
                else
                    msg.send("%s doesn't appear to exist".printf(data.get_string_member("domain")));
            });
        }
    }
}

public Type[] register_plugin() {
    return {typeof(isitup)};
}
