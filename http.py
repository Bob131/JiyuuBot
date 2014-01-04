import wsgiref.simple_server
import urllib
import threading
import os
import time

exec(open(os.path.join(os.path.dirname(__file__), "configs" + os.sep + "config.py"), "r").read())

class httpd_api:
    def __init__(self, plugman_instance, httpreps):
        global http_responses
        http_responses = httpreps
        self.plugman = plugman_instance
        self.httpd = wsgiref.simple_server.make_server(HTTPD_IP, HTTPD_PORT, self.http_parse)
        t = threading.Thread(target = self.httpd.serve_forever)
        t.daemon = True
        t.start()

    def http_parse(self, environ, start_response):
        path = environ["PATH_INFO"][1:].replace("/", "")
        path = urllib.unquote_plus(path)
        toreturn = ""
        if path == "robots.txt":
            toreturn = "User-agent: *\nDisallow: /"
        else:
            tid = self.plugman.execute_command(path, "HTTP")
            while 1:
                if tid in http_responses.keys():
                    break
                time.sleep(1)
            toreturn = http_responses[tid]
            del http_responses[tid]
        start_response("200 OK", [("Content-type", "text/plain")])
        return [toreturn]
