from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NotificationData:
    """Represents one desktop notification captured from DBus."""

    app_name: str
    sender: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)

    def dedup_key(self) -> tuple[str, str, str]:
        """Small key used by the main loop to avoid repeated notifications."""
        return (
            self.app_name.strip().lower(),
            self.sender.strip().lower(),
            self.message.strip().lower(),
        )