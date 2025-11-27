from core.router import Router
from core.response import Response
from services.auth_service import register_user, login_user, logout_user
from app.middleware.auth import require_auth

router = Router()


@router.post('/register')
def handle_register(request):
    """Handle user registration.

    Expects form data:
        - username: str
        - password: str

    Returns:
        - 201 Created if successful
        - 400 Bad Request if validation fails
    """
    try:
        form_data = request.form_data()
        username = form_data.get('username')
        password = form_data.get('password')

        if not username or not password:
            response = Response.bad_request(b"Username and password required")
            return response.to_bytes()

        success, message = register_user(username, password)

        if success:
            response = Response()
            response.status(201)
            response.text(message)
            return response.to_bytes()
        else:
            response = Response.bad_request(message.encode())
            return response.to_bytes()

    except Exception as e:
        response = Response.server_error(f"Registration failed: {str(e)}".encode())
        return response.to_bytes()


@router.post('/login')
def handle_login(request):
    """Handle user login.

    Expects form data:
        - username: str
        - password: str

    Returns:
        - 200 OK with cookies set if successful
        - 401 Unauthorized if credentials invalid
    """
    try:
        form_data = request.form_data()
        username = form_data.get('username')
        password = form_data.get('password')

        if not username or not password:
            response = Response.bad_request(b"Username and password required")
            return response.to_bytes()

        success, auth_token, xsrf_token = login_user(username, password)

        if success:
            response = Response()
            response.status(200)
            response.set_cookie('auth_token', auth_token, http_only=True, secure=True, max_age=3600)
            response.set_cookie('auth', 'true', max_age=3600)
            response.text("Login successful")
            return response.to_bytes()
        else:
            response = Response()
            response.status(401)
            response.text("Invalid credentials")
            return response.to_bytes()

    except Exception as e:
        response = Response.server_error(f"Login failed: {str(e)}".encode())
        return response.to_bytes()


@router.post('/logout')
@require_auth
def handle_logout(request):
    """Handle user logout.

    Requires authentication.

    Returns:
        - 302 redirect to home page
    """
    try:
        auth_token = request.cookies.get('auth_token')

        if auth_token:
            logout_user(auth_token)

        response = Response()
        response.delete_cookie('auth_token')
        response.delete_cookie('auth')
        response.redirect('/')
        return response.to_bytes()

    except Exception as e:
        response = Response.server_error(f"Logout failed: {str(e)}".encode())
        return response.to_bytes()
