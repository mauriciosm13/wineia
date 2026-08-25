from domain.models.customer import Customer
from domain.models.pre_sale_customer import PreSaleCustomer


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


class PreSaleCustomerService:

    def __init__(self, repository):
        self.repository = repository

    def create_customer(self, name, email, whatsapp, preferences):
        existing = self.repository.get_by_email(email)

        if existing:
            return dict(existing)

        customer = PreSaleCustomer(name, email, whatsapp, preferences)

        self.repository.save(customer)

        return customer.to_dict()

    def activate(self, email, customer_repository, plan="free"):
        lead = self.repository.get_by_email(email)
        if not lead:
            return None

        lead = _as_dict(lead)
        existing = customer_repository.get_by_phone(lead["whatsapp"])
        lead_preferences = lead.get("preferences") or []

        if existing:
            existing_dict = _as_dict(existing)
            merged_preferences = _merge_preferences(
                existing_dict.get("preferences"), lead_preferences
            )
            if merged_preferences != _normalize_preferences(existing_dict.get("preferences")):
                existing_dict["preferences"] = merged_preferences
                customer_repository.update(existing_dict)
            return existing_dict

        customer = Customer(
            phone=lead["whatsapp"],
            name=lead.get("name"),
            status="active",
            plan=plan,
            preferences=_normalize_preferences(lead_preferences),
        )
        customer_repository.save(customer)
        return customer.to_dict()
