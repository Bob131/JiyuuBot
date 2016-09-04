%%{
  machine metar_scanner;

  cloud = (
    ("FEW" | "SCT" | "BKN" | "OVC") > MatchStart % {
      CLOUD->cover = jweather_metar_cloud_cover_from_string(MATCH);
      CLOUD->valid = TRUE;
    }
    ("///" | digit{3} > MatchStart % {
      CLOUD->height = g_new(guint, 1);
      *CLOUD->height = atoi(MATCH);
    })
    (
      ("CB" | "TCU" | "ST" | "SC" | "CU" | "NS" | "AC" | "AS") > MatchStart % {
        CLOUD->type = g_new(JWeatherMetarConvectiveCloud, 1);
        *CLOUD->type = jweather_metar_convective_cloud_from_string(MATCH);
      }
      | "///"
    )?
  ) > {add_cloud(report);};

  other_sky =
    ("CLR" | "SKC" | "NSC" | "NCD") > MatchStart % {
      add_cloud(report);
      CLOUD->cover = jweather_metar_cloud_cover_from_string(MATCH);
    }
    | ("VV" digit{3});
}%%
