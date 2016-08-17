include $(top_srcdir)/build-aux/glib-tap.mk

test_programs = jiyuubot-test

# link so we get our own generated C file
jiyuubot.vala:
	$(AM_V_GEN) $(LN_S) ../jiyuubot.vala jiyuubot.vala

-include ../Makefile.am

jiyuubot_test_SOURCES = \
	$(top_srcdir)/src/libtp/tp.vapi \
	$(top_srcdir)/src/libjiyuubot/jiyuubot.vapi \
	jiyuubot.vala \
	jiyuubot-test.vala
jiyuubot_test_VALAFLAGS = \
	-D TEST \
	$(jiyuubot_VALAFLAGS)
jiyuubot_test_CFLAGS = $(jiyuubot_CFLAGS)
jiyuubot_test_LDADD = $(jiyuubot_LDADD)


CLEANFILES += \
	jiyuubot.vala \
	*.c \
	*.stamp \
	*.stamp-t
