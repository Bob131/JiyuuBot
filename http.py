import urllib
import os
import time
import threading
import socket

exec(open(os.path.join(os.path.dirname(__file__), "configs" + os.sep + "config.py"), "r").read())

class httpd_api:
    def __init__(self, plugman_instance, httpreps):
        global http_responses
        http_responses = httpreps
        self.plugman = plugman_instance
        serv = socket.socket()
        serv.bind((HTTPD_IP, HTTPD_PORT))
        serv.listen(5)
        for x in range(0,4):
            t = threading.Thread(target = self.http_parse, args = (serv,))
            t.daemon = True
            t.start()

    def http_parse(self, sock):
        client, addr = sock.accept()
        req = client.recv(2048)
        path = ""
        for line in req.split("\n"):
            if line.startswith("GET"):
                print "HTTPD: '%s' from %s at %s" % (line, addr, time.strftime("%Y-%m-%d %H:%M:%S"))
                path = line.split(" ")[1]
                break
        path = urllib.unquote_plus(path[1:])
        command = path.split(" ")[0]
        resp_code = "200 OK"
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
            resp_code = "404 Not Found"
        toreturn = "HTTP/1.1 %s\nServer: Jiyuu Radio\nContent-Type: text/plain\n\n%s" % (resp_code, toreturn)
        client.send(toreturn)
        client.close()
