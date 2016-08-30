include $(top_srcdir)/build-aux/glib-tap.mk

test_programs = libtp-test

libtp_test_SOURCES = \
	../tp.vapi \
	libtp-test.vala
libtp_test_VALAFLAGS = \
	$(jiyuubot_U_VALAFLAGS)
libtp_test_CFLAGS = \
	-I../ \
	$(jiyuubot_U_CFLAGS)
libtp_test_LDADD = \
	../libtp.la \
	$(jiyuubot_U_LDADD)

if TP_GLIB_TEST
libtp_test_SOURCES += telepathy-glib-interfaces.vapi
libtp_test_VALAFLAGS += -D TP_GLIB_TEST
libtp_test_CFLAGS += $(tp_glib_CFLAGS)
libtp_test_LDADD += $(tp_glib_LDADD)
endif

-include $(top_srcdir)/git.mk
