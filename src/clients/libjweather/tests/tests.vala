public static int main(string[] args) {
    Test.init(ref args);
    Test.set_nonfatal_assertions();

    Test.add_func("/libjweather/citysearch/sydney", () => {
        var citysearch = new JWeather.CitySearch();

        string name;
        var location = citysearch.find_by_name("sydney", out name);

        assert (name == "Sydney, New South Wales, Australia");
        assert (location.get_name() == "Sydney");
    });

    Test.add_func("/libjweather/citysearch/bisbne", () => {
        var citysearch = new JWeather.CitySearch();

        string name;
        var location = citysearch.find_by_name("bisbne", out name);

        assert (name == "Brisbane, Queensland, Australia");
        assert (location.get_name() == "Brisbane");
    });

    Test.add_func("/libjweather/metar/location-test", () => {
        var citysearch = new JWeather.CitySearch();
        var location = citysearch.find_by_name("vilnius");
        var wait = true;

        JWeather.Metar.Report.from_location.begin(location, (obj, res) => {
            try {
                var result = JWeather.Metar.Report.from_location.end(res);
                assert (result.city_name != null
                    && (!) result.city_name == "Vilnius, Lithuania");
                assert (result.station_code == "EYVI");
            } catch (IOError e) {
                if (e.message.has_prefix("Failed to fetch"))
                    Test.incomplete(e.message);
                else {
                    message(e.message);
                    Test.fail();
                }
            }
            wait = false;
        });

        while (wait)
            MainContext.default().iteration(true);
    });

    Test.add_func("/libjweather/metar/station-code-test", () => {
        var wait = true;

        JWeather.Metar.Report.from_station_code.begin("KDEN", (obj, res) => {
            try {
                var result = JWeather.Metar.Report.from_station_code.end(res);
                assert (result.city_name != null
                    && (!) result.city_name == "Denver, Colorado, United States");
                assert (result.station_code == "KDEN");
            } catch (IOError e) {
                if (e.message.has_prefix("Failed to fetch"))
                    Test.incomplete(e.message);
                else {
                    message(e.message);
                    Test.fail();
                }
            }
            wait = false;
        });

        while (wait)
            MainContext.default().iteration(true);
    });

    Test.run();
    return 0;
}
