JWeather.CitySearch search;

class WeatherOptions : JiyuuBot.CommandOptions {
    public bool city = false;
    public string metar = "";

    construct {
        this.allow_extra_args = true;
        this.add_option("city", ref city, "Get the current weather for a city",
            "Sydney", 'c');
        this.add_option("metar", ref metar,
            "Get the current weather from an ICAO METAR station", "YSSY", 'm');
    }
}

string mangle_city_name(string name) {
    var split_name = name.split(", ");
    string[] unique_parts = {};

    foreach (var part in split_name)
        if (!(part in unique_parts))
            unique_parts += part;

    return string.joinv(", ", (string?[]?) unique_parts);
}

string mangle_enum_name(int val, Type @enum, string delimiter = " ")
    requires (@enum.is_enum())
{
    var @class = (EnumClass) @enum.class_ref();
    var enum_value = @class.get_value(val);
    return_if_fail(enum_value != null);
    return ((!) enum_value).value_nick.replace("-", delimiter).strip().down();
}

async void handle_invocation(
    JiyuuBot.MessageContext context,
    WeatherOptions options) throws Error
{
    JWeather.Metar.Report report;

    if (options.city) {
        var city = search.find_by_name(
            string.joinv(" ", (string?[]?) options.positional_arguments));
        report = yield JWeather.Metar.Report.from_location(city);
    } else {
        if (options.extra_args(context))
            return;
        report =
            yield JWeather.Metar.Report.from_station_code(options.metar);
    }

    var reply = new JiyuuBot.ReplyBuilder.with_prefix("Weather %s: ",
        report.city_name != null ?
            @"in $(mangle_city_name((!) report.city_name))"
            : @"from $(report.station_code)");

    unowned List<JWeather.Metar.Observation>? element = report.weather;

    for (var i = 0; i < 3 && element != null; i++) {
        var observation = ((!) element).data;

        switch (observation.intensity) {
            case JWeather.Metar.Intensity.MODERATE:
                break;
            case JWeather.Metar.Intensity.NEAR_BY:
                reply.add("near-by");
                break;
            default:
                reply.add(mangle_enum_name(observation.intensity,
                    typeof(JWeather.Metar.Intensity)));
                break;
        }

        foreach (var descriptor in observation.descriptors)
            switch (descriptor) {
                case JWeather.Metar.Descriptor.PATCHES:
                    reply.add("patches of");
                    break;
                case JWeather.Metar.Descriptor.SHOWERS:
                    reply.add(observation.phenomena == null ?
                        "showers"
                        : "showering");
                    break;
                case JWeather.Metar.Descriptor.THUNDERSTORM:
                    reply.add(observation.phenomena == null ?
                        "thunderstorms"
                        : "stormy");
                    break;
                default:
                    reply.add(mangle_enum_name(descriptor,
                        typeof(JWeather.Metar.Descriptor)));
                    break;
            }

        if (observation.phenomena != null) {
            var type = ((!) observation.phenomena).type;

            if (type == typeof(JWeather.Metar.Precipitation)) {
                unowned List<JWeather.Metar.Precipitation> precips =
                    (List) ((!) observation.phenomena).@value;
                foreach (var p in precips)
                    switch (p) {
                        case JWeather.Metar.Precipitation.UNKNOWN:
                            reply.add("unknown precipitation");
                            break;
                        case JWeather.Metar.Precipitation.RAIN:
                            reply.add("rains");
                            break;
                        default:
                            reply.add(mangle_enum_name(p,
                                typeof(JWeather.Metar.Precipitation)));
                            break;
                    }

            } else if (type == typeof(JWeather.Metar.Obscuration)) {
                var phenomena = (JWeather.Metar.Obscuration)
                    ((!) observation.phenomena).@value;
                switch (phenomena) {
                    case JWeather.Metar.Obscuration.FOG:
                        reply.add(observation.intensity
                            == JWeather.Metar.Intensity.MODERATE
                            && observation.descriptors.length() == 0 ?
                                "foggy" : "fog");
                        break;
                    default:
                        reply.add(mangle_enum_name(phenomena,
                            typeof(JWeather.Metar.Obscuration)));
                        break;
                }

            } else if (type == typeof(JWeather.Metar.Other)) {
                var phenomena = (JWeather.Metar.Other)
                    ((!) observation.phenomena).@value;
                switch (phenomena) {
                    case JWeather.Metar.Other.FUNNEL_CLOUD:
                        reply.add("tornadoes");
                        break;
                    default:
                        reply.add(mangle_enum_name(phenomena,
                            typeof(JWeather.Metar.Other)));
                        break;
                }
            }
        }

        element = ((!) element).next;

        if (element != null)
            switch (i) {
                case 0:
                    reply.add("with");
                    break;
                case 1:
                    reply.add("and");
                    break;
                default:
                    break;
            }
    }

    reply.new_sentence();

    if (report.clouds.length() > 0) {
        var cover = (JWeather.Metar.CloudCover) 0;
        foreach (var cloud in report.clouds)
            if (cloud.cover > cover)
                cover = cloud.cover;

        string format;
        switch (cover) {
            case JWeather.Metar.CloudCover.FEW:
            case JWeather.Metar.CloudCover.SCATTERED:
            case JWeather.Metar.CloudCover.BROKEN:
                format = "%s clouds";
                break;
            case JWeather.Metar.CloudCover.CLEAR:
                format = "%s skies";
                break;
            default:
                format = "%s";
                break;
        }

        reply.add(format, mangle_enum_name(cover,
            typeof(JWeather.Metar.CloudCover)));
        reply.new_sentence();
    }

    // 6km/h should cut out 0 and 1 on the Beaufort scale
    if (report.wind != null && ((!) report.wind).speed >= 6) {
        var wind = (!) report.wind;

        var beaufort_scale = JWeather.Metar.get_beaufort(wind.speed);
        return_if_fail(beaufort_scale > 1);

        string description;

        // a slight mangling of the true category names to try and improve
        // clarity
        switch (beaufort_scale) {
            case 2:
                description = "light %serly breeze";
                break;
            case 3:
                description = "gentle %serly breeze";
                break;
            case 4:
            case 5:
                description = "%serly breeze";
                break;
            case 6:
            case 7:
                description = "strong %serly winds";
                break;
            case 8:
            case 9:
                description = "%serly gale-force winds";
                break;
            case 10:
            case 11:
                description = "violent %serly winds";
                break;
            default:
                description = "hurricane-force winds from the %s";
                break;
        }

        reply.add(description, mangle_enum_name(wind.direction,
            typeof(JWeather.Metar.Bearing), "-"));

        if (wind.gust_speed != null) {
            reply.add("with");
            var gust_speed = (!) wind.gust_speed;
            switch (JWeather.Metar.get_beaufort(gust_speed)) {
                case 0:
                case 1:
                case 2:
                case 3:
                case 4:
                case 5:
                    break;
                case 6:
                case 7:
                    reply.add("strong");
                    break;
                case 8:
                case 9:
                    reply.add("gale-force");
                    break;
                case 10:
                case 11:
                    reply.add("storm-force");
                    break;
                default:
                    reply.add("hurricane-force");
                    break;
            }
            reply.add("gusts of %dkm/h", (int) gust_speed);
        }

        reply.new_sentence();
    }

    if (report.temperature != null) {
        reply.add("%d°C", (!) report.temperature);
        if (report.dew_point != null)
            reply.add("with a dew point of %d°C", (!) report.dew_point);
        reply.new_sentence();
    }

    if (report.visibility != null) {
        reply.add("visibility:");

        var vis = (!) report.visibility;
        if (vis == JWeather.Metar.PERFECT_VISIBILITY)
            reply.add("more than 10km");
        else if (vis < 1000)
            reply.add("%um", vis);
        else
            reply.add("%.1fkm".printf(vis / 1000d).replace(".0", ""));

        reply.new_sentence();
    }

    if (report.automated || report.corrected)
        reply.add(report.automated ? "automated" : "corrected");

    reply.add(report.time.format("observation from %Y-%m-%d %H:%M UTC"));

    if (report.city_name != null)
        reply.add("(ICAO %s)", report.station_code);

    yield context.reply(reply.build_reply());
}

int main(string[] args) {
    search = new JWeather.CitySearch();

    var client = new JiyuuBot.CommandClient<WeatherOptions>({"weather"});
    client.description = "Show the weather in different parts of the world";
    client.command_invoked.connect((context, options) => {
        handle_invocation.begin(context, options, (obj, res) => {
            try {
                handle_invocation.end(res);
            } catch (Error e) {
                context.reply.begin(e.message);
                warning(e.message); // print so the syslog is less confusing
            }
        });
    });

    var app = new JiyuuBot.ClientApp();
    app.register(client);

    return app.run(args);
}
