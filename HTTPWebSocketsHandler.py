'''
The MIT License (MIT)

Copyright (C) 2014, 2015 Seven Watt <info@sevenwatt.com>
<http://www.sevenwatt.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import sys
import codecs
import struct
import errno, socket #for socket exceptions
import threading
import traceback
from base64 import b64encode
from hashlib import sha1

VER = sys.version_info[0]
if VER >= 3:
    from http.server import SimpleHTTPRequestHandler
    from io import StringIO
    from email.message import Message
else:
    from StringIO import StringIO
    from mimetools import Message
    from SimpleHTTPServer import SimpleHTTPRequestHandler

class WebSocketError(Exception):
    pass

class HTTPWebSocketsHandler:
    _ws_GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    _opcode_continu = 0x0
    _opcode_text = 0x1
    _opcode_binary = 0x2
    _opcode_close = 0x8
    _opcode_ping = 0x9
    _opcode_pong = 0xa

    def __init__(self, http_handler):
        self.http_handler=http_handler
        self._handshake()
        self._read_messages()

    mutex = threading.Lock()

    def send_message(self, message):
        self._send_message(self._opcode_text, message)

    def _read_messages(self):
        while self.connected == True:
            try:
                self._read_next_message()
            except (socket.error, WebSocketError) as e:
                #websocket content error, time-out or disconnect.
                self.http_handler.log_message("RCV: Close connection: Socket Error %s" % str(e.args))
                self._ws_close()
            except Exception as err:
                #unexpected error in websocket connection.
                traceback.print_exc()
                self.http_handler.log_error("RCV: Exception: in _read_messages: %s" % str(err.args))
                self._ws_close()

    def _read_bytes(self, length):
        # print(" read_bytes(%d)"%(length))
        raw_data = self.http_handler.rfile.read(length)
        return raw_data

    def _read_next_message(self):
        #self.rfile.read(n) is blocking.
        #it returns however immediately when the socket is closed.
        try:
            byte = self._read_bytes(1)
            self.opcode = ord(byte) & 0x0F
            # print("op : ", self.opcode)
            length = ord(self._read_bytes(1)) & 0x7F
            # print("length : ", length)
            if length == 126:
                length = struct.unpack(">H", self._read_bytes(2))[0]
            elif length == 127:
                length = struct.unpack(">Q", self._read_bytes(8))[0]
            masks = self._read_bytes(4)
            # print("MASKS : {}".format(masks))
            decoded = None
            if VER >= 3:
                decoded = bytearray()
            else:
                decoded = ''
            datastream = self._read_bytes(length)
            # print("datastream : {}".format(datastream))
            for char in datastream:
                if VER >= 3:
                    decoded.append(char ^ masks[len(decoded) % 4])
                else:
                    decoded += chr(ord(char) ^ ord(masks[len(decoded) % 4]))

            if VER >= 3:
                decoded = bytes(decoded)
                # print("length of decdoecd = {}".format(len(decoded)))
                # print("length of decdoecd.decode() = {}".format(len(decoded.decode())))
            self._on_message(decoded)
        except (struct.error, TypeError) as e:
            traceback.print_exc()
            #catch exceptions from ord() and struct.unpack()
            if self.connected:
                raise WebSocketError("Websocket read aborted while listening")
            else:
                #the socket was closed while waiting for input
                self.http_handler.log_error("RCV: _read_next_message aborted after closed connection")
                pass

    def _send_impl(self, msg):
        # print("_send_impl .... {}".format(type(msg)))
        global VER
        if VER >= 3:
            data = bytearray()
            if type(msg) == int:
                data = bytes([msg])
            elif type(msg) == bytes:
                data = msg
            elif type(msg) == str:
                data = msg.encode()
            self.http_handler.request.send(data)
        else:
            data = msg
            if type(msg) == int:
                data = chr(msg)
            self.http_handler.request.send(data)

    def _send_message(self, opcode, message):
        try:
            #use of self.wfile.write gives socket exception after socket is closed. Avoid.
            self._send_impl(0x80 + opcode)
            length = len(message)
            if length <= 125:
                self._send_impl(length)
            elif length >= 126 and length <= 65535:
                self._send_impl(126)
                self._send_impl(struct.pack(">H", length))
            else:
                self._send_impl(127)
                self._send_impl(struct.pack(">Q", length))
            if length > 0:
                # print("_send_message : lenght = {}".format(length))
                self._send_impl(message)
        except socket.error as e:
            #websocket content error, time-out or disconnect.
            traceback.print_exc()
            self.http_handler.log_message("SND: Close connection: Socket Error %s" % str(e.args))
            self._ws_close()
        except Exception as err:
            #unexpected error in websocket connection.
            traceback.print_exc()
            self.http_handler.log_error("SND: Exception: in _send_message: %s" % str(err.args))
            self._ws_close()

    def _handshake(self):
        headers=self.http_handler.headers
        if headers.get("Upgrade", None) != "websocket":
            return
        key = headers['Sec-WebSocket-Key'].strip()
        coded_ID = (key + self._ws_GUID).encode("ascii")
        hexed = sha1(coded_ID).hexdigest()
        hex_decoded = codecs.decode(hexed, 'hex_codec')
        digest = b64encode(hex_decoded).decode()
        self.http_handler.send_response(101, 'Switching Protocols')
        self.http_handler.send_header('Upgrade', 'websocket')
        self.http_handler.send_header('Connection', 'Upgrade')
        self.http_handler.send_header('Sec-WebSocket-Accept', digest)
        self.http_handler.end_headers()
        self.connected = True
        #self.close_connection = 0
        self.http_handler.on_ws_connected(self)

    def _ws_close(self):
        #avoid closing a single socket two time for send and receive.
        self.mutex.acquire()
        try:
            if self.connected:
                self.connected = False
                #Terminate BaseHTTPRequestHandler.handle() loop:
                self.close_connection = 1
                #send close and ignore exceptions. An error may already have occurred.
                try:
                    self._send_close()
                except:
                    pass
                self.http_handler.on_ws_closed(self)
            else:
                self.http_handler.log_message("_ws_close websocket in closed state. Ignore.")
                pass
        finally:
            self.mutex.release()

    def _on_message(self, message):
        #self.log_message("_on_message: opcode: %02X msg: %s" % (self.opcode, message))

        # close
        if self.opcode == self._opcode_close:
            self.connected = False
            #Terminate BaseHTTPRequestHandler.handle() loop:
            self.http_handler.close_connection = 1
            try:
                self._send_close()
            except:
                pass
            self.http_handler.on_ws_closed(self)
        # ping
        elif self.opcode == self._opcode_ping:
            self._send_message(self._opcode_pong, message)
        # pong
        elif self.opcode == self._opcode_pong:
            pass
        # data
        elif (self.opcode == self._opcode_continu or
                self.opcode == self._opcode_text or
                self.opcode == self._opcode_binary):
            self.http_handler.on_ws_message(self, message)

    def _send_close(self):
        #Dedicated _send_close allows for catch all exception handling
        msg = bytearray()
        msg.append(0x80 + self._opcode_close)
        msg.append(0x00)
        # print(" >> _send_close")
        self._send_impl(msg)
