base_client_VALAFLAGS = \
	--vapidir $(top_srcdir)/src/libtp \
	--pkg tp \
	--vapidir $(top_srcdir)/src/libjiyuubot \
	--pkg jiyuubot \
	$(jiyuubot_U_VALAFLAGS)
base_client_CFLAGS = \
	-I$(top_srcdir)/src/libtp \
	-I$(top_srcdir)/src/libjiyuubot \
	$(jiyuubot_U_CFLAGS)
base_client_LDADD = \
	$(top_srcdir)/src/libtp/libtp.la \
	$(top_srcdir)/src/libjiyuubot/libjiyuubot.la \
	$(jiyuubot_U_LDFLAGS)

servicedir = $(datadir)/dbus-1/services

client_PROGRAMS = \
	bots \
	version
service_DATA = \
	so.bob131.JiyuuBot.Client.bots.service \
	so.bob131.JiyuuBot.Client.version.service

$(service_DATA):
	$(AM_GEN_V) printf "[D-BUS Service]\nName=%s\nExec=%s\n" \
		`echo $@ | sed "s|\.service||"` \
		$(clientdir)/`echo $@ | cut -d. -f5` > $@

bots_SOURCES = bots.vala
bots_VALAFLAGS = $(base_client_VALAFLAGS)
bots_CFLAGS = $(base_client_CFLAGS)
bots_LDADD = $(base_client_LDADD)

version_SOURCES = version.vala
version_VALAFLAGS = $(base_client_VALAFLAGS)
version_CFLAGS = $(base_client_CFLAGS)
version_LDADD = $(base_client_LDADD)

CLEANFILES = \
	$(service_DATA)

-include $(top_srcdir)/git.mk
