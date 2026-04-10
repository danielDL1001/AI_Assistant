from scripts.logger_setup import setup_logger
from scripts.notification_listener import LinuxNotificationListener
from scripts.filters import should_read_notification
from scripts.formatter import format_speech
from scripts.tts_engine import TTSEngine
from scripts.deduplicator import Deduplicator
from scripts.config import ENABLE_DEDUPLICATION


def main():
    logger = setup_logger()
    tts = TTSEngine()
    deduplicator = Deduplicator()

    listener = LinuxNotificationListener()

    logger.info("Assistente iniciada (modo Linux real).")

    def handle_notification(notification):
        print("CHEGOU:", notification)

        tts.speak("teste direto")
        logger.info(
            f"Nova notificação | "
            f"{notification.app_name} | "
            f"{notification.sender} | "
            f"{notification.message}"
        )

#        if not should_read_notification(notification):
#            return

#        if ENABLE_DEDUPLICATION:
#            if deduplicator.is_duplicate(
#                notification.sender,
#                notification.message
#            ):
#                return

        speech = format_speech(notification)
        print("FALANDO:", speech)
        tts.speak(speech)

    listener.start(handle_notification)


if __name__ == "__main__":
    main()