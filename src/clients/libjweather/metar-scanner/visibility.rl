%%{
  machine metar_scanner;

  statute_miles =
    "M"?
    (
      (digit > MatchStart % {miles = atoi(MATCH);} space)?
      digit > MatchStart % {miles_numerator = atoi(MATCH);} "/"
    )?
    digit{1,2} > MatchStart % {
      int match = atoi(MATCH);
      if (miles_numerator)
        miles += miles_numerator / match;
      else
        miles = match;
    }
    "SM" % {
      gdouble kilometers = miles * 1.609l;
      jweather_metar_report_set_visibility(report, (int) (kilometers * 1000));
      miles = 0;
      miles_numerator = 0;
    };

  meters =
    digit{4,5} > MatchStart % {
      jweather_metar_report_set_visibility(report, atoi(MATCH));
    }
    [NESW]{,2} "DV"?;

  visibility = statute_miles | meters;
}%%
