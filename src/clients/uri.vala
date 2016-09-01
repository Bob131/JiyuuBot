Soup.Session session;
Soup.ContentSniffer content_sniffer;

async bool is_sane_request(string uri_string) {
    var uri = new Soup.URI(uri_string);

    Soup.Address? address = null;
    var status = Soup.Status.NONE;
    session.prefetch_dns(uri.get_host(), null, (addr, s) => {
        address = addr;
        status = (Soup.Status) s;
        is_sane_request.callback();
    });
    yield;

    if (status != Soup.Status.OK) {
        debug("DNS prefetch for '%s' failed: %s", uri_string,
            Soup.Status.get_phrase(status));
        return false;
    }

    return_if_fail(address != null);
    var g_address = (InetSocketAddress) ((!) address).get_gsockaddr();
    var inet_address = g_address.get_address();

    if (inet_address.is_link_local
            || inet_address.is_loopback
            || inet_address.is_multicast
            || inet_address.is_site_local
            || inet_address.is_any) {
        debug("Rejecting request for '%s', looks like a local address",
            uri_string);
        return false;
    }

    return true;
}

// handle it in an async function to avoid lots of nested callbacks
async string? get_description(string uri) {
    if (!(yield is_sane_request(uri)))
        return null;

    var message = new Soup.Message("GET", uri);

    size_t received = 0;
    message.got_chunk.connect((buf) => {
        received += buf.length;
        // arbitrary value attained by trial-and-error
        if (received > 40960)
            session.cancel_message(message, Soup.Status.CANCELLED);
    });

    session.queue_message(message, () => {
        get_description.callback();
    });
    yield;

    if (!(message.status_code == Soup.Status.OK
            || message.status_code == Soup.Status.CANCELLED)) {
        debug("Request for '%s' failed: %s", uri, message.reason_phrase);
        return null;
    }

    var data = message.response_body.flatten();
    HashTable<string, string>? @params;
    var type = content_sniffer.sniff(message, data, out @params);

    var ret = type.dup();

    var content_length = message.response_headers.get_content_length();
    if (content_length != 0)
        ret += ", " + format_size(content_length, FormatSizeFlags.IEC_UNITS);

    if (type == "text/html") {
        return_if_fail(@params != null);
        string? charset = ((!) @params)["charset"];

        var document = Html.Doc.read_doc((string) data.data, "",
            charset != null ? charset : "utf-8",
            Html.ParserOption.RECOVER | Html.ParserOption.NOERROR
            | Html.ParserOption.NOWARNING);

        var titles =
            new Xml.XPath.Context(document).eval("//title")->nodesetval;
        if (titles->length() > 0)
            try {
                var title =
                    /\s+/s.replace(titles->item(0)->get_content(), -1, 0, " ");
                ret = @"$(title.strip()) [$ret]";
            } catch {}
    }

    return ret;
}

int main(string[] args) {
    var client = new JiyuuBot.RegexClient(/(https?:\/\/[^\s]+)/i);
    session = new Soup.Session();
    content_sniffer = new Soup.ContentSniffer();

    client.regex_match.connect((context, match) => {
        var matches = match.fetch_all();
        // start from 1 since the zeroth element is the entire string
        for (var i = 1; i < int.min(matches.length, 3); i++)
            get_description.begin(matches[i], (obj, res) => {
                var uri_description = get_description.end(res);
                if (uri_description != null)
                    context.reply.begin((!) uri_description);
            });
    });

    var app = new JiyuuBot.ClientApp();
    app.register(client);

    return app.run(args);
}
