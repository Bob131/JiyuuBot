AC_INIT([jiyuubot], m4_esyscmd_s([echo "3-`git describe --always`"]))

AC_CONFIG_AUX_DIR([build-aux])
AC_CONFIG_MACRO_DIRS([m4])

AM_INIT_AUTOMAKE([foreign subdir-objects])
AM_SILENT_RULES([yes])

AM_PROG_VALAC([0.28])
AM_PROG_CC_C_O

dnl ###########################################################################
dnl Dependencies
dnl ###########################################################################

GLIB_REQUIRED=2.40.0
AC_SUBST([GLIB_REQUIRED])

PKG_CHECK_MODULES(jiyuubot_U, [
  glib-2.0 >= $GLIB_REQUIRED
  gobject-2.0 >= $GLIB_REQUIRED
  gio-2.0 >= $GLIB_REQUIRED
  telepathy-glib
])

AC_SUBST([jiyuubot_U_VALAFLAGS], ["--pkg gio-2.0 \
          --pkg telepathy-glib \
          --vapidir=\$(top_srcdir)/vapi \
          --target-glib=$GLIB_REQUIRED \
          --enable-experimental \
          --enable-experimental-non-null \
          --fatal-warnings"])

AC_PATH_PROG([VALADOC], [valadoc], [xno])
AM_CONDITIONAL([HAS_VALADOC], [test x$has_valadoc != xno])

CFLAGS="$CFLAGS -w"

GLIB_TESTS

dnl ###########################################################################
dnl Files to generate
dnl ###########################################################################

AC_CONFIG_FILES([
Makefile
src/Makefile
src/libjiyuubot/Makefile
src/jiyuubot/Makefile
src/clients/Makefile
])
LT_INIT([disable-static])
AC_OUTPUT
