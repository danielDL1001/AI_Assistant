import logging
import threading
import time
from collections import deque

from scripts.config import RESUME_COLLECTION_SECONDS, SUSPEND_GAP_SECONDS
from scripts.formatter import format_rest_summary, format_speech

from scripts.models import NotificationData
from scripts.notification_listener import create_notification_listener
from scripts.tts_engine import TTSEngine



def setup_logger() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    return logging.getLogger("assistant")


class NotificationDeduplicator:
    def __init__(self, max_size: int = 100):
        self._recent = deque(maxlen=max_size)
        self._recent_set: set[tuple[str, str, str]] = set()

    def is_duplicate(self, notification: NotificationData) -> bool:
        key = notification.dedup_key()

        if key in self._recent_set:
            return True

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
    listener = create_notification_listener(logger=logger)
    rest_manager = RestModeManager(logger=logger)

    logger.info("Assistant started. Listening for notifications in background...")
    
    def _finalize_resume_window() -> None:
        history = rest_manager.finalize_resume_collection()
        tts.speak(format_rest_summary(history))

    def on_resume_from_suspend() -> None:
        rest_manager.start_resume_collection()
        threading.Timer(RESUME_COLLECTION_SECONDS, _finalize_resume_window).start()

    monitor = SuspendGapMonitor(on_resume=on_resume_from_suspend, logger=logger)
    monitor.start()



    def handle_notification(notification: NotificationData) -> None:
        if not notification.message.strip():
            logger.info("Skipped empty notification from %s", notification.app_name)
            return

        if deduplicator.is_duplicate(notification):
            logger.info(
                "Skipped duplicate notification | app=%s sender=%s",
                notification.app_name,
                notification.sender,
            )
            return
        
        if rest_manager.capture_or_none(notification):
            logger.info(
                "Captured for resume summary | app=%s sender=%s",
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

        tts.speak(format_speech(notification))

    listener.start(handle_notification)

if __name__ == "__main__":
    main()