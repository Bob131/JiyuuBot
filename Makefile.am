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

MAINTAINERCLEANFILES = \
	$(GITIGNORE_MAINTAINERCLEANFILES_TOPLEVEL) \
	$(GITIGNORE_MAINTAINERCLEANFILES_MAKEFILE_IN) \
	$(GITIGNORE_MAINTAINERCLEANFILES_M4_LIBTOOL) \
	m4/gsettings.m4 m4/introspection.m4 m4/pkg.m4 \
	docs

DISTCLEANFILES = $(wildcard *.conf)

-include git.mk
