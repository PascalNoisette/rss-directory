import os
import tempfile
from http.server import BaseHTTPRequestHandler

try:
    import uwsgi
except ImportError:
    pass

class WsgiFileWrapper:
    def __init__(self, fd):
        self.fd = fd

    def fileno(self):
        return self.fd

class WsgiHandler(BaseHTTPRequestHandler):
    # generic class for SimpleHTTPServer
    # you can use it as a trait
    # so your handler become a wsgi entry point
    # instead of a http socket handler

    def setup(self):
        # override to disable socket dependencies of StreamRequestHandler
        # do_GET will be called outside normal workflow
        self.wfile = tempfile.TemporaryFile()
        self.rfile =  WsgiFileWrapper(uwsgi.connection_fd())# https://github.com/unbit/uwsgi/blob/master/tests/websockets_chat_async.py
        self.wsgi_headers = []
        self.wsgi_response = ""

        environ = self.request
        os.chdir(environ['DOCUMENT_ROOT'] + "/")
        self.request_version = environ['SERVER_PROTOCOL'];
        if 'HTTP_SEC_WEBSOCKET_KEY' in environ:
            uwsgi.websocket_handshake(environ['HTTP_SEC_WEBSOCKET_KEY'], environ.get('HTTP_ORIGIN', ''))
            environ['REQUEST_METHOD'] = 'SOCKET'
            self.http_handler = self
        self.command = environ['REQUEST_METHOD']
        self.directory = os.getcwd()
        self.client_address = environ['REMOTE_ADDR']
        self.path = environ['PATH_INFO']
        self.requestline = self.command + " " + self.path + " " + self.request_version
        self.headers = {}
        for header in environ:
            if header.startswith("HTTP_"):
                self.headers["-".join(map(str.capitalize, header[5:].split("_")))] = environ[header]
            if header.startswith("X"):
                self.headers[header] = environ[header]


    def do_SOCKET(self):
        self.on_ws_connected(self)

    def send_message(self, message):
        uwsgi.websocket_send(message)


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



