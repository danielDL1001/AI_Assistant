from dataclasses import dataclass
from datetime import datetime


@dataclass
class NotificationData:
    app_name: str
    sender: str
    message: str
    timestamp: datetime
    is_group: bool = False