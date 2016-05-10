SUBDIRS = src tests

docs:
if HAS_VALADOC
	$(AM_V_GEN) valadoc -o docs --pkg gio-2.0 --pkg telepathy-glib src/libjiyuubot/libjiyuubot.vala
endif


EXTRA_DIST = autogen.sh


clean-local:
	rm -rf docs

dist-hook:
	cd $(distdir); rm -rf docs
