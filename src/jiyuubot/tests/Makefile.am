include $(top_srcdir)/build-aux/glib-tap.mk

test_programs = jiyuubot-test

# link so we get our own generated C file
jiyuubot.vala:
	$(AM_V_GEN) $(LN_S) ../jiyuubot.vala jiyuubot.vala

jiyuubot_test_SOURCES = \
	$(top_srcdir)/src/libtp/tp.vapi \
	$(top_srcdir)/src/libjiyuubot/jiyuubot.vapi \
	jiyuubot.vala \
	jiyuubot-test.vala
jiyuubot_test_VALAFLAGS = \
	-D TEST \
	$(jiyuubot_U_VALAFLAGS)
jiyuubot_test_CFLAGS = \
	-I$(top_srcdir)/src/libtp \
	-I$(top_srcdir)/src/libjiyuubot \
	$(jiyuubot_U_CFLAGS)
jiyuubot_test_LDADD = \
	$(top_srcdir)/src/libtp/libtp.la \
	$(top_srcdir)/src/libjiyuubot/libjiyuubot.la \
	$(jiyuubot_U_LDADD)

CLEANFILES += jiyuubot.vala

-include $(top_srcdir)/git.mk
