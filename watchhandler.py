import os
import select
from http.server import SimpleHTTPRequestHandler

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path


class XmlWatcher(FileSystemEventHandler):

    def __init__(self, http_handler):
        self.http_handler = http_handler
        self.enabled = True

    def on_any_event(self, event):
        if self.enabled and event.src_path == "/app/static" + self.http_handler.path :
            self.enabled = False
            w = os.fdopen(self.http_handler.signal_pipe, "w")
            w.write("finished")
            w.close()


class WatchHandler(SimpleHTTPRequestHandler):

    def on_ws_connected(self, websocket):
        self.log_message('"WS CONNECTED"')
        file = "/app/static" + self.path
        path = os.path.dirname(file)
        # https://www.tutorialspoint.com/python/os_pipe.htm
        r_pipe, self.signal_pipe = os.pipe()

        self.observer = Observer()
        self.observer.schedule(XmlWatcher(self), path, recursive=False)
        self.observer.start()
        # prevent observer created to late to watch forever if file already exists
        if os.path.exists(file):
            Path(file).touch()

        select.select([self.rfile, r_pipe], [], [self.rfile, r_pipe])
        self.observer.stop()
        websocket.send_message(self.path + " has changed")

    def on_ws_closed(self, websocket):
        self.observer.stop()
        self.log_message('"WS CLOSED"')

    def on_ws_message(self, websocket, message):
        pass
