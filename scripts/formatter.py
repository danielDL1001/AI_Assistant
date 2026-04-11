from scripts.config import (
    DISCREET_TEMPLATE,
    INTRO_TEMPLATE,
    MESSAGE_TEMPLATE,
    READ_MODE,
    REST_EMPTY_TEMPLATE,
    REST_SUMMARY_TEMPLATE,
    USER_NAME,
)
from scripts.models import NotificationData

def format_speech(notification: NotificationData) -> str:
    sender = notification.sender.strip() or notification.app_name.strip() or "origem desconhecida"
    message = notification.message.strip()

    if READ_MODE == "discreet":
        return DISCREET_TEMPLATE.format(user=USER_NAME, sender=sender)

    intro = INTRO_TEMPLATE.format(user=USER_NAME, sender=sender)
    return f"{intro} {MESSAGE_TEMPLATE.format(message=message)}"

def format_rest_summary(notifications: list[NotificationData]) -> str:
    if not notifications:
        return REST_EMPTY_TEMPLATE.format(user=USER_NAME)

    summary = REST_SUMMARY_TEMPLATE.format(user=USER_NAME, num_notificacao=len(notifications))
    details = " ".join(format_speech(notification) for notification in notifications)
    return f"{summary} {details}"