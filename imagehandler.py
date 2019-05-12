"""
    Custom Http handler
    Author: Pascal Noisette

"""

from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from tinytag import TinyTag

class ImageHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        """Serve image"""
        path = self.translate_path(self.path)

        if not path.endswith(".mp3.png"):
            return super().do_GET()

        try:
            file = path[:-len(".png")]
            tag = TinyTag.get(file, image=True)
            image = tag.get_image()
            assert image is not None
        except (OSError, AssertionError):
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "image/png")
        self.send_header("Content-Length", len(image))
        self.end_headers()
        self.wfile.write(image)

