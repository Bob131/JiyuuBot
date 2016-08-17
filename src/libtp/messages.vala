namespace Tp {
    [Flags]
    public enum MessageSendFlags {
        NONE = 0,
        REPORT_DELIVERY,
        REPORT_READ,
        REPORT_DELETED
    }

    public enum MessageType {
        NORMAL,
        ACTION,
        NOTICE,
        AUTO_REPLY,
        DELIVERY_REPORT
    }

    internal unowned T get_val<T>(Variant? variant, char type) {
        if (variant == null)
            return null;
        unowned T ret;
        ((!) variant).get(type.to_string(), out ret);
        return ret;
    }

    public struct Message {
        HashTable<string, Variant?>[] parts;

        public string? token {owned get {
            return get_val(parts[0]["message-token"], 's');
        }}
        // return of '0' indicates absent value
        public int64 received_timestamp {get {
            return get_val(parts[0]["message-received"], 'x');
        }}
        public string? sender_nick {get {
            return get_val(parts[0]["sender-nickname"], 's');
        }}
        public MessageType message_type {
            get {
                return get_val(parts[0]["message-type"], 'u');
            }
            set {
                return_if_fail(value != MessageType.DELIVERY_REPORT);
                parts[0]["message-type"] = new Variant("u", value);
            }
        }
        public bool scrollback {get {
            return get_val(parts[0]["scrollback"], 'b');
        }}
        public bool rescued {get {
            return get_val(parts[0]["rescued"], 'b');
        }}

        public string? to_text() {
            string? ret = null;
            foreach (var part in parts[1:parts.length]) {
                var type = part["content-type"];
                if (type != null && ((!) type).get_string() == "text/plain") {
                    ret = get_val<string>(part["content"], 's').strip();
                    break;
                }
            }
            return ret;
        }
    }
}
