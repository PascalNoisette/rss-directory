"""
    Custom Http handler
    Author: Pascal Noisette

"""

import io
import os
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler

from itunes import ItunesRSS2, ItunesRSSItem, isValidItunesRSSItem


class DirectoryHandler(SimpleHTTPRequestHandler):

    def translate_path(self, path):
        """
        Override to serve /app/static/ dir in addition to cwd
        """
        staticfile = "/app/static" + path
        if os.path.exists(staticfile) and os.path.isfile(staticfile) and not os.path.isdir(staticfile):
            return staticfile
        return super().translate_path(path)

    def get_items(self, root_dir):
        for dir_, _, files in os.walk(root_dir):
            for file_name in files:
                rel_dir = os.path.relpath(dir_, root_dir)
                rel_file = os.path.join(rel_dir, file_name)
                full_name = os.path.join(dir_, file_name)
                if os.path.isfile(rel_file) and isValidItunesRSSItem(rel_file):
                    yield ItunesRSSItem(self.get_base_url(), rel_file, full_name)

    def list_directory(self, path):
        """
        Override to return XML dir listing instead of default dir listing
        """
        encoding = sys.getfilesystemencoding()
        try:
            file = "/index.xml"
            f = io.open("/app/static" + file, "w")
            ItunesRSS2(self.get_base_url(), path, self.get_items(path)).write_xml(f, encoding)
            f.close()
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", self.get_base_url()+file)
            self.end_headers()
        except OSError:
            self.send_error(
                HTTPStatus.NOT_FOUND,
                "No permission to list directory")

        return None

    def get_base_url(self):
        host = self.headers.get("X-Forwarded-Host", self.headers.get("Host"))
        proto = self.headers.get("X-Forwarded-Proto", "http")
        return proto + "://" + host
