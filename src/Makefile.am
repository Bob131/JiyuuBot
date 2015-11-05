noinst_libdir = $(abs_builddir)
noinst_bindir = .


noinst_lib_LTLIBRARIES = libjiyuubot-api.la
noinst_bin_PROGRAMS = jiyuubot


libjiyuubot_api_la_SOURCES = \
	plugin-api.vala

libjiyuubot_api_la_VALAFLAGS = \
	--pkg gio-2.0 \
	--pkg gee-0.8 \
	--pkg purple \
	--pkg constants \
	--thread \
	--library jiyuubot-api \
	-H jiyuubot-api.h \
	--vapi $(top_srcdir)/vapi/jiyuubot-api.vapi \
	--gir JiyuuBot-1.0.gir \
	--vapidir $(top_srcdir)/vapi \
	--target-glib $(GLIB_REQUIRED)

libjiyuubot_api_la_CFLAGS = \
	-DGITREV=\"$(GIT_REV)\" \
	$(jiyuubot_U_CFLAGS)

libjiyuubot_api_la_LIBADD = $(jiyuubot_U_LIBS)


jiyuubot_SOURCES = \
	config.vala \
	plugin-loader.vala \
	plugin-url-handler.vala \
	purple.vala \
	main.vala

jiyuubot_VALAFLAGS = \
	--pkg gio-2.0 \
	--pkg gee-0.8 \
	--pkg gmodule-2.0 \
	--pkg libsoup-2.4 \
	--pkg libxml-2.0 \
	--pkg posix \
	--pkg purple \
	--pkg purple-amend \
	--pkg constants \
	--pkg python \
	--pkg jiyuubot-api \
	--vapidir $(top_srcdir)/vapi \
	--target-glib $(GLIB_REQUIRED)

jiyuubot_CFLAGS = \
	-DAPPID=\"so.bob131.jiyuubot\" \
	-DROOTDIR=\"$(abs_top_srcdir)\" \
	-DGITREV=\"$(GIT_REV)\" \
	-I. \
	-I$(top_srcdir)/vapi \
	-fPIC \
	$(jiyuubot_U_CFLAGS)

jiyuubot_LDADD = \
	libjiyuubot-api.la \
	$(jiyuubot_U_LIBS)


all:
	g-ir-compiler \
		--shared-library libjiyuubot-api.so \
		--output JiyuuBot-1.0.typelib \
		JiyuuBot-1.0.gir 2> /dev/null
