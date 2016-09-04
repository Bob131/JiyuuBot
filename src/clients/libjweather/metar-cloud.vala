namespace JWeather.Metar {
    public enum CloudCover {
        FEW,
        SCATTERED,
        BROKEN,
        OVERCAST,

        CLEAR,
        NO_SIGNIFICANT_CLOUDS,
        NO_CLOUDS_DETECTED;

        public static CloudCover from_string(string input) {
            switch (input) {
                case "FEW":
                    return FEW;
                case "SCT":
                    return SCATTERED;
                case "BKN":
                    return BROKEN;
                case "OVC":
                    return OVERCAST;
                case "CLR":
                case "SKC":
                    return CLEAR;
                case "NSC":
                    return NO_SIGNIFICANT_CLOUDS;
                case "NCD":
                    return NO_CLOUDS_DETECTED;
                default:
                    return_if_reached();
            }
        }
    }

    public enum ConvectiveCloud {
        // standard METAR cloud types
        CUMULONIMBUS,
        TOWERING_CUMULUS,

        // supposed to be for SIGWX _only_, but some METAR reports contain them
        // anyway
        STRATUS,
        STRATOCUMULUS,
        CUMULUS,
        NIMBO_STRATUS,
        ALTO_CUMULUS,
        ALTO_STRATUS;

        public static ConvectiveCloud from_string(string input) {
            switch (input) {
                case "CB":
                    return CUMULONIMBUS;
                case "TCU":
                    return TOWERING_CUMULUS;
                case "ST":
                    return STRATUS;
                case "SC":
                    return STRATOCUMULUS;
                case "CU":
                    return CUMULUS;
                case "NS":
                    return NIMBO_STRATUS;
                case "AC":
                    return ALTO_CUMULUS;
                case "AS":
                    return ALTO_STRATUS;
                default:
                    return_if_reached();
            }
        }
    }

    public class Cloud {
        public CloudCover cover;
        public uint? height;
        public ConvectiveCloud? type;

        // this lets us check whether this cloud really is FEW with no height
        // or type, or whether this was mistakenly added to a list
        internal bool valid = false;
    }
}
