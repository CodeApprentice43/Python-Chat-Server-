import json
from core.websocket import (
    WebSocketConnection,
    WebSocketManager,
    WebSocketFrame,
    create_handshake_response
)
from models.session import get_authenticated_user
from services.chat_service import post_message

ws_manager = WebSocketManager()


def handle_websocket_upgrade(request, client_socket):
    """Handle WebSocket upgrade from HTTP request."""
    print(f"WebSocket upgrade requested from {request.path}")

    websocket_key = None

    for name, value in request.headers.items():
        if name.lower() == 'sec-websocket-key':
            websocket_key = value
            break

    if not websocket_key:
        print("No WebSocket key found")
        return b"HTTP/1.1 400 Bad Request\r\n\r\n"

    auth_token = request.cookies.get('auth_token')
    username = None

    if auth_token:
        username = get_authenticated_user(auth_token)

    print(f"WebSocket connection for user: {username if username else 'guest'}")

    handshake_response = create_handshake_response(websocket_key)
    client_socket.sendall(handshake_response)

    connection = WebSocketConnection(client_socket, username)
    ws_manager.add_connection(connection)

    print(f"Total connections: {ws_manager.get_connection_count()}")

    connection.send_json({
        'type': 'welcome',
        'username': username if username else 'guest'
    })

    broadcast_online_users()

    handle_websocket_messages(connection)


def handle_websocket_messages(connection: WebSocketConnection):
    """Handle incoming WebSocket messages from a connection."""
    buffer = b''

    print(f"Starting message handling for connection")

    while not connection.closed:
        try:
            data = connection.socket.recv(4096)

            if not data:
                print(f"No data received, closing connection")
                break

            buffer += data

            frame = connection.parse_frame(buffer)

            if frame:
                frame_length = len(buffer) - len(frame.payload)
                if frame.opcode == WebSocketFrame.OPCODE_TEXT:
                    payload_length_size = 1
                    if len(buffer) >= 2:
                        payload_len = buffer[1] & 0x7F
                        if payload_len == 126:
                            payload_length_size = 3
                        elif payload_len == 127:
                            payload_length_size = 9

                    masked = (buffer[1] & 0x80) != 0
                    mask_size = 4 if masked else 0

                    total_frame_size = 1 + payload_length_size + mask_size + len(frame.payload)
                    buffer = buffer[total_frame_size:]

                if frame.is_close():
                    connection.send_close()
                    break

                elif frame.is_ping():
                    connection.send_pong(frame.payload)

                elif frame.is_text():
                    try:
                        message_data = json.loads(frame.payload.decode('utf-8'))
                        print(f"Received message data: {message_data}")
                        handle_message(connection, message_data)
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        print(f"Error decoding message: {e}")

        except Exception as e:
            print(f"Error in message handling: {e}")
            break

    print(f"WebSocket connection closed")
    ws_manager.remove_connection(connection)
    broadcast_online_users()


def handle_message(connection: WebSocketConnection, data: dict):
    """Handle different types of WebSocket messages."""
    message_type = data.get('type')

    if message_type == 'chat':
        handle_chat_message(connection, data)

    elif message_type == 'webrtc-offer':
        handle_webrtc_signal(connection, data)

    elif message_type == 'webrtc-answer':
        handle_webrtc_signal(connection, data)

    elif message_type == 'webrtc-ice-candidate':
        handle_webrtc_signal(connection, data)


def handle_chat_message(connection: WebSocketConnection, data: dict):
    """Handle incoming chat message."""
    message_text = data.get('message', '')
    media = data.get('media')

    # Require either message or media
    if not message_text and not media:
        return

    username = connection.username if connection.username else 'guest'

    print(f"Chat message from {username}: {message_text[:50] if message_text else '[media]'}")

    success, result = post_message(username, message_text, media)

    if success:
        print(f"Broadcasting message to {ws_manager.get_connection_count()} connections")
        broadcast_data = {
            'type': 'chat',
            'id': result['id'],
            'username': result['username'],
            'message': result.get('message', '')
        }

        if 'media' in result and result['media']:
            broadcast_data['media'] = result['media']

        ws_manager.broadcast(broadcast_data)
    else:
        print(f"Failed to post message: {result}")


def handle_webrtc_signal(connection: WebSocketConnection, data: dict):
    """Handle WebRTC signaling (offer, answer, ICE candidates)."""
    target_username = data.get('target')

    if not target_username:
        return

    for conn in ws_manager.connections:
        if conn.username == target_username and not conn.closed:
            conn.send_json({
                'type': data.get('type'),
                'from': connection.username,
                'offer': data.get('offer'),
                'answer': data.get('answer'),
                'candidate': data.get('candidate')
            })
            break


def broadcast_online_users():
    """Broadcast updated online users list to all clients."""
    online_users = ws_manager.get_online_users()

    ws_manager.broadcast({
        'type': 'online-users',
        'users': online_users
    })
