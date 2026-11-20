import os

DEFAULT_ON_DEMAND_DAILY_LIMIT_ENTRY = 2
DEFAULT_ON_DEMAND_DAILY_LIMIT_SUPERIOR = 10


def _non_negative_int_env(name, default):
    raw = os.getenv(name)
    if raw is None or str(raw).strip() == "":
        return default
    try:
        value = int(str(raw).strip())
    except ValueError:
        return default
    if value < 0:
        return default
    return value


PROJECT_ID = os.getenv("PROJECT_ID")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")
TWILIO_TIMEOUT = int(os.getenv("TWILIO_TIMEOUT", "30"))
JOB_INTERNAL_SECRET = os.getenv("JOB_INTERNAL_SECRET")
WEBHOOK_RATE_LIMIT_IP_MAX = int(os.getenv("WEBHOOK_RATE_LIMIT_IP_MAX", "120"))
WEBHOOK_RATE_LIMIT_IP_WINDOW_SECONDS = int(os.getenv("WEBHOOK_RATE_LIMIT_IP_WINDOW_SECONDS", "60"))
WEBHOOK_RATE_LIMIT_PHONE_MAX = int(os.getenv("WEBHOOK_RATE_LIMIT_PHONE_MAX", "30"))
WEBHOOK_RATE_LIMIT_PHONE_WINDOW_SECONDS = int(os.getenv("WEBHOOK_RATE_LIMIT_PHONE_WINDOW_SECONDS", "60"))
WAITLIST_RATE_LIMIT_IP_MAX = int(os.getenv("WAITLIST_RATE_LIMIT_IP_MAX", "30"))
WAITLIST_RATE_LIMIT_IP_WINDOW_SECONDS = int(os.getenv("WAITLIST_RATE_LIMIT_IP_WINDOW_SECONDS", "60"))
DEFAULT_WAITLIST_MIN_AGE = 18
WAITLIST_MIN_AGE = _non_negative_int_env("WAITLIST_MIN_AGE", DEFAULT_WAITLIST_MIN_AGE)
ON_DEMAND_DAILY_LIMIT_ENTRY = _non_negative_int_env(
    "ON_DEMAND_DAILY_LIMIT_ENTRY", DEFAULT_ON_DEMAND_DAILY_LIMIT_ENTRY
)
ON_DEMAND_DAILY_LIMIT_SUPERIOR = _non_negative_int_env(
    "ON_DEMAND_DAILY_LIMIT_SUPERIOR", DEFAULT_ON_DEMAND_DAILY_LIMIT_SUPERIOR
)
def _resolve_ia_daily_call_budget():
    """Prefer IA_DAILY_CALL_BUDGET; fall back to legacy CLAUDE_DAILY_CALL_BUDGET."""
    ia_raw = os.getenv("IA_DAILY_CALL_BUDGET")
    if ia_raw is not None and str(ia_raw).strip() != "":
        return _non_negative_int_env("IA_DAILY_CALL_BUDGET", 0)
    return _non_negative_int_env("CLAUDE_DAILY_CALL_BUDGET", 0)


IA_DAILY_CALL_BUDGET = _resolve_ia_daily_call_budget()
CLAUDE_DAILY_CALL_BUDGET = IA_DAILY_CALL_BUDGET

DEFAULT_PRIVACY_POLICY_URL = "https://example.com/privacy"
DEFAULT_TERMS_OF_SERVICE_URL = "https://example.com/terms"


def _url_env(name, default):
    raw = os.getenv(name)
    if raw is None:
        return default
    value = str(raw).strip()
    if not value:
        return default
    return value


PRIVACY_POLICY_URL = _url_env("PRIVACY_POLICY_URL", DEFAULT_PRIVACY_POLICY_URL)
TERMS_OF_SERVICE_URL = _url_env("TERMS_OF_SERVICE_URL", DEFAULT_TERMS_OF_SERVICE_URL)
