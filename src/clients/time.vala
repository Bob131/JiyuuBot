class TimeOptions : JiyuuBot.CommandOptions {
    public bool city = false;
    public string tzid = "";

    construct {
        this.allow_extra_args = true;
        this.add_option("city", ref city, "Display the current time for a city",
            "Syndey", 'c');
        this.add_option("tz", ref tzid,
            "Display the current time for an IANA TZID or ISO 8601 offset",
            "Australia/Sydney", 't');
    }
}

int main(string[] args) {
    var client = new JiyuuBot.CommandClient<TimeOptions>({"time"});
    client.description =
        "Display the current time in different parts of the world";

    var search = new JWeather.CitySearch();

    client.command_invoked.connect((context, options) => {
        var reply = "The current time %s is ";

        if (options.city) {
            string city_name;
            var city = search.find_by_name(
                string.joinv(" ", (string?[]?) options.positional_arguments),
                out city_name);

            var weather_timezone = city.get_timezone();
            if (weather_timezone == null) {
                context.reply.begin(
                    @"$city_name doesn't have an associated time zone");
                return;
            }

            options.tzid = ((!) weather_timezone).get_tzid();
            reply = reply.printf(@"in $city_name");
        } else if (options.tzid != "") {
            if (options.extra_args(context))
                return;

            reply = reply.printf(@"for $(options.tzid)");
        } else
            assert_not_reached();

        var timezone = new TimeZone(options.tzid);
        var foreign_time = new DateTime.now(timezone);

        reply += foreign_time.format("%H:%M on a %A");
        reply += " (";

        if (options.city)
            reply += @"$(options.tzid), ";

        var offset = foreign_time.get_utc_offset() / TimeSpan.SECOND;
        var offset_time = Time.gm((time_t) offset.abs());
        reply += "UTC%c%s)".printf(offset < 0 ? '-' : '+',
            offset_time.format("%H:%M"));

        context.reply.begin(reply);
    });

    var app = new JiyuuBot.ClientApp();
    app.register(client);

    return app.run(args);
}
