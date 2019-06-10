
"""
    Custom Http handler
    Author: Pascal Noisette

"""

import os
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler

import re


class RangeHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        """
        Overridden to seek in file thanks to devgianlu
        https://gist.github.com/devgianlu/018b299f8817bf92350bf7bf70214e4d
        """
        self.range_from, self.range_to = self._get_range_header()
        if self.range_from is None:
            return super().do_GET()

        f = self.send_range_head()
        if f:
            self.copy_file_range(f, self.wfile)
            f.close()

    def _get_range_header(self):
        """ Returns request Range start and end if specified.
        If Range header is not specified returns (None, None)
        """
        range_header = self.headers.get("Range")
        if range_header is None:
            return (None, None)
        if not range_header.startswith("bytes="):
            print("Not implemented: parsing header Range: %s" % range_header)
            return (None, None)
        regex = re.compile(r"^bytes=(\d+)\-(\d+)?")
        rangething = regex.search(range_header)
        if rangething:
            from_val = int(rangething.group(1))
            if rangething.group(2) is not None:
                return (from_val, int(rangething.group(2)))
            else:
                return (from_val, None)
        else:
            print('CANNOT PARSE RANGE HEADER:', range_header)
            return (None, None)

    def send_range_head(self):
        """Common code for GET and HEAD commands.
        This sends the response code and MIME headers.
        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.
        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            return super().send_head()

        if not os.path.exists(path) and path.endswith('/data'):
            # FIXME: Handle grits-like query with /data appended to path
            # stupid grits
            if os.path.exists(path[:-5]):
                path = path[:-5]

        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        if self.range_from is None:
            self.send_response(HTTPStatus.OK)
        else:
            self.send_response(HTTPStatus.PARTIAL_CONTENT)

        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        file_size = fs.st_size
        if self.range_from is not None:
            if self.range_to is None or self.range_to >= file_size:
                self.range_to = file_size-1
            self.send_header("Content-Range",
                             "bytes %d-%d/%d" % (self.range_from,
                                                 self.range_to,
                                                 file_size))
            # Add 1 because ranges are inclusive

            self.send_header("Content-Length", "%d" %
                             (1 + self.range_to - self.range_from))
        else:
            self.send_header("Content-Length", str(file_size))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def copy_file_range(self, in_file, out_file):
        """ Copy only the range in self.range_from/to. """
        in_file.seek(self.range_from)
        # Add 1 because the range is inclusive
        left_to_copy = 1 + self.range_to - self.range_from
        buf_length = 64*1024
        bytes_copied = 0
        while bytes_copied < left_to_copy:
            read_buf = in_file.read(min(buf_length, left_to_copy))
            if len(read_buf) == 0:
                break
            out_file.write(read_buf)
            bytes_copied += len(read_buf)

        return bytes_copied
