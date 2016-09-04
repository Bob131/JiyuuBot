namespace JWeather.Metar {
    public enum Intensity {
        LIGHT,
        MODERATE,
        HEAVY,
        NEAR_BY;

        public static Intensity from_string(string input) {
            switch (input) {
                case "-":
                    return LIGHT;
                case "+":
                    return HEAVY;
                case "VC":
                    return NEAR_BY;
                default:
                    return_if_reached();
            }
        }
    }

    public enum Descriptor {
        SHALLOW,
        PARTIAL,
        PATCHES,
        LOW_DRIFTING,
        BLOWING,
        SHOWERS,
        THUNDERSTORM,
        FREEZING;

        public static Descriptor from_string(string input) {
            switch (input) {
                case "MI":
                    return SHALLOW;
                case "PR":
                    return PARTIAL;
                case "BC":
                    return PATCHES;
                case "DR":
                    return LOW_DRIFTING;
                case "BL":
                    return BLOWING;
                case "SH":
                    return SHOWERS;
                case "TS":
                    return THUNDERSTORM;
                case "FZ":
                    return FREEZING;
                default:
                    return_if_reached();
            }
        }
    }

    public enum Precipitation {
        UNKNOWN,
        DRIZZLE,
        RAIN,
        SNOW,
        SNOW_GRAINS,
        ICE_CRYSTALS,
        ICE_PELLETS,
        HAIL,
        SMALL_HAIL;

        public static Precipitation from_string(string input) {
            switch (input) {
                case "DZ":
                    return DRIZZLE;
                case "RA":
                    return RAIN;
                case "SN":
                    return SNOW;
                case "SG":
                    return SNOW_GRAINS;
                case "IC":
                    return ICE_CRYSTALS;
                case "PL":
                    return ICE_PELLETS;
                case "GR":
                    return HAIL;
                case "GS":
                    return SMALL_HAIL;
                case "UP":
                    return UNKNOWN;
                default:
                    return_if_reached();
            }
        }
    }

    public enum Obscuration {
        MIST,
        FOG,
        SMOKE,
        ASH,
        DUST,
        SAND,
        HAZE,
        SPRAY;

        public static Obscuration from_string(string input) {
            switch (input) {
                case "BR":
                    return MIST;
                case "FG":
                    return FOG;
                case "FU":
                    return SMOKE;
                case "VA":
                    return ASH;
                case "DU":
                    return DUST;
                case "SA":
                    return SAND;
                case "HZ":
                    return HAZE;
                case "PY":
                    return SPRAY;
                default:
                    return_if_reached();
            }
        }
    }

    public enum Other {
        WHIRLS,
        SQUALLS,
        FUNNEL_CLOUD,
        SANDSTORM,
        DUSTSTORM;

        public static Other from_string(string input) {
            switch (input) {
                case "PO":
                    return WHIRLS;
                case "SQ":
                    return SQUALLS;
                case "FC":
                    return FUNNEL_CLOUD;
                case "SS":
                    return SANDSTORM;
                case "DS":
                    return DUSTSTORM;
                default:
                    return_if_reached();
            }
        }
    }

    // Wrap it in a class so the generic type is stored. Vala generates code
    // that requires the type to be specified on instantiation, which is why
    // we're doing this in a class separate from Observation.
    public class Phenomena {
        public Type type;
        public void* @value;

        public Phenomena(Type type) {
            this.type = type;
        }
    }

    public class Observation {
        public Intensity intensity = Intensity.MODERATE;
        public List<Descriptor> descriptors;
        public Phenomena? phenomena;
    }
}
