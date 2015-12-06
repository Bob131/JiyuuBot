namespace JiyuuBot {
    namespace Config {
        public class AccountInfo : Object {
            public string id {construct; get;}
            public string username {construct; get;}
            public string protocol {construct; get;}

            public Purple.Account account;
            public Gee.HashMap<string, Variant> settings = new Gee.HashMap<string, Variant>();

            public signal void chats_altered();
            private Gee.HashSet<string> _chats = new Gee.HashSet<string>();
            public string[] chats {
                owned get {
                    string[] r = {};
                    foreach (var chat in _chats) {
                        r += chat;
                    }
                    return r;
                }
            }

            public void add_chat(string chat) {
                _chats.add(chat);
                chats_altered();
            }

            public void remove_chat(string chat) {
                _chats.remove(chat);
                chats_altered();
            }

            public AccountInfo(string id, string[] chats) {
                Object(id: id, username: id.split(":")[0], protocol: id.split(":")[1]);
                foreach (var chat in chats) {
                    _chats.add(chat);
                }
            }
        }


        public class AccountList : Object {
            public Gee.HashMap<string, AccountInfo> accounts {construct; private get;}
            public KeyFile file {construct; private get;}

            public int length {
                get {
                    return accounts.size;
                }
            }

            public void append(AccountInfo account) {
                accounts.set(account.id, account);
            }

            public new AccountInfo @get(string id) {
                return accounts.get(id);
            }

            public Gee.Iterator<AccountInfo> iterator() {
                return accounts.values.iterator();
            }

            public AccountList.load_from_config() {
                Object(accounts: new Gee.HashMap<string, AccountInfo>(), file: new KeyFile());
                var config_path = Path.build_filename(root_dir, "config", "purple.ini");
                try {
                    file.load_from_file(config_path, KeyFileFlags.KEEP_COMMENTS|KeyFileFlags.KEEP_TRANSLATIONS);
                } catch (Error e) {
                    stderr.printf(@"Could not read config file: $(e.message)\n");
                    Posix.exit(1);
                }

                foreach (var group in file.get_groups()) {
                    if (!(":" in group)) {
                        stderr.printf(@"Invalid account specification: $(group)\n");
                        continue;
                    }

                    string[] chats = {};
                    if (file.has_key(group, "autojoin-chats")) {
                        chats = /,\s*/.split(file.get_value(group, "autojoin-chats").replace("\"", ""));
                    }
                    var account = new AccountInfo(group, chats);

                    account.chats_altered.connect(() => {
                        file.set_string(account.id, "autojoin-chats", "\"" + string.joinv(", ", account.chats) + "\"");
                        file.save_to_file(config_path);
                    });

                    foreach (var key in file.get_keys(group)) {
                        if (key == "autojoin-chats")
                            continue;
                        try {
                            var variant = Variant.parse(null, file.get_value(group, key));

                            string[] allowed_variants = {"s", "i", "b"};
                            if (!(variant.get_type_string() in allowed_variants)) {
                                throw new KeyFileError.INVALID_VALUE(@"Invalid variant type '$(variant.get_type_string())'");
                            }

                            account.settings[key] = variant;
                        } catch (Error e) {
                            stderr.printf(@"Malformed settings key '$(key)' in '$(group)': $(e.message)\n");
                        }
                    }
                    this.append(account);
                }

                if (this.length == 0) {
                    stderr.printf("No accounts defined in purple.ini, exiting\n");
                    Posix.exit(1);
                }
            }
        }


        public class PluginConfigStore : Object {
            public string path {construct; private get;}
            public KeyFile file;
            private Gee.HashMap<string, Gee.HashMap<string, string>> groups;
            private FileMonitor config_monitor;

            public PluginConfig get_group(string group) {
                Gee.HashMap<string, string> map;
                if (groups.has_key(group))
                    map = groups[group];
                else {
                    map = new Gee.HashMap<string, string>();
                    if (file.has_group(group))
                        foreach (var key in file.get_keys(group))
                            map[key] = file.get_value(group, key);
                    groups[group] = map;
                }
                return new PluginConfig(map);
            }

            private void load() {
                if (!FileUtils.test(path, FileTest.EXISTS))
                    Posix.creat(path, 0666);

                file = new KeyFile();
                file.load_from_file(path, KeyFileFlags.NONE);

                groups.foreach((entry) => {
                    var group = entry.key;
                    var map = entry.value;
                    if (!file.has_group(group)) {
                        map.clear();
                        return true;
                    }
                    string[] processed_keys = {};
                    map.foreach((map_entry) => {
                        var key = map_entry.key;
                        var val = map_entry.value;
                        if (!file.has_key(group, key)) {
                            map.unset(key);
                            return true;
                        }
                        if (val != file.get_value(group, key)) {
                            map[key] = file.get_value(group, key);
                            processed_keys += key;
                        }
                        return true;
                    });
                    foreach (var key in file.get_keys(group)) {
                        if (!(key in processed_keys)) {
                            map[key] = file.get_value(group, key);
                        }
                    }
                    return true;
                });
            }

            public PluginConfigStore() {
                Object(path: Path.build_filename(root_dir, "config", "plugin.ini"));
            }

            construct {
                groups = new Gee.HashMap<string, Gee.HashMap<string, string>>();

                load();

                config_monitor = File.new_for_path(path).monitor_file(FileMonitorFlags.NONE);
                config_monitor.changed.connect((_, __, ev) => {
                    if (ev == FileMonitorEvent.CHANGES_DONE_HINT) {
                        load();
                        message("Reloaded plugin configs");
                    }
                });
            }
        }
    }
}
