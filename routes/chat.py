from core.router import Router
from core.response import Response
from services.chat_service import get_messages, post_message, delete_message
from app.middleware.auth import require_auth, optional_auth
from app.middleware.xsrf import require_xsrf

router = Router()


@router.get('/chat-messages')
def handle_get_messages(request):
    """Get all chat messages.

    No authentication required.

    Returns:
        200 OK with JSON array of messages
    """
    try:
        messages = get_messages()

        response = Response()
        response.json(messages)
        return response.to_bytes()

    except Exception as e:
        response = Response.server_error(f"Failed to retrieve messages: {str(e)}".encode())
        return response.to_bytes()


@router.post('/chat-messages')
@optional_auth
def handle_post_message(request):
    """Post a new chat message.

    Optional authentication.
    If authenticated, requires XSRF token.

    Expects form data or JSON:
        - message: str

    Returns:
        201 Created with message data
        400 Bad Request if validation fails
    """
    try:
        username = getattr(request, 'user', None)

        if username:
            form_data = request.form_data()
            xsrf_token = form_data.get('xsrf_token')

            if not xsrf_token:
                response = Response.bad_request(b"XSRF token required for authenticated users")
                response.status(403)
                return response.to_bytes()

            from models.session import verify_xsrf_token
            if not verify_xsrf_token(username, xsrf_token):
                response = Response.bad_request(b"Invalid XSRF token")
                response.status(403)
                return response.to_bytes()

            message_text = form_data.get('message')
        else:
            username = "guest"
            try:
                json_data = request.json()
                message_text = json_data.get('message')
            except:
                form_data = request.form_data()
                message_text = form_data.get('message')

        if not message_text:
            response = Response.bad_request(b"Message is required")
            return response.to_bytes()

        success, result = post_message(username, message_text)

        if success:
            response = Response()
            response.status(201)
            response.json(result)
            return response.to_bytes()
        else:
            response = Response.bad_request(result.encode())
            return response.to_bytes()

    except Exception as e:
        response = Response.server_error(f"Failed to post message: {str(e)}".encode())
        return response.to_bytes()


@router.delete('/chat-messages/{id}')
@require_auth
def handle_delete_message(request):
    """Delete a chat message.

    Requires authentication.
    Users can only delete their own messages.

    Returns:
        204 No Content if successful
        403 Forbidden if not owner
        404 Not Found if message doesn't exist
    """
    try:
        message_id = request.path_params.get('id')
        username = request.user

        if not message_id:
            response = Response.bad_request(b"Message ID required")
            return response.to_bytes()

        success, message = delete_message(message_id, username)

        if success:
            response = Response()
            response.status(204)
            return response.to_bytes()
        else:
            if "Forbidden" in message:
                response = Response()
                response.status(403)
                response.text(message)
                return response.to_bytes()
            else:
                response = Response.not_found(message.encode())
                return response.to_bytes()

    except Exception as e:
        response = Response.server_error(f"Failed to delete message: {str(e)}".encode())
        return response.to_bytes()
