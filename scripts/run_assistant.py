import logging
from collections import deque

from scripts.formatter import format_speech
from scripts.models import NotificationData
from scripts.notification_listener import LinuxNotificationListener
from scripts.tts_engine import TTSEngine


def setup_logger() -> logging.Logger:
    """Creates a basic console logger for the assistant."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    return logging.getLogger("assistant")


class NotificationDeduplicator:
    """
    Basic deduplicator based on recent notification keys.

    Keeps only the most recent keys in memory.
    """

    def __init__(self, max_size: int = 100):
        self._recent = deque(maxlen=max_size)
        self._recent_set: set[tuple[str, str, str]] = set()

    def is_duplicate(self, notification: NotificationData) -> bool:
        key = notification.dedup_key()

        if key in self._recent_set:
            return True

        # If deque is full, remove old key from set before appending new one.
        if len(self._recent) == self._recent.maxlen:
            oldest = self._recent[0]
            self._recent_set.discard(oldest)

        self._recent.append(key)
        self._recent_set.add(key)
        return False


def main() -> None:
    logger = setup_logger()
    tts = TTSEngine(logger=logger)
    deduplicator = NotificationDeduplicator()
    listener = LinuxNotificationListener(logger=logger)

    logger.info("Assistant started. Listening for all Linux notifications...")

    def handle_notification(notification: NotificationData) -> None:
        # Extra guard: ignore empty messages.
        if not notification.message.strip():
            logger.info("Skipped empty notification from %s", notification.app_name)
            return

        # Basic duplicate prevention.
        if deduplicator.is_duplicate(notification):
            logger.info(
                "Skipped duplicate notification | app=%s sender=%s",
                notification.app_name,
                notification.sender,
            )
            return

        logger.info(
            "New notification | app=%s sender=%s message=%s",
            notification.app_name,
            notification.sender,
            notification.message,
        )

        text = format_speech(notification)
        tts.speak(text)

    listener.start(handle_notification)


if __name__ == "__main__":
    main()