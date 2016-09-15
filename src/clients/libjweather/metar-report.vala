extern void scan_metar(JWeather.Metar.Report report, string metar_string)
    throws IOError;

const string METAR_URI =
    "http://tgftp.nws.noaa.gov/data/observations/metar/stations/%s.TXT";

Soup.Session? session = null;
Soup.Session get_session() {
    if (session == null)
        session = new Soup.Session();
    return (!) session;
}

namespace JWeather.Metar {
    public const uint PERFECT_VISIBILITY = 9999;

    public class Report : Object {
        string _metar_string;
        public string metar_string {get {return _metar_string;}}

        internal string? _city_name;
        public string? city_name {get {return _city_name;}}
        internal void city_name_from_location(GWeather.Location location) {
            var temp_name = "";
            build_city_name(location, ref temp_name);
            if (temp_name != "")
                _city_name = temp_name;
        }

        // if these are null, they should be set by the parser
        internal string? _station_code;
        public string station_code {get {
            return_if_fail(_station_code != null);
            return (!) _station_code;
        }}

        internal DateTime? _time;
        public DateTime time {get {
            return_if_fail(_time != null);
            return (!) _time;
        }}

        // default to false
        internal bool _automated;
        public bool automated {get {return _automated;}}
        internal bool _corrected;
        public bool corrected {get {return _corrected;}}

        internal void modifier(string token) {
            switch (token) {
                case "AUTO":
                    _automated = true;
                    break;
                case "COR":
                    _corrected = true;
                    break;
                default:
                    return_if_reached();
            }
        }

        public Wind? wind;

        internal uint? _visibility;
        public uint? visibility {get {return _visibility;}}

        internal void set_visibility(int meters)
            requires (meters > 0)
        {
            // ignore smaller values
            if (_visibility != null && meters < (!) _visibility)
                return;
            _visibility = uint.min(PERFECT_VISIBILITY, (uint) meters);
        }

        public List<Observation> weather;

        public List<Cloud> clouds;

        internal int? _temperature;
        public int? temperature {get {return _temperature;}}
        internal int? _dew_point;
        public int? dew_point {get {return _dew_point;}}

        // Vala generates broken code when using async constructors, so a lot
        // of constructor logic lives in separate methods

        internal async string station_code_setup(string icao_station_code)
            throws IOError
        {
            _station_code = icao_station_code;

            if (_city_name == null) {
                var world = GWeather.Location.get_world();
                if (world != null) {
                    GWeather.Location? location =
                        ((!) world).find_by_station_code(icao_station_code);
                    while (location != null && ((!) location).get_level()
                            != GWeather.LocationLevel.CITY)
                        location = ((!) location).get_parent();
                    if (location != null)
                        city_name_from_location((!) location);
                }
            }

            var uri = METAR_URI.printf(icao_station_code);
            var message = new Soup.Message("GET", uri);

            get_session().queue_message(message, () => {
                station_code_setup.callback();
            });
            yield;

            if (message.status_code != Soup.Status.OK)
                throw new IOError.FAILED("Failed to fetch '%s': %s (code %u)",
                    uri, message.reason_phrase, message.status_code);

            var contents = (string) message.response_body.flatten().data;
            var lines = contents.split("\n");

            return_if_fail(lines.length > 1);

            var time = lines[0];
            var metar_report = lines[1];

            debug("Fetched time: %s", time);

            int year = 0, month = 0, day = 0, hour = 0, minute = 0;
            time.scanf("%d/%d/%d %d:%d", &year, &month, &day, &hour, &minute);
            _time = new DateTime.utc(year, month, day, hour, minute, 0);

            return metar_report;
        }

        internal void parse_metar(string metar_string) throws IOError {
            debug("Parsing METAR string: %s", metar_string);

            _metar_string = metar_string;

            scan_metar(this, metar_string);

            weather.reverse();
            clouds.reverse();

            Observation[] obs_to_remove = {};
            foreach (var entry in weather)
                if (entry.intensity == Intensity.MODERATE
                        && entry.descriptors.length() == 0
                        && entry.phenomena == null)
                    obs_to_remove += entry;
            foreach (var entry in obs_to_remove)
                weather.remove(entry);

            Cloud[] clouds_to_remove = {};
            foreach (var entry in clouds)
                if (entry.cover == CloudCover.FEW && !entry.valid)
                    clouds_to_remove += entry;
            foreach (var entry in clouds_to_remove)
                clouds.remove(entry);
        }

        internal Report() {}

        public async static Report from_location(GWeather.Location location)
            throws IOError
        {
            var report = new Report();

            report.city_name_from_location(location);

            GWeather.Location? _station = null;
            foreach (var possible_station in location.get_children())
                if (possible_station.get_level() ==
                        GWeather.LocationLevel.WEATHER_STATION) {
                    _station = possible_station;
                    break;
                }

            if (_station == null)
                throw new IOError.FAILED("%s does not have a METAR station",
                    report._city_name == null ?
                        "Location"
                        : (!) report._city_name);

            var station = (!) _station;

            if (station.get_code() == null)
                throw new IOError.FAILED("METAR station for %s has no code. %s",
                    report._city_name == null ?
                        "location"
                        : (!) report._city_name,
                    "This is a bug in libgweather.");

            report.parse_metar(yield report.station_code_setup(
                (!) station.get_code()));

            return report;
        }

        public async static Report from_station_code(string icao_station_code)
            throws IOError
        {
            var report = new Report();
            report.parse_metar(yield report.station_code_setup(
                icao_station_code.up().strip()));
            return report;
        }

        public static Report from_string(string metar_string) throws IOError {
            var report = new Report();
            report.parse_metar(metar_string);
            return report;
        }
    }
}
