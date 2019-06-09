from HTTPWebSocketsHandler import HTTPWebSocketsHandler


class SocketHandler(HTTPWebSocketsHandler):

    def parse_request(self):
        parseStatus = super().parse_request()
        if self.headers.get("Upgrade", False) and self.headers.get("Upgrade", None).lower().strip() == "websocket":
            self.command = "SOCKET"
        return parseStatus

    def do_SOCKET(self):
        self._handshake()
        self._read_messages()
