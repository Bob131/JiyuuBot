namespace Tp {
    public string path_from_name(string name) {
        return "/%s".printf(name.replace(".", "/"));
    }

    public string name_from_path(string path) {
        return path[1:path.length].replace("/", ".");
    }
}
