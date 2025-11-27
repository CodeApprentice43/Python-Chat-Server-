from models.message import (
    create_message as create_message_model,
    get_all_messages as get_all_messages_model,
    delete_message as delete_message_model,
    is_message_owner
)


def get_messages() -> list[dict]:
   
    return get_all_messages_model()


def post_message(username: str, message: str, media: dict = None) -> tuple[bool, dict | str]:

    if not message and not media:
        return (False, "Message cannot be empty")

    if message and len(message) > 5000:
        return (False, "Message too long (max 5000 characters)")

    message_data = create_message_model(username, message or '', media)

    return (True, message_data)


def delete_message(message_id: str, username: str) -> tuple[bool, str]:
   
    if not is_message_owner(message_id, username):
        return (False, "Forbidden: You can only delete your own messages")

    success = delete_message_model(message_id)

    if success:
        return (True, "Message deleted")
    else:
        return (False, "Message not found")
