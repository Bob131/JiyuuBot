import re
import requests
import humanize
from . import send, regex_handler, functions, _dispatch_ready

handlers = {}

@functions
def http_link_handler(regex):
    """
        Convenience decorator for handling URLs.

        Registers decorated function to handle lines containing a URL.
    """
    def register(f):
        handlers[regex] = _dispatch_ready(f)
    return register


@functions
def headers_to_readable(headers, url=None):
    readable = ""
    if 'content-type' in headers:
        headers['content-type'] = re.split(";\s?",
                headers['content-type'])[0]
        readable += headers['content-type']
    else:
        return
    if 'content-length' in headers and \
            headers['content-length'].isdigit():
        readable += ', {}'.format(humanize.naturalsize(
            headers['content-length'], binary=True))
    else:
        # set to arbitrarily large number to avoid DoS
        headers['content-length'] = '999999999'

    if headers['content-type'].startswith('text/html') and url and \
            int(headers['content-length']) < 1048576:
        try:
            r = requests.get(url).text
            # anger the regex gods
            title = re.findall("<title>(.*?)</title>", r)[0]
            readable = "{} [{}]".format(title, readable)
        except:
            pass

    return readable or None


@regex_handler("\\bhttps?://\w+")
def link_dispatch(msg):
    for regex in handlers:
        if re.search(regex, msg['msg']):
            handlers[regex](msg=msg, matches=re.findall(regex, msg['msg']))
            return

    links = re.findall("\\b(https?://[^\s]*)\\b", msg['msg'])
    if len(links) > 1:
        return # don't bother
    try:
        r = requests.head(links[0])
        info = functions.headers_to_readable(r.headers, links[0])
        assert(info != None)
        send(info)
    except:
        pass
