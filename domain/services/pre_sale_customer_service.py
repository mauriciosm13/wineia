from core import config
from domain.models.customer import Customer
from domain.models.pre_sale_customer import PreSaleCustomer
from domain.privacy_terms import build_privacy_terms_notice, privacy_terms_consent_metadata


def _as_dict(record):
    if isinstance(record, dict):
        return dict(record)
    if hasattr(record, "to_dict"):
        return record.to_dict()
    return dict(record)


def _normalize_preferences(preferences):
    if not preferences:
        return []
    if isinstance(preferences, list):
        return [p for p in preferences if isinstance(p, str) and p.strip()]
    if isinstance(preferences, dict):
        return [f"{key}: {value}" for key, value in preferences.items()]
    return []


def _merge_preferences(existing_preferences, lead_preferences):
    merged = _normalize_preferences(existing_preferences)
    for preference in _normalize_preferences(lead_preferences):
        if preference not in merged:
            merged.append(preference)
    return merged


def _privacy_terms_notice():
    return build_privacy_terms_notice(config.PRIVACY_POLICY_URL, config.TERMS_OF_SERVICE_URL)


def _has_consent(record):
    return bool(record.get("privacy_terms_version") and record.get("privacy_terms_accepted_at"))


def _consent_from_lead_or_fresh(lead):
    if _has_consent(lead):
        return {
            "privacy_terms_version": lead.get("privacy_terms_version"),
            "privacy_terms_accepted_at": lead.get("privacy_terms_accepted_at"),
        }
    return privacy_terms_consent_metadata()


def _with_notice(payload):
    result = dict(payload)
    result["privacy_terms_notice"] = _privacy_terms_notice()
    return result


class PreSaleCustomerService:

    def __init__(self, repository):
        self.repository = repository

    def create_customer(self, name, email, whatsapp, preferences):
        existing = self.repository.get_by_email(email)

        if existing:
            return dict(existing)

        consent = privacy_terms_consent_metadata()
        customer = PreSaleCustomer(
            name,
            email,
            whatsapp,
            preferences,
            privacy_terms_version=consent["privacy_terms_version"],
            privacy_terms_accepted_at=consent["privacy_terms_accepted_at"],
        )

        self.repository.save(customer)

        return _with_notice(customer.to_dict())

    def activate(self, email, customer_repository, plan="free"):
        lead = self.repository.get_by_email(email)
        if not lead:
            return None

        lead = _as_dict(lead)
        existing = customer_repository.get_by_phone(lead["whatsapp"])
        lead_preferences = lead.get("preferences") or []
        consent = _consent_from_lead_or_fresh(lead)

        if existing:
            existing_dict = _as_dict(existing)
            merged_preferences = _merge_preferences(
                existing_dict.get("preferences"), lead_preferences
            )
            changed = False
            if merged_preferences != _normalize_preferences(existing_dict.get("preferences")):
                existing_dict["preferences"] = merged_preferences
                changed = True
            if not _has_consent(existing_dict) and _has_consent(lead):
                existing_dict["privacy_terms_version"] = lead.get("privacy_terms_version")
                existing_dict["privacy_terms_accepted_at"] = lead.get("privacy_terms_accepted_at")
                changed = True
            if changed:
                customer_repository.update(existing_dict)
            return _with_notice(existing_dict)

        customer = Customer(
            phone=lead["whatsapp"],
            name=lead.get("name"),
            status="active",
            plan=plan,
            preferences=_normalize_preferences(lead_preferences),
            privacy_terms_version=consent["privacy_terms_version"],
            privacy_terms_accepted_at=consent["privacy_terms_accepted_at"],
        )
        customer_repository.save(customer)
        return _with_notice(customer.to_dict())
