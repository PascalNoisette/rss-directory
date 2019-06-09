import asyncio
import await
from websockets import WebSocketServerProtocol
from http.server import SimpleHTTPRequestHandler, HTTPStatus
from websockets.handshake import check_request, accept
from websockets.extensions.permessage_deflate import ServerPerMessageDeflateFactory

@asyncio.coroutine
def serve(rfile, wfile):
    handler = WebSocketServerProtocol(hello, None, extensions=[ServerPerMessageDeflateFactory()])
    rstream = asyncio.StreamReader()
    rstream.set_transport(rfile)
    wstream = asyncio.StreamWriter(wfile, asyncio.StreamReaderProtocol(rstream), rstream)
    handler.client_connected(rstream, wstream)

class WebSocketHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.headers.get("Upgrade", None) != "websocket":
            return super().do_GET()

        self.send_response(HTTPStatus.SWITCHING_PROTOCOLS)
        self.send_header('Upgrade', 'websocket')
        self.send_header('Sec-Websocket-Extensions', 'permessage-deflate')
        self.send_header('Connection', 'Upgrade')
        self.send_header('Sec-WebSocket-Accept', accept(check_request(self.headers)))
        self.end_headers()

        asyncio.get_event_loop().run_until_complete(serve(self.rfile, self.wfile))

    def finish(self):
        if hasattr(self, "header") and self.headers.get("Upgrade", None) != "websocket":
            return super().finish()

        if not self.wfile.closed:
                self.wfile.flush()



async def hello(websocket, path):
    async for message in websocket:
        await websocket.send("echoing : " + message)

if __name__ == "__main__":
    import websockets
    start_server = websockets.serve(hello, 'localhost', 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()