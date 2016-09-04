namespace JWeather {
    internal void add_ngrams(GenericSet<string> ngrams, string input, int n) {
        foreach (var str in input.normalize().casefold().split(", "))
            for (var i = 0; i < str.length; i++) {
                char[] ngram = {};
                for (var c = i; (c - i) < n && c < str.length; c++)
                    ngram += str[c];
                ngram += 0;
                ngrams.add((string) ngram);
            }
    }

    internal GenericSet<string> get_ngrams(string input) {
        var ret = new GenericSet<string>(str_hash, str_equal);
        add_ngrams(ret, input, 2);
        add_ngrams(ret, input, 3);
        return ret;
    }

    [Compact]
    internal class LocationIndex {
        public string name = "";
        public GenericSet<string> ngrams;
        public GWeather.Location location;
    }

    internal void build_city_name(GWeather.Location? _location, ref string name)
    {
        if (_location == null)
            return;
        var location = (!) _location;

        name += location.get_name();

        // don't include locations on a level higher than COUNTRY
        if (location.get_level() > GWeather.LocationLevel.COUNTRY) {
            name += ", ";
            build_city_name(location.get_parent(), ref name);
        }
    }

    public class CitySearch : Object {
        internal List<LocationIndex> cities = new List<LocationIndex>();

        public GWeather.Location find_by_name(
            string input,
            out string full_name = null)
        {
            var ngrams = get_ngrams(input);

            var highest = 0;
            unowned LocationIndex? selected = null;

            foreach (unowned LocationIndex index in cities) {
                var matches = 0;

                foreach (var ngram in index.ngrams.get_values())
                    if (ngram in ngrams)
                        matches++;

                if (matches > highest) {
                    highest = matches;
                    selected = index;
                }
            }

            full_name = ((!) selected).name;

            debug("City selected from input '%s': %s", input, full_name);

            return ((!) selected).location;
        }

        void index_cities(GWeather.Location location) {
            if (location.get_level() == GWeather.LocationLevel.CITY) {
                var index = new LocationIndex();
                build_city_name(location, ref index.name);
                index.ngrams = get_ngrams(index.name);
                index.location = location;
                cities.append((owned) index);
            }

            foreach (var child in location.get_children())
                index_cities(child);
        }

        construct {
            var world = GWeather.Location.get_world();
            if (world == null)
                error("Failed to parse Locations.xml");
            index_cities((!) world);
        }
    }
}
