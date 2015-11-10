[CCode (cheader_filename = "Python.h")]
namespace Python {
    [CCode (cname = "Py_IsInitialized")]
    public bool is_initialized();
    [CCode (cname = "Py_InitializeEx")]
    public void initialize_ex(bool initsigs);
    [CCode (cname = "Py_Finalize")]
    public void finalize();
    [CCode (cname = "PyEval_InitThreads")]
    public void init_threads();

    public enum StartSymbol {
        [CCode (cname = "Py_eval_input")]
        EVAL,
        [CCode (cname = "Py_file_input")]
        FILE,
        [CCode (cname = "Py_single_input")]
        SINGLE
    }

    namespace GIL {
        [CCode (cname = "PyGILState_STATE")]
        [SimpleType]
        public struct State {}
        [CCode (cname = "PyGILState_Ensure")]
        public static Python.GIL.State @lock();
        [CCode (cname = "PyGILState_Release")]
        public void release(Python.GIL.State state);
    }

    namespace Error {
        public errordomain E {
            FAILED
        }
        [CCode (cname = "PyErr_Occurred")]
        public bool occurred();
        [CCode (cname = "PyErr_Print")]
        public void print();
    }

    [CCode (cname = "PyObject", ref_function = "Py_IncRef", unref_function = "Py_DecRef")]
    [Compact]
    public class Object {
        [CCode (cheader_filename = "PythonVala.h", cname = "VPyObject_CallMethod")]
        public Python.Object call_method(string method, string arg_format, ...) throws Python.Error.E;
        [CCode (cname = "PyObject_IsTrue")]
        public bool is_true();
    }

    [CCode (cname = "PyObject")]
    public class Dict : Python.Object {
        [CCode (cname = "PyDict_GetItemString")]
        public Python.Object get_item_string(string item);
    }

    [CCode (cname = "PyObject")]
    public class Module : Python.Object {
        [CCode (cname = "PyModule_AddStringConstant")]
        public bool add_string_constant(string name, string val);
        [CCode (cname = "PyModule_AddObject")]
        public bool add_object(string name, Python.Object val);
        [CCode (cname = "PyModule_GetDict")]
        public Dict get_dict();
        [CCode (cname = "PyModule_New")]
        public Module(string name);
    }

    [CCode (cname = "PyObject")]
    public class Import : Python.Object {
        [CCode (cname = "PyImport_ImportModule")]
        public Import(string module_path);
    }

    [CCode (cname = "PyCodeObject")]
    public class Code : Python.Object {
        [CCode (cname = "PyEval_EvalCode")]
        public Python.Object eval(Python.Object globals, Python.Object locals);
        [CCode (cname = "Py_CompileString")]
        private Code(string data, string filename, Python.StartSymbol start);
        public static Code from_file(string file_path) throws GLib.Error {
            string contents;
            GLib.FileUtils.get_contents(file_path, out contents);
            var name = GLib.Path.get_basename(file_path);
            return new Code(contents, name, Python.StartSymbol.FILE);
        }
    }

    [CCode (cname = "PyListObject", type_check_function = "PyList_Check")]
    public class List : Python.Object {
        [CCode (cname = "PyList_Size")]
        public int get_size();
        public int length {get {return get_size();}}
        [CCode (cname = "PyList_GetItem")]
        public Python.Object @get(int index);
    }

    [CCode (cname = "PyObject")]
    public class String : Python.Object {
        [CCode (cname = "PyUnicode_AsUTF8AndSize")]
        public unowned string to_string(int size = 0);
    }
}


[CCode (cheader_filename = "pygobject.h")]
namespace PyGObject {
    [CCode (cname = "pygobject_init")]
    public Python.Object init(int req_major = -1, int req_minor = -1, int req_micro = -1);
    [CCode (cname = "pyg_enable_threads")]
    public void enable_threads();

    [CCode (cname = "pygobject_new")]
    public Python.Object new_from_obj(GLib.Object obj);

    [CCode (cname = "pyg_type_wrapper_new")]
    public Python.Object type_wrapper_new(GLib.Type type);
    [CCode (cname = "pyg_type_from_object")]
    public GLib.Type type_from_object(Python.Object obj);
}
