from models.user import create_user, verify_password, user_exists
from models.session import create_session, delete_session, get_username_from_token, create_xsrf_token
from utils.validation import validate_password


def register_user(username: str, password: str) -> tuple[bool, str]:
 
    if not username or not password:
        return (False, "Username and password are required")

    if user_exists(username):
        return (False, "Username already exists")

    if not validate_password(password):
        return (False, "Password must be at least 8 characters with uppercase, lowercase, number, and special character (!@#$%^&()-_=)")

    success = create_user(username, password)

    if success:
        return (True, "User created successfully")
    else:
        return (False, "Failed to create user")


def login_user(username: str, password: str) -> tuple[bool, str | None, str | None]:
   
    if not username or not password:
        return (False, None, None)

    if not verify_password(username, password):
        return (False, None, None)

    auth_token = create_session(username)
    xsrf_token = create_xsrf_token(username)

    return (True, auth_token, xsrf_token)


def logout_user(token: str) -> bool:
 
    return delete_session(token)


def get_authenticated_user(token: str) -> str | None:
   
    if not token:
        return None

    return get_username_from_token(token)
