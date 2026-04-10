import subprocess
import re
from datetime import datetime

from scripts.models import NotificationData


class LinuxNotificationListener:
    def __init__(self):
        self.process = None

    def start(self, callback):
        self.process = subprocess.Popen(
            ["dbus-monitor", "interface='org.freedesktop.Notifications'"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        buffer = []
        inside_notify = False

        for line in self.process.stdout:
            line = line.strip()

            if "member=Notify" in line:
                inside_notify = True
                buffer = []
                continue

            if inside_notify:
                if "string" in line:
                    match = re.findall(r'"(.*?)"', line)
                    if match:
                        buffer.append(match[0])

                # Quando terminar o bloco
                if "int32" in line:
                    inside_notify = False

                    if len(buffer) >= 5:
                        app_name = buffer[0]
                        sender = buffer[3]
                        message = buffer[4]

                        notification = NotificationData(
                            app_name=app_name,
                            sender=sender,
                            message=message,
                            timestamp=datetime.now(),
                            is_group=":" in sender
                        )

                        print("PARSED:", notification)  # debug

                        callback(notification)

                    buffer = []