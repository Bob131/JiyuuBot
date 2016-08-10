SUBDIRS = tests

lib_LTLIBRARIES = libjiyuubot.la

include_HEADERS = jiyuubot.h
pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = jiyuubot.pc

vapidir = $(datadir)/vala/vapi
vapi_DATA = jiyuubot.vapi jiyuubot.deps

girdir = $(datadir)/gir-1.0
gir_DATA = JiyuuBot-$(SHORT_VERSION).gir
typelibdir = $(libdir)/girepository-1.0
typelib_DATA = JiyuuBot-$(SHORT_VERSION).typelib

BUILT_SOURCES = \
	jiyuubot.h \
	jiyuubot.pc \
	jiyuubot.vapi jiyuubot.deps \
	JiyuuBot-$(SHORT_VERSION).gir JiyuuBot-$(SHORT_VERSION).typelib

jiyuubot.deps:
	$(AM_V_GEN) printf "gio-2.0\ntelepathy-glib\n" > $@

JiyuuBot-$(SHORT_VERSION).typelib: JiyuuBot-$(SHORT_VERSION).gir
	$(AM_V_GEN) g-ir-compiler --shared-library=libjiyuubot --output=$@ $<

libjiyuubot_la_SOURCES = libjiyuubot.vala
libjiyuubot_la_VALAFLAGS = \
	--library jiyuubot \
	-H jiyuubot.h \
	--vapi jiyuubot.vapi \
	--gir JiyuuBot-$(SHORT_VERSION).gir \
	$(jiyuubot_U_VALAFLAGS)
libjiyuubot_la_CFLAGS = $(jiyuubot_U_CFLAGS)
libjiyuubot_la_LIBADD = $(jiyuubot_U_LIBS)
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
