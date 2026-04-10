from scripts.config import (
    USER_NAME,
    READ_MODE,
    INTRO_TEMPLATE,
    MESSAGE_TEMPLATE,
    DISCREET_TEMPLATE,
)
from scripts.models import NotificationData


def format_speech(notification: NotificationData) -> str:
    sender = notification.sender.strip()
    message = notification.message.strip()

    if READ_MODE == "discreet":
        return DISCREET_TEMPLATE.format(
            user=USER_NAME,
            sender=sender
        )

    intro = INTRO_TEMPLATE.format(
        user=USER_NAME,
        sender=sender
    )

    content = MESSAGE_TEMPLATE.format(
        message=message
    )

    return f"{intro} {content}"