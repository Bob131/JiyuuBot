include $(top_srcdir)/build-aux/glib-tap.mk

test_programs = libjiyuubot-test

libjiyuubot_test_SOURCES = \
	../jiyuubot.vapi \
	libjiyuubot-test.vala
libjiyuubot_test_VALAFLAGS = \
	$(jiyuubot_U_VALAFLAGS)
libjiyuubot_test_CFLAGS = \
	-I../ \
	$(jiyuubot_U_CFLAGS)
libjiyuubot_test_LDADD = \
	../libjiyuubot.la \
	$(jiyuubot_U_LDADD)

CLEANFILES += \
	*.c \
	*.stamp \
	*.stamp-t
