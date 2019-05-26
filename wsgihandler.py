import os
import tempfile
from http.server import BaseHTTPRequestHandler


class WsgiHandler(BaseHTTPRequestHandler):
    # generic class for SimpleHTTPServer
    # you can use it as a trait
    # so your handler become a wsgi entry point
    # instead of a http socket handler

    def setup(self):
        # override to disable socket dependencies of StreamRequestHandler
        # do_GET will be called outside normal workflow
        self.wfile = tempfile.TemporaryFile()
        self.wsgi_headers = []
        self.wsgi_response = ""

        environ = self.request
        self.request_version = environ['SERVER_PROTOCOL'];
        self.command = environ['REQUEST_METHOD']
        self.directory = os.getcwd()
        self.client_address = environ['REMOTE_ADDR']
        self.path = environ['PATH_INFO']
        self.requestline = self.command + " " + self.path + " " + self.request_version
        self.headers = {}
        for header in environ:
            if header.startswith("HTTP_"):
                self.headers["-".join(map(str.capitalize, header[5:].split("_")))] = environ[header]

    def handle(self):
        mname = 'do_' + self.command
        if hasattr(self, mname):
            method = getattr(self, mname)
            method()

    def get_content(self):
        block_size = 32768
        environ = self.request
        if 'wsgi.file_wrapper' in environ:
            return environ['wsgi.file_wrapper'](self.wfile, block_size)
        else:
            return iter(lambda: self.wfile.read(block_size), '')

    def finish(self):
        self.wfile.flush()
        self.wfile.seek(0)

    def send_response(self, code, message=None):
        self.log_request(code)
        self.wsgi_response = "{} {}".format(code._value_, code.phrase)

    def send_header(self, keyword, value):
        self.wsgi_headers.append((keyword, value))

    def end_headers(self):
        start_response = self.server
        start_response(self.wsgi_response, self.wsgi_headers)



