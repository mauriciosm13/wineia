from datetime import datetime, timezone


class ClaudeBudgetExceededError(Exception):
    """Raised when the global Claude daily call budget is exhausted."""


def utc_day_key(now=None):
    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    else:
        now = now.astimezone(timezone.utc)
    return now.strftime("%Y-%m-%d")


def ensure_within_budget(repository, budget, now=None):
    if budget is None or budget <= 0:
        return
    day_key = utc_day_key(now)
    count = repository.get_call_count(day_key)
    if count >= budget:
        raise ClaudeBudgetExceededError(
            f"claude daily call budget exceeded: count={count} budget={budget} day={day_key}"
        )


def record_successful_call(repository, now=None):
    day_key = utc_day_key(now)
    return repository.increment_call_count(day_key)
