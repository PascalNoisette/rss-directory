import os
from http.server import SimpleHTTPRequestHandler

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from HTTPWebSocketsHandler import HTTPWebSocketsHandler

class XmlWatcher(FileSystemEventHandler):

    def __init__(self, websocket):
        self.websocket = websocket

    def on_any_event(self, event):
        if event.src_path == "/app/static" + self.websocket.path :
            self.websocket.send_message(self.websocket.path + " has changed")


class WatchHandler(HTTPWebSocketsHandler):

    def on_ws_connected(self):
        self.log_message('"WS CONNECTED"')
        file = "/app/static" + self.path
        path = os.path.dirname(file)
        self.observer = Observer()
        self.observer.schedule(XmlWatcher(self), path, recursive=False)
        self.observer.start()
        # prevent observer created to late to watch forever if file already exists
        if os.path.exists(file):
            Path(file).touch()

    def on_ws_message(self, message):
        self.log_message('"WS IN"')

    def on_ws_closed(self):
        self.log_message('"WS CLOSED"')
        self.observer.stop()

    def send_message(self, message):
        self.log_message('"WS OUT"')
        super().send_message(message)
