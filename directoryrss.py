import optparse
import os
import socketserver

from rangehandler import RangeHandler

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-p", "--port", help="Port", default=5000)
    parser.add_option("-d", "--dir", help="Directory to serve", default="/pub/")
    (option, args) = parser.parse_args()
    os.chdir(option.dir)
    httpd = socketserver.ThreadingTCPServer(("", option.port), RangeHandler)
    print("serving at port", option.port)
    httpd.serve_forever()
