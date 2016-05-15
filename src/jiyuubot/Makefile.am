SUBDIRS = tests

bin_PROGRAMS = jiyuubot

jiyuubot_SOURCES = jiyuubot.vala
jiyuubot_VALAFLAGS = \
	$(jiyuubot_U_VALAFLAGS)
jiyuubot_CFLAGS = \
	$(jiyuubot_U_CFLAGS)
jiyuubot_LDADD = \
	$(jiyuubot_U_LIBS)

CLEANFILES = \
	$(jiyuubot_SOURCES:%.vala=%.c) \
	*.stamp \
	*.stamp-t

dist-hook:
	cd $(distdir); rm -f $(CLEANFILES)
