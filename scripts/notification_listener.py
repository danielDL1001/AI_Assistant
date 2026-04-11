import logging
import platform
import re
import subprocess
from abc import ABC, abstractmethod
from collections.abc import Callable
from scripts.models import NotificationData

class NotificationListener(ABC):
    @abstractmethod
    def start(self, callback: Callable[[NotificationData], None]) -> None:
        raise NotImplementedError

class LinuxNotificationListener(NotificationListener):
    """Captures desktop notifications from DBus using `dbus-monitor`."""

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger(__name__)
        self.process: subprocess.Popen[str] | None = None

    def start(self, callback: Callable[[NotificationData], None]) -> None:
        self.logger.info("Starting DBus notification listener...")

        self.process = subprocess.Popen(
            ["dbus-monitor", "interface='org.freedesktop.Notifications'"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        if not self.process.stdout:
            self.logger.error("Unable to read dbus-monitor stdout.")
            return

        buffer: list[str] = []
        inside_notify = False

        for raw_line in self.process.stdout:
            line = raw_line.strip()

            if "member=Notify" in line:
                inside_notify = True
                buffer = []
                continue

            if not inside_notify:
                continue

            if line.startswith("string"):
                matches = re.findall(r'"(.*?)"', line)
                if matches:
                    buffer.append(matches[0])

            if "int32" in line:
                inside_notify = False
                notification = self._build_notification(buffer)
                buffer = []

                if notification:
                    callback(notification)

    def _build_notification(self, values: list[str]) -> NotificationData | None:
        if len(values) < 5:
            self.logger.debug("Skipping malformed notification block: %s", values)
            return None

        app_name = values[0].strip()
        sender = values[3].strip()
        message = values[4].strip()

        if not message:
            self.logger.debug("Ignoring empty notification from app=%s sender=%s", app_name, sender)
            return None

        return NotificationData(app_name=app_name, sender=sender, message=message)

class WindowsNotificationListener(NotificationListener):
    """Placeholder listener for Windows builds.

    Windows toast capture requires a native event bridge; until then, we keep the
    assistant alive and emit a clear log message.
    """

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger(__name__)

    def start(self, callback: Callable[[NotificationData], None]) -> None:
        _ = callback
        self.logger.warning(
            "Windows notification capture is not available yet in this build. "
            "TTS background pipeline is active, but no notifications are being consumed."
        )

def create_notification_listener(logger: logging.Logger | None = None) -> NotificationListener:
    system = platform.system().lower()
    if "linux" in system:
        return LinuxNotificationListener(logger=logger)
    if "windows" in system:
        return WindowsNotificationListener(logger=logger)
    raise RuntimeError(f"Unsupported platform for notification listener: {platform.system()}")
