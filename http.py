import mtwsgi.mtwsgi as mtwsgi
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
        self.httpd = mtwsgi.make_server(HTTPD_IP, HTTPD_PORT, self.http_parse, 4)
        self.httpd.serve_forever()

    def http_parse(self, environ, start_response):
        path = environ["PATH_INFO"][1:]
        path = urllib.unquote_plus(path)
        command = path.split(" ")[0]
        toreturn = ""
        if path == "robots.txt":
            toreturn = "User-agent: *\nDisallow: /"
        elif command in self.plugman.httplist.keys():
            tid = self.plugman.execute_command(path, "HTTP")
            for x in range(0,10):
                if tid in http_responses.keys():
                    break
                time.sleep(1)
            try:
                toreturn = http_responses[tid]
                del http_responses[tid]
            except KeyError:
                toreturn = "\"No output\""
        else:
            toreturn = "\"Invalid command\""
        start_response("200 OK", [("Content-type", "text/plain")])
        return [toreturn]
