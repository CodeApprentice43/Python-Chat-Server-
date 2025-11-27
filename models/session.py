import hashlib
import uuid
from database.connection import get_db


def create_session(username: str) -> str:
    """Create authentication session for user.

    Args:
        username: Username to create session for

    Returns:
        str: Authentication token (UUID) - unhashed version for cookie
    """
    db = get_db()
    tokens = db['tokens']

    auth_token = str(uuid.uuid4())
    token_hash = hashlib.sha256(auth_token.encode()).hexdigest()

    tokens.insert_one({
        'username': username,
        'hash': token_hash,
        'access_token': auth_token
    })

    return auth_token


def get_session(token: str) -> dict | None:
    """Get session by authentication token.

    Args:
        token: Authentication token (unhashed)

    Returns:
        dict: Session document with username, hash, access_token, or None if not found
    """
    db = get_db()
    tokens = db['tokens']

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    session = tokens.find_one({'hash': token_hash}, {'_id': 0})

    return session


def delete_session(token: str) -> bool:
    """Delete session by authentication token.

    Args:
        token: Authentication token to delete

    Returns:
        bool: True if session was deleted, False if not found
    """
    db = get_db()
    tokens = db['tokens']

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    result = tokens.delete_one({'hash': token_hash})

    return result.deleted_count > 0


def get_username_from_token(token: str) -> str | None:
    """Get username associated with token.

    Args:
        token: Authentication token

    Returns:
        str: Username if session exists, None otherwise
    """
    session = get_session(token)
    return session['username'] if session else None


def create_xsrf_token(username: str) -> str:
    """Create XSRF token for user.

    Args:
        username: Username to create token for

    Returns:
        str: XSRF token (UUID)
    """
    db = get_db()
    xsrf_tokens = db['xsrf_tokens']

    xsrf_token = str(uuid.uuid4())

    xsrf_tokens.update_one(
        {'username': username},
        {'$set': {'xsrf_token': xsrf_token}},
        upsert=True
    )

    return xsrf_token


def get_xsrf_token(username: str) -> str | None:
    """Get XSRF token for user.

    Args:
        username: Username to get token for

    Returns:
        str: XSRF token if exists, None otherwise
    """
    db = get_db()
    xsrf_tokens = db['xsrf_tokens']

    result = xsrf_tokens.find_one({'username': username}, {'_id': 0})
    return result['xsrf_token'] if result else None


def verify_xsrf_token(username: str, token: str) -> bool:
    """Verify XSRF token for user.

    Args:
        username: Username
        token: XSRF token to verify

    Returns:
        bool: True if token matches, False otherwise
    """
    stored_token = get_xsrf_token(username)
    return stored_token == token if stored_token else False


def get_authenticated_user(token: str) -> str | None:
    """Get authenticated username from token (alias for get_username_from_token).

    Args:
        token: Authentication token

    Returns:
        str: Username if authenticated, None otherwise
    """
    return get_username_from_token(token)
