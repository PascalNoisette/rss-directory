import optparse
import os
import socketserver

from directoryhandler import DirectoryHandler
from rangehandler import RangeHandler
from imagehandler import ImageHandler
from sockethandler import SocketHandler
from watchhandler import WatchHandler
from wsgihandler import WsgiHandler
from jinjahandler import JinjaHandler


class RssHandler(WatchHandler, SocketHandler, DirectoryHandler, RangeHandler, ImageHandler, JinjaHandler):
    # @todo  : i am starting to need a router
    pass

class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = os.environ.get('DEBUG', False)


class RssHandlerWsgi(WsgiHandler, RssHandler):
    pass

def application(environ, start_response):
    handler = RssHandlerWsgi(environ, environ['REMOTE_ADDR'], start_response)
    return handler.get_content()


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-p", "--port", help="Port", default=5000)
    parser.add_option("-d", "--dir", help="Directory to serve", default="/pub/")
    (option, args) = parser.parse_args()
    os.chdir(option.dir)
    httpd = Server(("", option.port), RssHandler)
    print("serving at port", option.port)
    httpd.serve_forever()
