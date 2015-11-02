#include <stdio.h>
#include <Python.h>
#include <glib.h>


#define PYTHON_ERROR_E python_error_e_quark()

GQuark python_error_e_quark(void) {
    return g_quark_from_static_string("python-error-e-quark");
}

typedef enum {
    PYTHON_ERROR_E_FAILED
} PythonErrorE;

#define VPyObject_CallMethod(obj, method, arg_format, error, ...) \
    ({ \
        PyObject *result = PyObject_CallMethod(obj, method, arg_format, __VA_ARGS__); \
        if (PyErr_Occurred()) { \
            PyObject *type, *value, *tb; \
            PyErr_Fetch(&type, &value, &tb); \
            char *type_name = PyUnicode_AsUTF8AndSize(PyObject_GetAttrString(type, "__name__"), NULL); \
            char *value_str = PyUnicode_AsUTF8AndSize(PyObject_Str(value), NULL); \
            PyErr_Restore(type, value, tb); \
            PyErr_Print(); \
            g_set_error(error, PYTHON_ERROR_E, PYTHON_ERROR_E_FAILED, "%s: %s", type_name, value_str); \
        } \
        result; \
     })
