import json
from core.config import WAITLIST_RATE_LIMIT_IP_MAX, WAITLIST_RATE_LIMIT_IP_WINDOW_SECONDS
from core.rate_limit import SlidingWindowRateLimiter
from api.webhook_rate_limit import client_ip_from_environ

_waitlist_limiter = SlidingWindowRateLimiter()


def waitlist_ip_rate_limit_allows(environ) -> bool:
    ip = client_ip_from_environ(environ)
    return _waitlist_limiter.allow(
        f"waitlist:ip:{ip}",
        WAITLIST_RATE_LIMIT_IP_MAX,
        float(WAITLIST_RATE_LIMIT_IP_WINDOW_SECONDS),
    )


def reject_rate_limited_waitlist(start_response):
    start_response("429 Too Many Requests", [("Content-Type", "application/json")])
    return [json.dumps({"error": "rate_limit_exceeded"}).encode()]


def reset_waitlist_rate_limiter_for_tests():
    _waitlist_limiter.reset()
