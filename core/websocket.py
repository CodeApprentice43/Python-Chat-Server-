import hashlib
import base64
import struct
import json
from typing import Optional


class WebSocketFrame:

    OPCODE_CONTINUATION = 0x0
    OPCODE_TEXT = 0x1
    OPCODE_BINARY = 0x2
    OPCODE_CLOSE = 0x8
    OPCODE_PING = 0x9
    OPCODE_PONG = 0xA

    def __init__(self, fin: bool, opcode: int, payload: bytes):
        self.fin = fin
        self.opcode = opcode
        self.payload = payload

    def is_text(self) -> bool:
        return self.opcode == self.OPCODE_TEXT

    def is_binary(self) -> bool:
        return self.opcode == self.OPCODE_BINARY

    def is_close(self) -> bool:
        return self.opcode == self.OPCODE_CLOSE

    def is_ping(self) -> bool:
        return self.opcode == self.OPCODE_PING

    def is_pong(self) -> bool:
        return self.opcode == self.OPCODE_PONG


class WebSocketConnection:

    def __init__(self, socket, username: Optional[str] = None):
        self.socket = socket
        self.username = username
        self.buffer = b''
        self.closed = False

    def send_frame(self, opcode: int, payload: bytes):
        if self.closed:
            return

        frame = bytearray()

        frame.append(0x80 | opcode)

        payload_len = len(payload)
        if payload_len <= 125:
            frame.append(payload_len)
        elif payload_len <= 65535:
            frame.append(126)
            frame.extend(struct.pack('!H', payload_len))
        else:
            frame.append(127)
            frame.extend(struct.pack('!Q', payload_len))

        frame.extend(payload)

        try:
            self.socket.sendall(bytes(frame))
        except:
            self.closed = True

    def send_text(self, message: str):
        self.send_frame(WebSocketFrame.OPCODE_TEXT, message.encode('utf-8'))

    def send_json(self, data: dict):
        self.send_text(json.dumps(data))

    def send_pong(self, payload: bytes):
        self.send_frame(WebSocketFrame.OPCODE_PONG, payload)

    def send_close(self):
        self.send_frame(WebSocketFrame.OPCODE_CLOSE, b'')
        self.closed = True

    def parse_frame(self, data: bytes) -> Optional[WebSocketFrame]:
        if len(data) < 2:
            return None

        fin = (data[0] & 0x80) != 0
        opcode = data[0] & 0x0F

        masked = (data[1] & 0x80) != 0
        payload_len = data[1] & 0x7F

        offset = 2

        if payload_len == 126:
            if len(data) < offset + 2:
                return None
            payload_len = struct.unpack('!H', data[offset:offset+2])[0]
            offset += 2
        elif payload_len == 127:
            if len(data) < offset + 8:
                return None
            payload_len = struct.unpack('!Q', data[offset:offset+8])[0]
            offset += 8

        if masked:
            if len(data) < offset + 4:
                return None
            mask = data[offset:offset+4]
            offset += 4

        if len(data) < offset + payload_len:
            return None

        payload = data[offset:offset+payload_len]

        if masked:
            payload = bytes(payload[i] ^ mask[i % 4] for i in range(len(payload)))

        return WebSocketFrame(fin, opcode, payload)


class WebSocketManager:

    def __init__(self):
        self.connections = []

    def add_connection(self, connection: WebSocketConnection):
        self.connections.append(connection)

    def remove_connection(self, connection: WebSocketConnection):
        if connection in self.connections:
            self.connections.remove(connection)

    def broadcast(self, message: dict, exclude: Optional[WebSocketConnection] = None):
        dead_connections = []

        for conn in self.connections:
            if conn == exclude or conn.closed:
                if conn.closed:
                    dead_connections.append(conn)
                continue

            try:
                conn.send_json(message)
            except:
                conn.closed = True
                dead_connections.append(conn)

        for conn in dead_connections:
            self.remove_connection(conn)

    def broadcast_to_authenticated(self, message: dict):
        dead_connections = []

        for conn in self.connections:
            if not conn.username or conn.closed:
                if conn.closed:
                    dead_connections.append(conn)
                continue

            try:
                conn.send_json(message)
            except:
                conn.closed = True
                dead_connections.append(conn)

        for conn in dead_connections:
            self.remove_connection(conn)

    def get_online_users(self) -> list[str]:
        users = set()
        for conn in self.connections:
            if conn.username and not conn.closed:
                users.add(conn.username)
        return sorted(list(users))

    def get_connection_count(self) -> int:
        return len([c for c in self.connections if not c.closed])


def compute_accept_key(websocket_key: str) -> str:
    magic_string = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    combined = websocket_key + magic_string
    sha1_hash = hashlib.sha1(combined.encode()).digest()
    return base64.b64encode(sha1_hash).decode()


def create_handshake_response(websocket_key: str) -> bytes:
    accept_key = compute_accept_key(websocket_key)

    response_lines = [
        "HTTP/1.1 101 Switching Protocols",
        "Upgrade: websocket",
        "Connection: Upgrade",
        f"Sec-WebSocket-Accept: {accept_key}",
        "",
        ""
    ]

    return "\r\n".join(response_lines).encode()
