namespace JiyuuBot {
    internal class RegistrarApp : Application {
        internal Client[] clients = {};

        internal override void activate() {
            this.hold();
        }

        internal override bool dbus_register(
            DBusConnection connection,
            string object_path) throws Error
        {
            foreach (var client in clients) {
                var client_name = client.get_type().name();
                try {
                    connection.register_object(
                        Tp.path_from_name(@"$(application_id).$(client_name)"),
                        client);
                } catch (IOError e) {
                    fatal("Failed to register client '%s': %s", client_name,
                        e.message);
                }
            }

            return base.dbus_register(connection, object_path);
        }
    }

    public class ClientApp : Object {
        internal RegistrarApp app = new RegistrarApp();

        public void register(Client client) {
            app.clients += client;
        }

        public int run(string[] args) {
            assert (args.length > 0);

            var id = "";
            foreach (var @char in Path.get_basename(args[0]).to_utf8())
                id += (@char.isalnum() ? "%c" : "%x").printf(@char);
            app.set_application_id(@"$(CLIENT).$(id)");

            return app.run(args);
        }
    }
}
