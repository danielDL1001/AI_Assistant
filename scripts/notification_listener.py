import logging
import re
import subprocess
from collections.abc import Callable

from scripts.models import NotificationData


class LinuxNotificationListener:
    """
    Captures desktop notifications from DBus using `dbus-monitor`.

    It parses the Notify call and extracts app name, summary (sender), and body (message).
    """

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger(__name__)
        self.process: subprocess.Popen[str] | None = None

    def start(self, callback: Callable[[NotificationData], None]) -> None:
        """Starts dbus-monitor and calls `callback` for each parsed notification."""
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

            # Notify call starts here.
            if "member=Notify" in line:
                inside_notify = True
                buffer = []
                continue

            if not inside_notify:
                continue

            # DBus string values are written as: string "value"
            if line.startswith("string"):
                matches = re.findall(r'"(.*?)"', line)
                if matches:
                    buffer.append(matches[0])

            # End of message body (basic approach, keeps original behavior simple)
            if "int32" in line:
                inside_notify = False
                notification = self._build_notification(buffer)
                buffer = []

                if notification:
                    callback(notification)

    def _build_notification(self, values: list[str]) -> NotificationData | None:
        """
        Expected Notify signature includes:
        app_name, ..., summary, body, ...
        We keep a robust fallback for different desktop implementations.
        """
        if len(values) < 5:
            self.logger.debug("Skipping malformed notification block: %s", values)
            return None

        app_name = values[0].strip()
        sender = values[3].strip()
        message = values[4].strip()

        # Ignore empty messages, as requested.
        if not message:
            self.logger.debug("Ignoring empty notification from app=%s sender=%s", app_name, sender)
            return None

        notification = NotificationData(
            app_name=app_name,
            sender=sender,
            message=message,
        )

        self.logger.debug(
            "Parsed notification | app=%s sender=%s message=%s",
            notification.app_name,
            notification.sender,
            notification.message,
        )
        return notification