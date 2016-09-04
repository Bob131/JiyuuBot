pkglib_LTLIBRARIES = libjweather.la

BUILT_SOURCES = jweather.deps jweather-priv.h

# requires GTK because gweather doesn't declare this dependency
jweather.deps:
	$(AM_V_GEN) printf "gweather-3.0\ngtk+-3.0\n" > $@

metar-scanner.c: metar-scanner.rl metar-scanner/*.rl
	$(AM_V_GEN) ragel -o $@ $<

libjweather_la_SOURCES = \
	citysearch.vala \
	metar-scanner.c \
	metar-cloud.vala \
	metar-observations.vala \
	metar-wind.vala \
	metar-report.vala
libjweather_la_VALAFLAGS = \
	--pkg libsoup-2.4 \
	--pkg gweather-3.0 \
	--pkg gtk+-3.0 \
	--library jweather \
	-H jweather.h -h jweather-priv.h \
	--vapi jweather.vapi \
	$(jiyuubot_U_VALAFLAGS)
libjweather_la_CFLAGS = \
	$(libsoup_CFLAGS) \
	-DGWEATHER_I_KNOW_THIS_IS_UNSTABLE \
	$(libgweather_CFLAGS) \
	$(jiyuubot_U_CFLAGS)
libjweather_la_LIBADD = \
	$(libsoup_LIBS) \
	$(libgweather_LIBS) \
	$(jiyuubot_U_LIBS)

CLEANFILES = metar-scanner.c

-include $(top_srcdir)/git.mk
