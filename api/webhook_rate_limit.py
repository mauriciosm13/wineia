import json
from core.config import WEBHOOK_RATE_LIMIT_IP_MAX, WEBHOOK_RATE_LIMIT_IP_WINDOW_SECONDS, WEBHOOK_RATE_LIMIT_PHONE_MAX, WEBHOOK_RATE_LIMIT_PHONE_WINDOW_SECONDS
from core.rate_limit import SlidingWindowRateLimiter

_webhook_limiter = SlidingWindowRateLimiter()


def client_ip_from_environ(environ) -> str:
    forwarded = environ.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return environ.get("REMOTE_ADDR", "unknown")


def webhook_ip_rate_limit_allows(environ) -> bool:
    ip = client_ip_from_environ(environ)
    return _webhook_limiter.allow(
        f"webhook:ip:{ip}",
        WEBHOOK_RATE_LIMIT_IP_MAX,
        float(WEBHOOK_RATE_LIMIT_IP_WINDOW_SECONDS),
    )


def webhook_phone_rate_limit_allows(phone: str) -> bool:
    if not phone:
        return True
    normalized = phone.strip()
    if not normalized:
        return True
    return _webhook_limiter.allow(
        f"webhook:phone:{normalized}",
        WEBHOOK_RATE_LIMIT_PHONE_MAX,
        float(WEBHOOK_RATE_LIMIT_PHONE_WINDOW_SECONDS),
    )


def reject_rate_limited_webhook(start_response):
    start_response("429 Too Many Requests", [("Content-Type", "application/json")])
    return [json.dumps({"error": "rate_limit_exceeded"}).encode()]


def reset_webhook_rate_limiter_for_tests():
    _webhook_limiter.reset()
