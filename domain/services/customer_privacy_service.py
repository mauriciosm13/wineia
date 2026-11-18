from domain.models.customer import CustomerStatus, normalize_customer_fields

REDACTED = "REDACTED"

_EXPORT_CUSTOMER_FIELDS = (
    "phone",
    "name",
    "status",
    "plan",
    "plan_tier",
    "weekly_education_opt_in",
    "preferences",
    "privacy_terms_version",
    "privacy_terms_accepted_at",
    "created_at",
    "last_message_at",
    "last_recommendation_at",
    "recommendation_window_started_at",
    "recommendation_send_count_7d",
    "messages_sent_today",
    "daily_reset",
)

_EXPORT_PRE_SALE_FIELDS = (
    "name",
    "email",
    "whatsapp",
    "preferences",
    "privacy_terms_version",
    "privacy_terms_accepted_at",
    "created_at",
)


def _as_dict(record):
    if isinstance(record, dict):
        payload = dict(record)
    elif hasattr(record, "to_dict"):
        payload = record.to_dict()
    else:
        payload = dict(record)
    return normalize_customer_fields(payload)


def _pre_sale_as_dict(record):
    if record is None:
        return None
    if isinstance(record, dict):
        return dict(record)
    if hasattr(record, "to_dict"):
        return record.to_dict()
    return dict(record)


def _pick(source, fields):
    return {field: source.get(field) for field in fields}


class CustomerPrivacyService:

    def __init__(self, customer_repository, pre_sale_repository):
        self.customer_repository = customer_repository
        self.pre_sale_repository = pre_sale_repository

    def export_customer(self, phone):
        existing = self.customer_repository.get_by_phone(phone)
        if existing is None:
            return None

        customer = _as_dict(existing)
        payload = _pick(customer, _EXPORT_CUSTOMER_FIELDS)

        lead = _pre_sale_as_dict(self.pre_sale_repository.get_by_whatsapp(phone))
        if lead is None:
            payload["pre_sale"] = None
        else:
            payload["pre_sale"] = _pick(lead, _EXPORT_PRE_SALE_FIELDS)

        return payload

    def erase_customer(self, phone):
        existing = self.customer_repository.get_by_phone(phone)
        if existing is None:
            return None

        customer = _as_dict(existing)
        customer["name"] = REDACTED
        customer["preferences"] = []
        customer["status"] = CustomerStatus.canceled
        customer["weekly_education_opt_in"] = False
        customer["privacy_terms_version"] = None
        customer["privacy_terms_accepted_at"] = None

        self.customer_repository.update(customer)

        pre_sale_deleted = False
        lead = _pre_sale_as_dict(self.pre_sale_repository.get_by_whatsapp(phone))
        if lead is not None and lead.get("email"):
            self.pre_sale_repository.delete(lead["email"])
            pre_sale_deleted = True

        result = dict(customer)
        result["erased"] = True
        result["pre_sale_deleted"] = pre_sale_deleted
        return result
