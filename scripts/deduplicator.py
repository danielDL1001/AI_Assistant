import time
from scripts.config import DEDUP_TTL_SECONDS


class Deduplicator:
    def __init__(self):
        self.cache = {}

    def _cleanup(self):
        now = time.time()
        expired_keys = [
            key for key, ts in self.cache.items()
            if now - ts > DEDUP_TTL_SECONDS
        ]
        for key in expired_keys:
            del self.cache[key]

    def is_duplicate(self, sender: str, message: str) -> bool:
        self._cleanup()
        key = f"{sender.strip().lower()}::{message.strip().lower()}"
        if key in self.cache:
            return True

        self.cache[key] = time.time()
        return False