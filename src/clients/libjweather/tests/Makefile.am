include $(top_srcdir)/build-aux/glib-tap.mk

test_programs = tests

tests_SOURCES = \
	tests.vala
tests_VALAFLAGS = \
	--vapidir .. \
	--pkg jweather \
	$(jiyuubot_U_VALAFLAGS)
tests_CFLAGS = \
	-I.. \
	-DGWEATHER_I_KNOW_THIS_IS_UNSTABLE \
	$(libgweather_CFLAGS) \
	$(jiyuubot_U_CFLAGS)
tests_LDADD = \
	../libjweather.la \
	$(jiyuubot_U_LDADD)

-include $(top_srcdir)/git.mk
