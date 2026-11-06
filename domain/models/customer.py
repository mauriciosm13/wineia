from datetime import datetime


class CustomerStatus:
    active = "active"
    canceled = "canceled"


class PlanTier:
    entry = "ENTRY"
    superior = "SUPERIOR"
    all = (entry, superior)


DEFAULT_PLAN_TIER = PlanTier.entry


def normalize_customer_fields(data):
    """Apply defaults for tier fields (migration-on-read). Mutates and returns data."""
    if "plan_tier" not in data or data["plan_tier"] is None:
        data["plan_tier"] = DEFAULT_PLAN_TIER
    if "weekly_education_opt_in" not in data or data["weekly_education_opt_in"] is None:
        data["weekly_education_opt_in"] = False
    return data


def validate_plan_tier(plan_tier):
    if plan_tier not in PlanTier.all:
        raise ValueError("plan_tier must be ENTRY or SUPERIOR")


class Customer:

    def __init__(
        self,
        phone,
        name=None,
        status=None,
        plan=None,
        preferences=None,
        plan_tier=None,
        weekly_education_opt_in=None,
        recommendation_window_started_at=None,
        recommendation_send_count_7d=None,
    ):
        self.phone = phone
        self.name = name
        self.status = status
        self.plan = plan
        self.plan_tier = plan_tier if plan_tier is not None else DEFAULT_PLAN_TIER
        self.weekly_education_opt_in = (
            False if weekly_education_opt_in is None else bool(weekly_education_opt_in)
        )
        self.preferences = preferences if preferences is not None else []
        self.created_at = datetime.utcnow()
        self.last_message_at = None
        self.last_recommendation_at = None
        self.recommendation_window_started_at = recommendation_window_started_at
        self.recommendation_send_count_7d = (
            0 if recommendation_send_count_7d is None else int(recommendation_send_count_7d)
        )
        self.messages_sent_today = 0
        self.daily_reset = None

    def to_dict(self):
        return {
            "phone": self.phone,
            "name": self.name,
            "plan": self.plan,
            "plan_tier": self.plan_tier,
            "weekly_education_opt_in": self.weekly_education_opt_in,
            "status": self.status,
            "preferences": self.preferences,
            "created_at": self.created_at,
            "last_message_at": self.last_message_at,
            "last_recommendation_at": self.last_recommendation_at,
            "recommendation_window_started_at": self.recommendation_window_started_at,
            "recommendation_send_count_7d": self.recommendation_send_count_7d,
            "messages_sent_today": self.messages_sent_today,
            "daily_reset": self.daily_reset,
        }
