noinst_libdir = $(abs_builddir)

noinst_lib_LTLIBRARIES = \
	bots.la \
	isitup.la


base_CFLAGS = \
	-I$(top_srcdir)/src \
	-fPIC \
	$(jiyuubot_U_CFLAGS)

base_VALAFLAGS = \
	--pkg gio-2.0 \
	--pkg gee-0.8 \
	--pkg libsoup-2.4 \
	--pkg purple \
	--pkg jiyuubot-api \
	--vapidir $(top_srcdir)/vapi \
	--target-glib $(GLIB_REQUIRED)

base_LIBADD = \
	$(top_srcdir)/src/libjiyuubot-api.la \
	$(jiyuubot_U_LIBS)

base_LDFLAGS = -module


bots_la_SOURCES = bots.vala
bots_la_CFLAGS = $(base_CFLAGS)
bots_la_VALAFLAGS = $(base_VALAFLAGS)
bots_la_LIBADD = $(base_LIBADD)
bots_la_LDFLAGS = $(base_LDFLAGS)

isitup_la_SOURCES = isitup.vala
isitup_la_CFLAGS = $(base_CFLAGS)
isitup_la_VALAFLAGS = \
	--pkg json-glib-1.0 \
	$(base_VALAFLAGS)
isitup_la_LIBADD = $(base_LIBADD)
isitup_la_LDFLAGS = $(base_LDFLAGS)
