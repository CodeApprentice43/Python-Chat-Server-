import struct
from core.websocket import (
    compute_accept_key,
    create_handshake_response,
    WebSocketFrame,
    WebSocketConnection,
    WebSocketManager
)


def test_compute_accept_key():
    """Test Sec-WebSocket-Accept computation."""
    key = "dGhlIHNhbXBsZSBub25jZQ=="
    expected = "s3pPLMBiTxaQ9kYGzzhZRbK+xOo="

    result = compute_accept_key(key)
    assert result == expected, f"Expected {expected}, got {result}"
    print("✓ Sec-WebSocket-Accept computation correct")


def test_handshake_response():
    """Test WebSocket handshake response generation."""
    key = "dGhlIHNhbXBsZSBub25jZQ=="

    response = create_handshake_response(key)
    response_str = response.decode()

    assert "HTTP/1.1 101 Switching Protocols" in response_str
    assert "Upgrade: websocket" in response_str
    assert "Connection: Upgrade" in response_str
    assert "Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=" in response_str
    print("✓ WebSocket handshake response correct")


def test_frame_parsing():
    """Test parsing WebSocket frames."""

    frame_data = bytearray()
    frame_data.append(0x81)
    frame_data.append(0x85)
    mask = b'\x37\xfa\x21\x3d'
    frame_data.extend(mask)
    message = b'Hello'
    masked_message = bytes(message[i] ^ mask[i % 4] for i in range(len(message)))
    frame_data.extend(masked_message)

    class MockSocket:
        pass

    conn = WebSocketConnection(MockSocket())
    frame = conn.parse_frame(bytes(frame_data))

    assert frame is not None
    assert frame.fin == True
    assert frame.opcode == WebSocketFrame.OPCODE_TEXT
    assert frame.payload == b'Hello'
    print("✓ WebSocket frame parsing correct")


def test_frame_parsing_extended_payload():
    """Test parsing frames with extended payload length."""

    frame_data = bytearray()
    frame_data.append(0x81)
    frame_data.append(0xFE)
    payload_len = 200
    frame_data.extend(struct.pack('!H', payload_len))
    mask = b'\x12\x34\x56\x78'
    frame_data.extend(mask)
    message = b'A' * payload_len
    masked_message = bytes(message[i] ^ mask[i % 4] for i in range(len(message)))
    frame_data.extend(masked_message)

    class MockSocket:
        pass

    conn = WebSocketConnection(MockSocket())
    frame = conn.parse_frame(bytes(frame_data))

    assert frame is not None
    assert frame.payload == b'A' * payload_len
    print("✓ Extended payload length parsing correct")


def test_websocket_manager():
    """Test WebSocket connection manager."""
    manager = WebSocketManager()

    class MockSocket:
        def sendall(self, data):
            pass

    conn1 = WebSocketConnection(MockSocket(), "alice")
    conn2 = WebSocketConnection(MockSocket(), "bob")
    conn3 = WebSocketConnection(MockSocket())

    manager.add_connection(conn1)
    manager.add_connection(conn2)
    manager.add_connection(conn3)

    assert manager.get_connection_count() == 3

    online_users = manager.get_online_users()
    assert len(online_users) == 2
    assert "alice" in online_users
    assert "bob" in online_users

    manager.remove_connection(conn1)
    assert manager.get_connection_count() == 2

    online_users = manager.get_online_users()
    assert len(online_users) == 1
    assert "bob" in online_users

    print("✓ WebSocket manager working correctly")


def test_opcode_detection():
    """Test WebSocket opcode detection methods."""
    text_frame = WebSocketFrame(True, WebSocketFrame.OPCODE_TEXT, b'hello')
    assert text_frame.is_text() == True
    assert text_frame.is_close() == False

    close_frame = WebSocketFrame(True, WebSocketFrame.OPCODE_CLOSE, b'')
    assert close_frame.is_close() == True
    assert close_frame.is_text() == False

    ping_frame = WebSocketFrame(True, WebSocketFrame.OPCODE_PING, b'')
    assert ping_frame.is_ping() == True
    assert ping_frame.is_pong() == False

    print("✓ Opcode detection methods correct")


if __name__ == '__main__':
    print("Running WebSocket tests...\n")

    test_compute_accept_key()
    test_handshake_response()
    test_frame_parsing()
    test_frame_parsing_extended_payload()
    test_websocket_manager()
    test_opcode_detection()

    print("\n✅ All WebSocket tests passed!")
