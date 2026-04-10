from scripts.config import BLOCKLIST, ALLOWLIST, IGNORE_GROUPS
from scripts.models import NotificationData


def should_read_notification(notification: NotificationData) -> bool:
    sender = notification.sender.strip()

    if IGNORE_GROUPS and notification.is_group:
        return False

    if sender in BLOCKLIST:
        return False

    if ALLOWLIST and sender not in ALLOWLIST:
        return False

    if not notification.message.strip():
        return False

    return True