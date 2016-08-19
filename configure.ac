AC_INIT([jiyuubot], [0.3])

AC_CONFIG_AUX_DIR([build-aux])
AC_CONFIG_MACRO_DIRS([m4])

AM_INIT_AUTOMAKE([foreign subdir-objects])
AM_SILENT_RULES([yes])

AM_PROG_VALAC([0.28])
AM_PROG_CC_C_O

SHORT_VERSION=$(echo $VERSION | cut -d. -f-2)
AC_SUBST([SHORT_VERSION])

AC_SUBST([clientdir], "\$(libexecdir)/jiyuubot")
AC_SUBST([pkgconfigdir], ["\$(libdir)/pkgconfig"])
AC_SUBST([vapidir], ["\$(datadir)/vala/vapi"])
AC_SUBST([girdir], ["\$(datadir)/gir-1.0"])
AC_SUBST([typelibdir], ["\$(libdir)/girepository-1.0"])

LT_INIT([disable-static])

CFLAGS="$CFLAGS -w"

dnl ###########################################################################
dnl Dependencies
dnl ###########################################################################

GLIB_REQUIRED=2.40.0
AC_SUBST([GLIB_REQUIRED])

PKG_CHECK_MODULES(jiyuubot_U, [
  glib-2.0 >= $GLIB_REQUIRED
  gobject-2.0 >= $GLIB_REQUIRED
  gio-2.0 >= $GLIB_REQUIRED
])

AC_SUBST([jiyuubot_U_VALAFLAGS], ["--pkg gio-2.0 \
          --target-glib=$GLIB_REQUIRED \
          --enable-experimental \
          --enable-experimental-non-null \
          --fatal-warnings"])

AC_PATH_PROG([VALADOC], [valadoc], [xno])
AM_CONDITIONAL([HAS_VALADOC], [test x$has_valadoc != xno])

GOBJECT_INTROSPECTION_CHECK([1.40.0])

GLIB_TESTS

dnl ###########################################################################
dnl Files to generate
dnl ###########################################################################

AC_CONFIG_FILES([
Makefile
src/Makefile
src/libtp/Makefile
src/libtp/tp.pc
src/libjiyuubot/Makefile
src/libjiyuubot/tests/Makefile
src/libjiyuubot/jiyuubot.pc
src/jiyuubot/Makefile
src/jiyuubot/tests/Makefile
src/clients/Makefile
])
AC_OUTPUT
