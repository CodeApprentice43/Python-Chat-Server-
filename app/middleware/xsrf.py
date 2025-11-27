from functools import wraps
from core.response import Response
from models.session import verify_xsrf_token


def require_xsrf(handler):
    """Middleware decorator to require XSRF token validation.

    Validates XSRF token from request body against stored token for user.
    Only enforces if user is authenticated (request.user exists).

    Usage:
        @require_auth
        @require_xsrf
        def state_changing_route(request):
            # XSRF token validated
            ...
    """
    @wraps(handler)
    def wrapper(request):
        username = getattr(request, 'user', None)

        if not username:
            return handler(request)

        form_data = request.form_data()
        xsrf_token = form_data.get('xsrf_token')

        if not xsrf_token:
            response = Response.bad_request(b"XSRF token required")
            response.status(403, "Forbidden")
            return response.to_bytes()

        if not verify_xsrf_token(username, xsrf_token):
            response = Response.bad_request(b"Invalid XSRF token")
            response.status(403, "Forbidden")
            return response.to_bytes()

        return handler(request)

    return wrapper
