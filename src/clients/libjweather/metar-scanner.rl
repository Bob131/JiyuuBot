#include "jweather-priv.h"

#define MATCH g_strndup(match_start, p - match_start)
#define GROUP JWEATHER_METAR_OBSERVATION(report->weather->data)
#define CLOUD JWEATHER_METAR_CLOUD(report->clouds->data)
#define TEMP ({gchar* temp = MATCH; if (temp[0] == 'M') temp[0] = '-'; temp;})

void add_cloud(JWeatherMetarReport* report) {
  report->clouds = g_list_prepend(report->clouds, jweather_metar_cloud_new());
}

%%{
  machine metar_scanner;

  action MatchStart {
    match_start = fpc;
  }

  station_id = alnum{4} > MatchStart % {
    if (!report->_station_code)
      report->_station_code = MATCH;
  };

  time =
    digit{2} > MatchStart % {day = atoi(MATCH);}
    digit{2} > MatchStart % {hour = atoi(MATCH);}
    digit{2} > MatchStart % {minute = atoi(MATCH);}
    "Z"
  % {
    if (!report->_time) {
      g_autoptr(GDateTime) now = g_date_time_new_now_utc();
      report->_time = g_date_time_new_utc(g_date_time_get_year(now),
        g_date_time_get_month(now), day, hour, minute, 0);
    }
  };

  modifier = ("AUTO" | "COR") > MatchStart % {
    jweather_metar_report_modifier(report, MATCH);
  };

  speed_units = "KMH" | "MPS" | "KT";

  include "metar-scanner/wind.rl";

  cavok = "CAVOK" % {
    jweather_metar_report_set_visibility(report,
      JWEATHER_METAR_PERFECT_VISIBILITY);

    add_cloud(report);
    CLOUD->cover = JWEATHER_METAR_CLOUD_COVER_CLEAR;
  };

  include "metar-scanner/visibility.rl";

  runway_vis_range = ("R" digit{2} [LCR]* "/")? (digit{4} . "V" | [PM])?
    digit{4} ([UDN] | "FT")?;

  include "metar-scanner/weather.rl";

  include "metar-scanner/cloud.rl";

  degrees = ("M"? digit{2}) > MatchStart;
  temp    = (
    degrees % {
      if (!report->_temperature) {
        report->_temperature = g_new(gint, 1);
        *report->_temperature = atoi(TEMP);
      }
    }
    . "/" .
    (degrees % {
      if (!report->_dew_point) {
        report->_dew_point = g_new(gint, 1);
        *report->_dew_point = atoi(TEMP);
      }
    })?
  | "M/M");

  main := (
    ("METAR" space)?
    station_id space
    time space
    (modifier space)?
    (wind | "/"{5,6} . speed_units) space
    (cavok . space | (
      ((visibility space)+ | "/"+ . space)?
      (runway_vis_range space){,4}
      ((weather space)+ | "/"+ . space)?
      ((cloud space)+ | other_sky . space | "/"+ . space)?
    ))
    (temp space)?
    ([QA] digit{4})?
    any*
  );
}%%

%% write data;

void scan_metar(
    JWeatherMetarReport* report,
    const gchar* string,
    GError** error)
{
    int cs;

    const char* p = string;
    const char* pe = string + strlen(string);

    const char* match_start;

    int hour, day, minute;

    // for parsing statute mile visibility
    int miles_numerator = 0;
    gdouble miles;

    %% write init;
    %% write exec;

    if (cs == metar_scanner_error)
        g_set_error(error, G_IO_ERROR, G_IO_ERROR_INVALID_DATA,
            "Failed to parse token at character %d", p - string);
}
