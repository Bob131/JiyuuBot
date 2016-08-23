SUBDIRS = tests

lib_LTLIBRARIES = libtp.la

include_HEADERS = tp.h
pkgconfig_DATA = tp.pc

vapi_DATA = tp.vapi tp.deps

gir_DATA = Tp-$(SHORT_VERSION).gir
typelib_DATA = Tp-$(SHORT_VERSION).typelib

BUILT_SOURCES = \
	namespace.vala \
	tp.h \
	tp.pc \
	tp.vapi tp.deps \
	Tp-$(SHORT_VERSION).gir Tp-$(SHORT_VERSION).typelib

namespace.vala: namespace.vala.in
	$(AM_V_GEN) sed -e "s|[@]SHORT_VERSION[@]|$(SHORT_VERSION)|" $< > $@

tp.deps:
	$(AM_V_GEN) printf "gio-2.0\n" > $@

Tp-$(SHORT_VERSION).typelib: Tp-$(SHORT_VERSION).gir
	$(AM_V_GEN) g-ir-compiler --shared-library=libtp --output=$@ $<

libtp_la_SOURCES = \
	accounts.vala \
	channels.vala \
	clients.vala \
	connections.vala \
	handles.vala \
	messages.vala \
	misc.vala \
	namespace.vala
libtp_la_VALAFLAGS = \
	--library tp \
	-H tp.h \
	--vapi tp.vapi \
	--gir Tp-$(SHORT_VERSION).gir \
	$(jiyuubot_U_VALAFLAGS)
libtp_la_CFLAGS = $(jiyuubot_U_CFLAGS)
libtp_la_LIBADD = $(jiyuubot_U_LIBS)
libtp_la_LDFLAGS = \
	-release $(SHORT_VERSION)

CLEANFILES = \
	$(libtp_la_SOURCES:.vala=.c) \
	$(BUILT_SOURCES) \
	*.stamp

clean-local:
	rm -f *.gir *.typelib

dist-hook:
	cd $(distdir); rm -f $(CLEANFILES)
