This library provides some helper code for the `time` and `weather` clients:

 * `citysearch.vala`: A super-simple n-gram search engine for GWeather. I had
   experimented with various distance metrics, but I found just indexing bi and
   tri-grams was much faster and provided better results.

 * `metar-*`: A METAR fetcher/lexer/parser. There's actually a fair bit of code
   in here, and some of it is bound to be buggy.
   If you (the reader) are interested in using this code but are weary of the
   AGPL license, send me an email. I'm more than happy to split this out into an
   LGPL library, it's only bundled with JiyuuBot since maintaining a separate
   library for a single program is a pain.
