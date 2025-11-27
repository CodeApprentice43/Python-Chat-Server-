import uuid
from database.connection import get_db
from utils.security import escape_html


def create_message(username: str, message: str, media: dict = None) -> dict:
    """Create a new chat message.

    Args:
        username: Username of message sender
        message: Message content (will be HTML-escaped)
        media: Optional media attachment (url, type, filename)

    Returns:
        dict: Created message with id, username, message, and optional media
    """
    db = get_db()
    messages = db['chat']

    message_id = str(uuid.uuid4())
    message_escaped = escape_html(message) if message else ''
    username_escaped = escape_html(username)

    message_doc = {
        'id': message_id,
        'username': username_escaped,
        'message': message_escaped
    }

    if media:
        message_doc['media'] = media

    messages.insert_one(message_doc)

    result = {
        'id': message_id,
        'username': username_escaped,
        'message': message_escaped
    }

    if media:
        result['media'] = media

    return result


def get_all_messages() -> list[dict]:
    """Get all chat messages.

    Returns:
        list: All messages ordered by insertion (oldest first)
    """
    db = get_db()
    messages = db['chat']

    message_list = list(messages.find({}, {'_id': 0}))

    return message_list


def get_message_by_id(message_id: str) -> dict | None:
    """Get a specific message by ID.

    Args:
        message_id: Message ID to retrieve

    Returns:
        dict: Message document or None if not found
    """
    db = get_db()
    messages = db['chat']

    message = messages.find_one({'id': message_id}, {'_id': 0})

    return message


def delete_message(message_id: str) -> bool:
    """Delete a message by ID.

    Args:
        message_id: Message ID to delete

    Returns:
        bool: True if deleted, False if not found
    """
    db = get_db()
    messages = db['chat']

    result = messages.delete_one({'id': message_id})

    return result.deleted_count > 0


def is_message_owner(message_id: str, username: str) -> bool:
    """Check if user owns a message.

    Args:
        message_id: Message ID to check
        username: Username to verify ownership

    Returns:
        bool: True if user owns message, False otherwise
    """
    message = get_message_by_id(message_id)

    if not message:
        return False

    return message['username'] == escape_html(username)
