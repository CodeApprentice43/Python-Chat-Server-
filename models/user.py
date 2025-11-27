import bcrypt
from database.connection import get_db
from utils.security import escape_html


def create_user(username: str, password: str) -> bool:
    """Create a new user with hashed password.

    Args:
        username: User's username (will be HTML-escaped)
        password: Plain text password (will be hashed with bcrypt)

    Returns:
        bool: True if user created successfully, False if username already exists
    """
    db = get_db()
    users = db['users']

    username_escaped = escape_html(username)

    if users.find_one({'username': username_escaped}):
        return False

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)

    users.insert_one({
        'username': username_escaped,
        'salt': salt,
        'hash': password_hash
    })

    return True


def get_user(username: str) -> dict | None:
    """Get user by username.

    Args:
        username: Username to look up

    Returns:
        dict: User document with username, salt, hash, or None if not found
    """
    db = get_db()
    users = db['users']

    username_escaped = escape_html(username)
    user = users.find_one({'username': username_escaped}, {'_id': 0})

    return user


def user_exists(username: str) -> bool:
    """Check if username already exists.

    Args:
        username: Username to check

    Returns:
        bool: True if user exists, False otherwise
    """
    return get_user(username) is not None


def verify_password(username: str, password: str) -> bool:
    """Verify user password.

    Args:
        username: Username
        password: Plain text password to verify

    Returns:
        bool: True if password matches, False otherwise
    """
    user = get_user(username)

    if not user:
        return False

    stored_hash = user['hash']

    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
