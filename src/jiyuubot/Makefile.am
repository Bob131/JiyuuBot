SUBDIRS = tests

bin_PROGRAMS = jiyuubot jiyuubot-launcher

jiyuubot_SOURCES = \
	$(top_srcdir)/src/libjiyuubot/jiyuubot.vapi \
	jiyuubot.vala
jiyuubot_VALAFLAGS = \
	$(jiyuubot_U_VALAFLAGS)
jiyuubot_CFLAGS = \
	-I$(top_srcdir)/src/libjiyuubot \
	$(jiyuubot_U_CFLAGS)
jiyuubot_LDADD = \
	$(top_srcdir)/src/libjiyuubot/libjiyuubot.la \
	$(jiyuubot_U_LIBS)

jiyuubot_launcher_SOURCES = \
	$(top_srcdir)/src/libjiyuubot/jiyuubot.vapi \
	jiyuubot-launcher.vala
jiyuubot_launcher_VALAFLAGS = \
	$(jiyuubot_U_VALAFLAGS)
jiyuubot_launcher_CFLAGS = \
	-I$(top_srcdir)/src/libjiyuubot \
	$(jiyuubot_U_CFLAGS)
jiyuubot_launcher_LDADD = \
	$(top_srcdir)/src/libjiyuubot/libjiyuubot.la \
	$(jiyuubot_U_LIBS)

CLEANFILES = \
	$(jiyuubot_SOURCES:%.vala=%.c) \
	$(jiyuubot_launcher_SOURCES:%.vala=%.c) \
	*.stamp \
	*.stamp-t

dist-hook:
	cd $(distdir); rm -f $(CLEANFILES)
