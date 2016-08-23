AM_MAKEFLAGS = --no-print-directory
DISTCHECK_CONFIGURE_FLAGS = --enable-introspection

SUBDIRS = src

docs:
if HAS_VALADOC
	$(AM_V_GEN) valadoc \
		-o docs \
		--package-name jiyuubot \
		--pkg gio-2.0 \
		src/libtp/*.vala \
		src/libjiyuubot/*.vala \
		src/libjiyuubot/clients/*.vala
else
	@echo "ERROR: valadoc not found in PATH"
	return 1
endif

EXTRA_DIST = autogen.sh

clean-local:
	rm -rf docs

dist-hook:
	cd $(distdir); rm -rf docs
