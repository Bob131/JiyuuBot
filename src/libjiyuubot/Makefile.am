SUBDIRS = tests

lib_LTLIBRARIES = libjiyuubot.la

include_HEADERS = jiyuubot.h
pkgconfig_DATA = jiyuubot.pc

vapi_DATA = jiyuubot.vapi jiyuubot.deps

gir_DATA = JiyuuBot-$(SHORT_VERSION).gir
typelib_DATA = JiyuuBot-$(SHORT_VERSION).typelib

BUILT_SOURCES = \
	namespace.vala \
	jiyuubot.h \
	jiyuubot.pc \
	jiyuubot.vapi jiyuubot.deps \
	JiyuuBot-$(SHORT_VERSION).gir JiyuuBot-$(SHORT_VERSION).typelib

namespace.vala: namespace.vala.in
	$(AM_V_GEN) sed -e "s|[@]SHORT_VERSION[@]|$(SHORT_VERSION)|" $< > $@

jiyuubot.deps:
	$(AM_V_GEN) printf "tp\n" > $@

JiyuuBot-$(SHORT_VERSION).typelib: JiyuuBot-$(SHORT_VERSION).gir
	$(AM_V_GEN) g-ir-compiler --includedir=$(top_srcdir)/src/libtp \
		--shared-library=libjiyuubot \
		--output=$@ \
		$<

libjiyuubot_la_SOURCES = \
	$(top_srcdir)/src/libtp/tp.vapi \
	clients.vala \
	messages.vala \
	misc.vala \
	namespace.vala
libjiyuubot_la_VALAFLAGS = \
	--library jiyuubot \
	-H jiyuubot.h \
	--vapi jiyuubot.vapi \
	--gir JiyuuBot-$(SHORT_VERSION).gir \
	$(jiyuubot_U_VALAFLAGS)
libjiyuubot_la_CFLAGS = \
	-I$(top_srcdir)/src/libtp \
	$(jiyuubot_U_CFLAGS)
libjiyuubot_la_LIBADD = \
	$(top_srcdir)/src/libtp/libtp.la \
	$(jiyuubot_U_LIBS)
libjiyuubot_la_LDFLAGS = \
	-release $(SHORT_VERSION)

CLEANFILES = \
	$(libjiyuubot_la_SOURCES:.vala=.c) \
	$(BUILT_SOURCES) \
	*.stamp

clean-local:
	rm -f *.gir *.typelib

dist-hook:
	cd $(distdir); rm -f $(CLEANFILES)
