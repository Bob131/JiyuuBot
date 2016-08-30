SUBDIRS = tests

bin_PROGRAMS = jiyuubot jiyuubot-launcher

jiyuubot_SOURCES = \
	$(top_srcdir)/src/libtp/tp.vapi \
	$(top_srcdir)/src/libjiyuubot/jiyuubot.vapi \
	accounts.vala \
	clients.vala \
	jiyuubot.vala
jiyuubot_VALAFLAGS = \
	$(jiyuubot_U_VALAFLAGS)
jiyuubot_CFLAGS = \
	-I$(top_srcdir)/src/libtp \
	-I$(top_srcdir)/src/libjiyuubot \
	$(jiyuubot_U_CFLAGS)
jiyuubot_LDADD = \
	$(top_srcdir)/src/libtp/libtp.la \
	$(top_srcdir)/src/libjiyuubot/libjiyuubot.la \
	$(jiyuubot_U_LIBS)

jiyuubot_launcher_SOURCES = \
	$(top_srcdir)/src/libtp/tp.vapi \
	$(top_srcdir)/src/libjiyuubot/jiyuubot.vapi \
	jiyuubot-launcher.vala
jiyuubot_launcher_VALAFLAGS = \
	--pkg posix \
	$(jiyuubot_U_VALAFLAGS)
jiyuubot_launcher_CFLAGS = \
	-DDATADIR=\"$(datadir)\" \
	$(jiyuubot_CFLAGS)
jiyuubot_launcher_LDADD = \
	$(jiyuubot_LDADD)

-include $(top_srcdir)/git.mk
