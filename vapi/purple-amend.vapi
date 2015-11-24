[CCode (cheader_filename = "purple.h", lower_case_cprefix = "purple_")]
namespace PurpleAmend {
    [CCode (cname = "PurpleCoreUiOps")]
    [Compact]
    public struct CoreUiOps {
        public weak GLib.Callback debug_ui_init;
        public weak GLib.Callback get_ui_info;
        public weak GLib.Callback quit;
        public weak GLib.Callback ui_init;
        public weak GLib.Callback ui_prefs_init;
    }
    public class Core {
        public static void set_ui_ops (ref PurpleAmend.CoreUiOps ops);
    }
    [CCode (cname = "PurpleEventLoopUiOps")]
    [Compact]
    public struct EventLoopUiOps {
        public weak GLib.Callback input_add;
        public weak GLib.Callback input_get_error;
        public weak GLib.Callback input_remove;
        public weak GLib.Callback timeout_add;
        public weak GLib.Callback timeout_add_seconds;
        public weak GLib.Callback timeout_remove;
    }
    [CCode (cname = "PurpleConnectionUiOps")]
    [Compact]
    public struct ConnectionUiOps {
        public weak GLib.Callback connect_progress;
        public weak GLib.Callback connected;
        public weak GLib.Callback disconnected;
        public weak GLib.Callback network_connected;
        public weak GLib.Callback network_disconnected;
        public weak GLib.Callback notice;
        public weak GLib.Callback report_disconnect;
        public weak GLib.Callback report_disconnect_reason;
    }
    [CCode (cname = "PurpleConversationUiOps")]
    [Compact]
    public struct ConversationUiOps {
        public weak GLib.Callback chat_add_users;
        public weak GLib.Callback chat_remove_users;
        public weak GLib.Callback chat_rename_user;
        public weak GLib.Callback chat_update_user;
        public weak GLib.Callback create_conversation;
        public weak GLib.Callback custom_smiley_add;
        public weak GLib.Callback custom_smiley_close;
        public weak GLib.Callback custom_smiley_write;
        public weak GLib.Callback destroy_conversation;
        public weak GLib.Callback has_focus;
        public weak GLib.Callback present;
        public weak GLib.Callback send_confirm;
        public weak GLib.Callback write_chat;
        public weak GLib.Callback write_conv;
        public weak GLib.Callback write_im;
    }
    public static void eventloop_set_ui_ops(ref PurpleAmend.EventLoopUiOps ops);
    public void connections_set_ui_ops(ref PurpleAmend.ConnectionUiOps ops);
    public void conversations_set_ui_ops(ref PurpleAmend.ConversationUiOps ops);
}


[CCode (cheader_filename = "purple.h")]
namespace Purple {
    [CCode (cname = "PURPLE_PLUGIN_PROTOCOL_INFO")]
    public unowned PluginProtocolInfo plugin_protocol_info(Plugin prpl);
}
