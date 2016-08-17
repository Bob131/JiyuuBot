namespace Tp {
    public const string ACCOUNT_MANAGER =
        "org.freedesktop.Telepathy.AccountManager";
    public const string ACCOUNT = "org.freedesktop.Telepathy.Account";

    [DBus (name = "org.freedesktop.Telepathy.AccountManager")]
    public interface AccountManager : DBusProxy {
        public async abstract ObjectPath create_account(
            string connection_manager,
            string protocol,
            string display_name,
            HashTable<string, Variant?> parameters,
            HashTable<string, Variant?> properties
        ) throws Error;

        [DBus (visible = false)]
        public static AccountManager dup() throws Error {
            return Bus.get_proxy_sync<AccountManager>(BusType.SESSION,
                ACCOUNT_MANAGER, path_from_name(ACCOUNT_MANAGER));
        }
    }

    [DBus (name = "org.freedesktop.Telepathy.Account")]
    public interface Account : DBusProxy {
        public abstract string display_name {set; owned get;}
        public abstract string nickname {set; owned get;}
        public abstract bool enabled {set; get;}
        public abstract bool connect_automatically {set; get;}

        public abstract async void remove() throws Error;

        public signal void removed();
    }

    public class AccountRequest : DBusProxy, Account {
        public string connection_manager {construct; get;}
        public string protocol {construct; get;}
        public HashTable<string, Variant?> parameters {construct; get;}

        public string display_name {set; owned get;}
        public string nickname {set; owned get;}
        public bool enabled {set; get;}
        public bool connect_automatically {set; get;}

        public async void remove() throws Error {
            throw new IOError.FAILED("Cannot remove request");
        }

        public async Account create(AccountManager am) throws Error {
            var props = new HashTable<string, Variant?>(str_hash, str_equal);

            if ((string?) nickname != null)
                props[@"$(ACCOUNT).Nickname"] = new Variant.string(nickname);

            props[@"$(ACCOUNT).Enabled"] = new Variant.boolean(enabled);
            props[@"$(ACCOUNT).ConnectAutomatically"] =
                new Variant.boolean(connect_automatically);

            var path = yield am.create_account(connection_manager, protocol,
                display_name, parameters, props);

            return yield Bus.get_proxy<Account>(BusType.SESSION,
                ACCOUNT_MANAGER, path);
        }

        public AccountRequest(string connection_manager, string protocol) {
            Object(connection_manager: connection_manager, protocol: protocol,
                parameters: new HashTable<string,Variant?>(str_hash,str_equal));
        }
    }
}
