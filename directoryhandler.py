"""
    Custom Http handler
    Author: Pascal Noisette

"""

import os
import re
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler

import background


class DirectoryHandler(SimpleHTTPRequestHandler):

    def send_head(self):
        try:
            background.file_is_ready(self.translate_path(self.path))
        except BlockingIOError:
            self.send_error(
                HTTPStatus.SERVICE_UNAVAILABLE,
                "Rss currently being generated")
            return None
        return super().send_head()

    def translate_path(self, path):
        """
        Override to serve /app/static/ dir in addition to cwd
        """
        staticfile = "/app/static" + path
        if os.path.exists(staticfile) and os.path.isfile(staticfile) and not os.path.isdir(staticfile):
            return staticfile
        return super().translate_path(path)

    def list_directory(self, path):
        """
        Override to return XML dir listing instead of default dir listing
        """
        file = self.get_rss_filename(path)
        background.generate(path=path, file="/app/static" + file, base_url=self.get_base_url(), pdir=os.getcwd())
        self.send_response(HTTPStatus.FOUND)
        self.send_header("Location", self.get_base_url()+file)
        self.end_headers()

    def get_base_url(self):
        host = self.headers.get("X-Forwarded-Host", self.headers.get("Host"))
        proto = self.headers.get("X-Forwarded-Proto", "http")
        return proto + "://" + host

    @staticmethod
    def get_rss_filename(path):
        file = "/index.xml"
        rel_dir = os.path.relpath(path, os.getcwd())
        if not rel_dir == ".":
            file = "/" + re.sub(r'(?u)[^-\w.]', '', str(rel_dir).strip().replace(' ', '_')) + ".xml"
        return file
