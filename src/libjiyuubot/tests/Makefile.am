include $(top_srcdir)/build-aux/glib-tap.mk

test_programs = libjiyuubot-test

libjiyuubot_test_SOURCES = \
	$(top_srcdir)/src/libtp/tp.vapi \
	../jiyuubot.vapi \
	libjiyuubot-test.vala
libjiyuubot_test_VALAFLAGS = \
	$(jiyuubot_U_VALAFLAGS)
libjiyuubot_test_CFLAGS = \
	-I$(top_srcdir)/src/libtp \
	-I../ \
	$(jiyuubot_U_CFLAGS)
libjiyuubot_test_LDADD = \
	$(top_srcdir)/src/libtp/libtp.la \
	../libjiyuubot.la \
	$(jiyuubot_U_LDADD)

CLEANFILES += \
	*.c \
	*.stamp \
	*.stamp-t
