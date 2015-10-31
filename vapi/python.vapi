[CCode (cheader_filename = "Python.h")]
namespace Python {
    [CCode (cname = "Py_IsInitialized")]
    public bool is_initialised();

    [CCode (cname = "")]
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

    [CCode (cname = "PyObject", ref_function = "Py_IncRef", unref_function = "Py_DecRef")]
    public class Object {}

    [CCode (cname = "PyObject")]
    public class Module : Python.Object {
        [CCode (cname = "PyModule_AddStringConstant")]
        public bool add_string_constant(string name, string val);
        [CCode (cname = "PyModule_AddObject")]
        public bool add_object(string name, Python.Object val);
        [CCode (cname = "PyModule_GetDict")]
        public Python.Object get_dict();
        [CCode (cname = "PyModule_New")]
        public Module(string name);
    }

    [CCode (cname = "PyObject")]
    class Import : Python.Object {
        [CCode (cname = "PyImport_ImportModule")]
        public Import(string module_path);
    }

    [CCode (cname = "PyCodeObject")]
    class Code : Python.Object {
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
}
