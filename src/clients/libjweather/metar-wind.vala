namespace JWeather.Metar {
    public enum Bearing {
        NORTH,
        NORTH_EAST,
        EAST,
        SOUTH_EAST,
        SOUTH,
        SOUTH_WEST,
        WEST,
        NORTH_WEST,

        VARIABLE;

        public static Bearing from_bearing(string bearing) {
            if (bearing == "VRB")
                return VARIABLE;
            if (bearing == "360")
                return NORTH;

            // each cardinal point is 45 degrees from the next
            int result = int.parse(bearing) / 45;
            return_if_fail(NORTH <= result <= NORTH_WEST);
            return (Bearing) result;
        }
    }

    public int get_beaufort(double kilometers_per_hour) {
        var meters_per_second = kilometers_per_hour / 3.6;
        return (int) Math.round(
            Math.pow(meters_per_second / 0.836, (double) 2 / 3));
    }

    public class Wind {
        public Bearing direction;
        public double speed;
        public double? gust_speed;

        // these should only be set if direction == Bearing.VARIABLE
        public Bearing? first_extreme;
        public Bearing? second_extreme;

        // convert from units specified in `units` to km/h
        internal void set_speed_units(string units) {
            switch (units) {
                case "KMH":
                    break; // already the unit we want
                case "MPS":
                    speed *= 3.6;
                    if (gust_speed != null)
                        gust_speed *= 3.6;
                    break;
                case "KT":
                    speed *= 1.85;
                    if (gust_speed != null)
                        gust_speed *= 1.85;
                    break;
                default:
                    return_if_reached();
            }
        }
    }
}
