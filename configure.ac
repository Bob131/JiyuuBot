AC_INIT([jiyuubot],[0.0])

AC_CONFIG_AUX_DIR([build-aux])
AC_CONFIG_MACRO_DIRS([m4])

AM_INIT_AUTOMAKE([foreign])

AM_PROG_VALAC([0.24])
AM_PROG_CC_C_O

GIT_REV=m4_esyscmd_s([git describe --always])
AC_SUBST([GIT_REV])

dnl ###########################################################################
dnl Dependencies
dnl ###########################################################################

GOBJECT_INTROSPECTION_CHECK([1.44.0])

GLIB_REQUIRED=2.38.0
GOBJ_REQUIRED=2.0.0
GIO_REQUIRED=2.0.0

PKG_CHECK_MODULES(jiyuubot_U, [
  glib-2.0 >= $GLIB_REQUIRED
  gobject-2.0 >= $GOBJ_REQUIRED
  gio-2.0 >= $GIO_REQUIRED
  gee-0.8
  libpeas-1.0
  purple
  libsoup-2.4
  python3
])

AC_SUBST([GLIB_REQUIRED])

dnl ###########################################################################
dnl Files to generate
dnl ###########################################################################

AC_CONFIG_FILES([
Makefile
src/Makefile
])
GLIB_GSETTINGS
LT_INIT([disable-static])
AC_OUTPUT
