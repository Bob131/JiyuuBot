namespace Tp {
    internal bool is_valid_path(string path) {
        if (path == "/")
            return true;

        if (path[0] != '/')
            return false;

        for (var i = 1; i < path.length; i++) {
            if (path[i] == '/')
                if (path[i - 1] == '/' || i == path.length - 1)
                    return false;
                else
                    continue;
            if (!path[i].isalnum() && path[i] != '_')
                return false;
        }

        return true;
    }

    public string path_from_name(string name)
        requires (DBus.is_name(name))
        ensures (is_valid_path(result))
    {
        return "/%s".printf(name.replace(".", "/"));
    }

    public string name_from_path(string path)
        requires (is_valid_path(path))
        ensures (DBus.is_name(result))
    {
        return path[1:path.length].replace("/", ".");
    }
}
