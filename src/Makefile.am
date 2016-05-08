noinst_libdir = $(abs_builddir)
noinst_bindir = .


noinst_lib_LTLIBRARIES = libjiyuubot-api.la
noinst_bin_PROGRAMS = jiyuubot


libjiyuubot_api_la_SOURCES = \
	plugin-api.vala

libjiyuubot_api_la_VALAFLAGS = \
	--pkg gio-2.0 \
	--pkg gee-0.8 \
	--pkg libsoup-2.4 \
	--pkg libxml-2.0 \
	--pkg purple \
	--pkg constants \
	--thread \
	--library jiyuubot-api \
	-H jiyuubot-api.h \
	--gir JiyuuBot-1.0.gir \
	$(jiyuubot_U_VALAFLAGS)

libjiyuubot_api_la_CFLAGS = \
	-DGITREV=\"$(GIT_REV)\" \
	$(jiyuubot_U_CFLAGS)

libjiyuubot_api_la_LIBADD = $(jiyuubot_U_LIBS)


JiyuuBot-1.0.typelib: libjiyuubot-api.la
	$(AM_V_GEN) $(GIR_COMPILER) --shared-library libjiyuubot-api.so \
		--output JiyuuBot-1.0.typelib JiyuuBot-1.0.gir

BUILT_SOURCES = JiyuuBot-1.0.typelib


jiyuubot_SOURCES = \
	config.vala \
	plugin-loader.vala \
	plugin-help.vala \
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
	$(jiyuubot_U_VALAFLAGS)

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


CLEANFILES = \
	$(libjiyuubot_api_la_SOURCES:%.vala=%.c) \
	$(jiyuubot_SOURCES:%.vala=%.c) \
	$(BUILT_SOURCES) \
	*.stamp \
	*.stamp-t

EXTRA_DIST = \
	plugin-loader.py

dist-hook:
	cd $(distdir); rm -f $(CLEANFILES)
