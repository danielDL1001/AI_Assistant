from scripts.models import NotificationData


def format_speech(notification: NotificationData) -> str:
    """
    Builds a natural sentence to read aloud.

    Example:
    "Notification from WhatsApp. John says: Hello there"
    """
    app_name = notification.app_name.strip() or "Unknown app"
    sender = notification.sender.strip() or "Unknown sender"
    message = notification.message.strip()

    return f"Notification from {app_name}. {sender} says: {message}"