namespace JiyuuBot {
    namespace Prpl {
        class Interface : Object {
            // prevent freeing of libpurple data
            private PurpleAmend.CoreUiOps ui_ops;
            private PurpleAmend.EventLoopUiOps loop_ops;
            private PurpleAmend.ConnectionUiOps conn_ops;
            private PurpleAmend.ConversationUiOps conv_ops;

            public Config.AccountList accounts {construct; get;}

            static weak Interface self;

            public Interface(Config.AccountList accs) {
                Object(accounts: accs);
                self = this;
            }

            public signal void incoming_message(Message msg);
            private delegate HashTable ChatInfoDefaults(Purple.Connection conn, string chat_name);

            private static uint input_handler(int fd, Purple.InputCondition purple_cond, Purple.InputFunction func, void* data) {
                IOCondition glib_cond = 0;

                var base_cond = IOCondition.HUP | IOCondition.ERR;

                if (purple_cond == Purple.InputCondition.READ)
                    glib_cond = IOCondition.IN | base_cond;
                else if (purple_cond == Purple.InputCondition.WRITE)
                    glib_cond = IOCondition.OUT | base_cond | IOCondition.NVAL;

                var channel = new IOChannel.unix_new(fd);
                return channel.add_watch_full(Priority.DEFAULT, glib_cond, () => {
                    func(data, fd, purple_cond);
                    return true;
                });
            }

            private static uint timeout_add(uint interval, SourceFunc func) {
                return Timeout.add(interval, func);
            }

            private static bool source_remove(uint tag) {
                return Source.remove(tag);
            }

            private static string construct_account_id(Purple.Account account) {
                return string.join(":", account.get_username(), account.get_protocol_id());
            }

            private static int join_on_invite(Purple.Account account,
                                              string inviter,
                                              string chat,
                                              string? invite_message,
                                              HashTable components,
                                              void* data)
            {
                self.accounts[construct_account_id(account)].add_chat(chat);
                return 1;
            }

            private static void join_chats(Purple.Connection conn) {
                var acc_id = string.join(":", conn.get_account().get_username(), conn.get_account().get_protocol_id());

                foreach (var chat_name in self.accounts[acc_id].chats) {
                    HashTable? hash = null;
                    weak Purple.PluginProtocolInfo info = Purple.plugin_protocol_info(conn.get_prpl());

                    if (info.chat_info_defaults != null)
                        hash = ((ChatInfoDefaults) info.chat_info_defaults)(conn, chat_name);

                    var chat = new Purple.Chat(conn.account, chat_name, hash);
                    if (chat != null)
                        Purple.serv_join_chat(conn, chat.get_components());
                    else
                        warning(@"Account '$(acc_id)' failed to connect to chat: $(chat_name)");
                }
            }

            private static void receive_message(Purple.Conversation conv,
                                                string? sender,
                                                string msg,
                                                Purple.MessageFlags _,
                                                time_t __)
            {
                if (sender != conv.get_gc().get_display_name() && sender != null) {
                    var unescaped = Purple.unescape_html(Purple.markup_strip_html(msg));
                    var purple_message = new Message(sender, unescaped, msg, conv);
                    self.incoming_message(purple_message);
                }
            }

            construct {
                message("libpurple version: " + Purple.Core.get_version(), null);
                Purple.util_set_user_dir("/dev/null");

                ui_ops = PurpleAmend.CoreUiOps();
                PurpleAmend.Core.set_ui_ops(ref ui_ops);

                loop_ops = {
                    (Callback) input_handler,
                    null,
                    (Callback) source_remove,
                    (Callback) timeout_add,
                    null,
                    (Callback) source_remove
                };
                PurpleAmend.eventloop_set_ui_ops(ref loop_ops);

                conn_ops = {
                    null,
                    (Callback) join_chats
                };
                PurpleAmend.connections_set_ui_ops(ref conn_ops);

                conv_ops = {};
                conv_ops.write_chat = (Callback) receive_message;
                conv_ops.write_im = (Callback) receive_message;
                PurpleAmend.conversations_set_ui_ops(ref conv_ops);

                Purple.Core.init(app_id);

                Purple.signal_connect(Purple.conversations_get_handle(),
                    "chat-invited", this, (Purple.Callback) join_on_invite, null);

                Purple.set_blist(Purple.blist_new());

                foreach (var account_info in accounts) {
                    var account = new Purple.Account(account_info.username, account_info.protocol);

                    account_info.settings.map_iterator().foreach((key, val) => {
                        if (val.get_type_string() == "b")
                            account.set_bool(key, val.get_boolean());
                        else if (val.get_type_string() == "i")
                            account.set_int(key, val.get_int32());
                        else if (val.get_type_string() == "s")
                            account.set_string(key, val.get_string());
                        return true;
                    });

                    account.set_enabled(app_id, true);
                    account_info.account = (owned) account;
                }
            }
        }
    }
}
