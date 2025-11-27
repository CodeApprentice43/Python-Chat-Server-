from functools import wraps
from core.response import Response
from services.auth_service import get_authenticated_user


def require_auth(handler):
    """Middleware decorator to require authentication.

    Checks for auth_token cookie and validates it.
    If valid, adds request.user attribute with username.
    If invalid, returns 401 Unauthorized.

    Usage:
        @require_auth
        def protected_route(request):
            username = request.user  # Available after auth
            ...
    """
    @wraps(handler)
    def wrapper(request):
        auth_token = request.cookies.get('auth_token')

        if not auth_token:
            response = Response.bad_request(b"Authentication required")
            response.status(401, "Unauthorized")
            return response.to_bytes()

        username = get_authenticated_user(auth_token)

        if not username:
            response = Response.bad_request(b"Invalid or expired token")
            response.status(401, "Unauthorized")
            return response.to_bytes()

        request.user = username
        return handler(request)

    return wrapper


def optional_auth(handler):
    """Middleware decorator for optional authentication.

    If auth_token exists and is valid, sets request.user.
    If not, sets request.user = None and continues.

    Usage:
        @optional_auth
        def route(request):
            if request.user:
                # Authenticated user
            else:
                # Anonymous user
    """
    @wraps(handler)
    def wrapper(request):
        auth_token = request.cookies.get('auth_token')
        request.user = None

        if auth_token:
            username = get_authenticated_user(auth_token)
            if username:
                request.user = username

        return handler(request)

    return wrapper
