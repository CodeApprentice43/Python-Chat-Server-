import socket
import os
import threading
from core.request import Request
from core.response import Response
from core.router import Router
from routes import auth, chat, files
from routes.websocket import handle_websocket_upgrade

HOST = '0.0.0.0'
PORT = 8080
STATIC_DIR = 'public'

main_router = Router()


def register_routes():
    """Register all application routes."""
    for route in auth.router.routes:
        main_router.routes.append(route)

    for route in chat.router.routes:
        main_router.routes.append(route)

    for route in files.router.routes:
        main_router.routes.append(route)


def serve_static_file(path: str) -> bytes:
    """Serve static files from public directory."""
    if path == '/':
        path = '/index.html'

    if '..' in path or path.startswith('/'):
        path = path.lstrip('/')

    filepath = os.path.join(STATIC_DIR, path)

    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        response = Response.not_found(b"File not found")
        return response.to_bytes()

    try:
        with open(filepath, 'rb') as f:
            content = f.read()

        content_type = 'text/html'
        if filepath.endswith('.css'):
            content_type = 'text/css'
        elif filepath.endswith('.js'):
            content_type = 'application/javascript'
        elif filepath.endswith('.json'):
            content_type = 'application/json'
        elif filepath.endswith('.png'):
            content_type = 'image/png'
        elif filepath.endswith('.jpg') or filepath.endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif filepath.endswith('.gif'):
            content_type = 'image/gif'
        elif filepath.endswith('.svg'):
            content_type = 'image/svg+xml'
        elif filepath.endswith('.ico'):
            content_type = 'image/x-icon'

        response = Response()
        response.status(200)
        response.set_header("Content-Type", content_type)
        response.body = content
        return response.to_bytes()

    except Exception as e:
        response = Response.server_error(f"Error serving file: {str(e)}".encode())
        return response.to_bytes()


def handle_client(client_socket, address):
    """Handle incoming client connection."""
    try:
        # Read initial chunk to get headers
        data = client_socket.recv(4096)

        if not data:
            return

        # Check if we need to read more data (for file uploads, etc.)
        header_end = data.find(b'\r\n\r\n')
        if header_end != -1:
            headers = data[:header_end].decode('utf-8', errors='ignore')

            # Check for Content-Length header
            for line in headers.split('\r\n'):
                if line.lower().startswith('content-length:'):
                    content_length = int(line.split(':')[1].strip())
                    body_received = len(data) - header_end - 4

                    # Read remaining body if needed
                    while body_received < content_length:
                        chunk = client_socket.recv(min(8192, content_length - body_received))
                        if not chunk:
                            break
                        data += chunk
                        body_received += len(chunk)
                    break

        request = Request(data)

        is_websocket = False
        for name, value in request.headers.items():
            if name.lower() == 'upgrade' and value.lower() == 'websocket':
                is_websocket = True
                break

        if is_websocket:
            handle_websocket_upgrade(request, client_socket)
            return

        response_bytes = main_router.route(request)

        if response_bytes is None:
            response_bytes = serve_static_file(request.path)

        client_socket.sendall(response_bytes)

    except Exception as e:
        try:
            response = Response.server_error(f"Server error: {str(e)}".encode())
            client_socket.sendall(response.to_bytes())
        except:
            pass

    finally:
        try:
            client_socket.close()
        except:
            pass


def run_server():
    """Start the TCP server."""
    register_routes()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(100)

    print(f"Server running on http://{HOST}:{PORT}")
    print(f"Press Ctrl+C to stop the server")

    try:
        while True:
            client_socket, address = server_socket.accept()

            # Handle each client in a separate thread
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, address),
                daemon=True
            )
            client_thread.start()

    except KeyboardInterrupt:
        print("\nShutting down server...")

    finally:
        server_socket.close()


if __name__ == '__main__':
    run_server()
