SUBDIRS = tests

bin_PROGRAMS = jiyuubot

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

CLEANFILES = \
	$(jiyuubot_SOURCES:%.vala=%.c) \
	*.stamp \
	*.stamp-t

dist-hook:
	cd $(distdir); rm -f $(CLEANFILES)
