SUBDIRS = libjweather

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
	$(jiyuubot_U_LIBS)

jweather_VALAFLAGS = \
	--vapidir libjweather \
	--pkg jweather \
	$(base_client_VALAFLAGS)
jweather_CFLAGS = \
	-Ilibjweather \
	$(libsoup_CFLAGS) \
	-DGWEATHER_I_KNOW_THIS_IS_UNSTABLE \
	$(libgweather_CFLAGS) \
	$(base_client_CFLAGS)
jweather_LDADD = \
	libjweather/libjweather.la \
	$(base_client_LDADD)

servicedir = $(datadir)/dbus-1/services

client_PROGRAMS = \
	bots \
	convert \
	uri \
	version
service_DATA = \
	so.bob131.JiyuuBot.Client.bots.service \
	so.bob131.JiyuuBot.Client.convert.service \
	so.bob131.JiyuuBot.Client.uri.service \
	so.bob131.JiyuuBot.Client.version.service

$(service_DATA):
	$(AM_GEN_V) printf "[D-BUS Service]\nName=%s\nExec=%s\n" \
		`echo $@ | sed "s|\.service||"` \
		$(clientdir)/`echo $@ | cut -d. -f5` > $@

bots_SOURCES = bots.vala
bots_VALAFLAGS = $(base_client_VALAFLAGS)
bots_CFLAGS = $(base_client_CFLAGS)
bots_LDADD = $(base_client_LDADD)

convert_SOURCES = convert.vala
convert_VALAFLAGS = \
	--pkg rest-0.7 \
	--pkg json-glib-1.0 \
	--thread \
	$(base_client_VALAFLAGS)
convert_CFLAGS = \
	$(librest_CFLAGS) \
	$(json_glib_CFLAGS) \
	$(base_client_CFLAGS)
convert_LDADD = \
	$(librest_LIBS) \
	$(json_glib_LIBS) \
	$(base_client_LDADD)

uri_SOURCES = uri.vala
uri_VALAFLAGS = \
	--pkg libsoup-2.4 \
	--pkg libxml-2.0 \
	$(base_client_VALAFLAGS)
uri_CFLAGS = \
	$(libsoup_CFLAGS) \
	$(libxml_CFLAGS) \
	$(base_client_CFLAGS)
uri_LDADD = \
	$(libsoup_LIBS) \
	$(libxml_LIBS) \
	$(base_client_LDADD)

version_SOURCES = version.vala
version_VALAFLAGS = $(base_client_VALAFLAGS)
version_CFLAGS = $(base_client_CFLAGS)
version_LDADD = $(base_client_LDADD)

CLEANFILES = \
	$(service_DATA)

-include $(top_srcdir)/git.mk
