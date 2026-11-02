import time
from collections import defaultdict, deque


class SlidingWindowRateLimiter:
    """In-process sliding window counter (not shared across gunicorn workers)."""

    def __init__(self):
        self._events = defaultdict(deque)

    def allow(self, key: str, max_requests: int, window_seconds: float) -> bool:
        if max_requests <= 0:
            return True
        if window_seconds <= 0:
            return True
        now = time.monotonic()
        window_start = now - window_seconds
        events = self._events[key]
        while events and events[0] <= window_start:
            events.popleft()
        if len(events) >= max_requests:
            return False
        events.append(now)
        return True

    def reset(self):
        self._events.clear()
