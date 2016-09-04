%%{
  machine metar_scanner;

  intensity  = ("-" | "+" | "VC") > MatchStart % {
    GROUP->intensity = jweather_metar_intensity_from_string(MATCH);
  };

  descriptor = ("MI" | "PR" | "BC" | "DR" | "BL" | "SH" | "FZ" | "TS")
    > MatchStart % {
      GROUP->descriptors = g_list_append(GROUP->descriptors,
        GINT_TO_POINTER(jweather_metar_descriptor_from_string(MATCH)));
    };

  precipitation = ("DZ" | "RA" | "S" . [NG] | "IC" | "PL" | "G" . [RS] | "UP")
    > MatchStart % {
      if (!GROUP->phenomena)
        GROUP->phenomena = jweather_metar_phenomena_new(
          JWEATHER_METAR_TYPE_PRECIPITATION);
      GROUP->phenomena->value = g_list_append(GROUP->phenomena->value,
        GINT_TO_POINTER(jweather_metar_precipitation_from_string(MATCH)));
    };

  obscuration = ("BR" | "FG" | "FU" | "VA" | "DU" | "SA" | "HZ" | "PY")
    > MatchStart % {
      GROUP->phenomena = jweather_metar_phenomena_new(
        JWEATHER_METAR_TYPE_OBSCURATION);
      GROUP->phenomena->value =
        GINT_TO_POINTER(jweather_metar_obscuration_from_string(MATCH));
    };

  other = ("PO" | "SQ" | "FC" | "SS" | "DS") > MatchStart % {
    GROUP->phenomena = jweather_metar_phenomena_new(JWEATHER_METAR_TYPE_OTHER);
    GROUP->phenomena->value =
      GINT_TO_POINTER(jweather_metar_other_from_string(MATCH));
  };

  phenomena = (precipitation{1,3} | obscuration | other);

  weather = (
    intensity?
    descriptor*
    (phenomena | descriptor)
  ) > {
    report->weather = g_list_prepend(report->weather,
      jweather_metar_observation_new());
  };
}%%
