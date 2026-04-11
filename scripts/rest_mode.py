import logging
import threading
import time
from typing import Callable

from scripts.models import NotificationData


class RestModeManager:
    """Gerencia a janela de coleta de notificações após retorno de suspensão."""

    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._lock = threading.Lock()
        self._collecting_resume_notifications = False
        self._resume_history: list[NotificationData] = []

    def start_resume_collection(self) -> None:
        with self._lock:
            self._collecting_resume_notifications = True
            self._resume_history = []
            self._logger.info("Resume collection started.")

    def capture_or_none(self, notification: NotificationData) -> bool:
        with self._lock:
            if not self._collecting_resume_notifications:
                return False

            self._resume_history.append(notification)
            return True

    def finalize_resume_collection(self) -> list[NotificationData]:
        with self._lock:
            history = list(self._resume_history)
            self._collecting_resume_notifications = False
            self._resume_history = []
            self._logger.info("Resume collection finished with %d notifications.", len(history))
            return history


class SuspendGapMonitor:
    """
    Detecta possível retorno de suspensão observando salto de tempo entre iterações.
    """

    def __init__(
        self,
        on_resume: Callable[[], None],
        logger: logging.Logger,
        threshold_seconds: float = 45.0,
        poll_interval_seconds: float = 1.0,
    ) -> None:
        self._on_resume = on_resume
        self._logger = logger
        self._threshold_seconds = threshold_seconds
        self._poll_interval_seconds = poll_interval_seconds
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="suspend-gap-monitor")
        self._thread.start()
        self._logger.info("Suspend gap monitor started.")

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self) -> None:
        previous = time.monotonic()
        while not self._stop_event.is_set():
            time.sleep(self._poll_interval_seconds)
            now = time.monotonic()
            elapsed = now - previous
            previous = now

            if elapsed >= self._threshold_seconds:
                self._logger.info(
                    "Detected resume from suspend (gap %.2fs >= %.2fs).",
                    elapsed,
                    self._threshold_seconds,
                )
                self._on_resume()
