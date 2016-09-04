%%{
  machine metar_scanner;

  bearing     = digit{3};

  wind_speed = digit{2,3} > MatchStart;
  gust       = "G" wind_speed % {
    report->wind->gust_speed = g_new(gdouble, 1);
    *report->wind->gust_speed = g_strtod(MATCH, NULL);
  };

  wind = (
    (bearing | "VRB") > MatchStart % {
      report->wind->direction = jweather_metar_bearing_from_bearing(MATCH);
    }
    wind_speed % {
      report->wind->speed = g_strtod(MATCH, NULL);
    }
    gust?
    speed_units > MatchStart % {
      jweather_metar_wind_set_speed_units(report->wind, MATCH);
    }
    (
      space
      bearing > MatchStart % {
        report->wind->first_extreme = g_new(JWeatherMetarBearing, 1);
        *report->wind->first_extreme =
          jweather_metar_bearing_from_bearing(MATCH);
      }
      "V"
      bearing > MatchStart % {
        report->wind->second_extreme = g_new(JWeatherMetarBearing, 1);
        *report->wind->second_extreme =
          jweather_metar_bearing_from_bearing(MATCH);
      }
    )?
  ) > {
    if (!report->wind)
      report->wind = jweather_metar_wind_new();
  };
}%%
