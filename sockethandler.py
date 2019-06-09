from base64 import b64encode, b64decode
from hashlib import sha1

from HTTPWebSocketsHandler import HTTPWebSocketsHandler


class SocketHandler(HTTPWebSocketsHandler):
    def on_ws_message(self, message):
        print(message)

    def on_ws_connected(self):
        """Override this handler."""
        pass

    def on_ws_closed(self):
        """Override this handler."""
        pass

    def parse_request(self):
        parseStatus = super().parse_request()
        if self.headers.get("Upgrade", False) and self.headers.get("Upgrade", None).lower().strip() == "websocket":
            self.command = "SOCKET"
        return parseStatus


    def do_SOCKET(self):
        self._handshake()
        self._read_messages()