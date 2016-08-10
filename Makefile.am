AM_MAKEFLAGS = --no-print-directory
DISTCHECK_CONFIGURE_FLAGS = --enable-introspection

SUBDIRS = src

docs:
if HAS_VALADOC
	$(AM_V_GEN) valadoc -o docs --pkg gio-2.0 --pkg telepathy-glib src/libjiyuubot/libjiyuubot.vala
else
	@echo "ERROR: valadoc not found in PATH"
	return 1
endif

EXTRA_DIST = autogen.sh

clean-local:
	rm -rf docs

dist-hook:
	cd $(distdir); rm -rf docs
