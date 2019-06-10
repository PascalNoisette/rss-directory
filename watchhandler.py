import os
from http.server import SimpleHTTPRequestHandler

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path


class XmlWatcher(FileSystemEventHandler):

    def __init__(self, websocket):
        self.websocket = websocket

    def on_any_event(self, event):
        if event.src_path == "/app/static" + self.websocket.http_handler.path :
            self.websocket.send_message(self.websocket.http_handler.path + " has changed")


class WatchHandler(SimpleHTTPRequestHandler):

    def on_ws_connected(self, websocket):
        self.log_message('"WS CONNECTED"')
        file = "/app/static" + self.path
        path = os.path.dirname(file)
        self.observer = Observer()
        self.observer.schedule(XmlWatcher(websocket), path, recursive=False)
        self.observer.start()
        # prevent observer created to late to watch forever if file already exists
        if os.path.exists(file):
            Path(file).touch()

    def on_ws_closed(self, websocket):
        self.observer.stop()
        self.log_message('"WS CLOSED"')

    def on_ws_message(self, websocket, message):
        pass
