from domain.models.customer import Customer, CustomerStatus, DEFAULT_PLAN_TIER, normalize_customer_fields, validate_plan_tier

UPDATABLE_FIELDS = ("name", "status", "plan", "preferences", "plan_tier", "weekly_education_opt_in")


def _as_dict(record):
    if isinstance(record, dict):
        payload = dict(record)
    elif hasattr(record, "to_dict"):
        payload = record.to_dict()
    else:
        payload = dict(record)
    return normalize_customer_fields(payload)


def _normalize_preferences(preferences):
    if preferences is None:
        return None
    if not isinstance(preferences, list):
        raise ValueError("preferences must be a list")
    normalized = []
    for preference in preferences:
        if not isinstance(preference, str):
            raise ValueError("preferences items must be strings")
        stripped = preference.strip()
        if not stripped:
            raise ValueError("preferences items cannot be empty")
        normalized.append(stripped)
    return normalized


class CustomerService:

    def __init__(self, repository):
        self.repository = repository

    def create_customer(self, phone, name, status, plan, plan_tier=None, weekly_education_opt_in=None):
        existing = self.repository.get_by_phone(phone)

        if existing:
            return _as_dict(existing)

        if plan_tier is not None:
            validate_plan_tier(plan_tier)
        if weekly_education_opt_in is not None and not isinstance(weekly_education_opt_in, bool):
            raise ValueError("weekly_education_opt_in must be a boolean")

        customer = Customer(
            phone,
            name,
            status,
            plan,
            plan_tier=plan_tier if plan_tier is not None else DEFAULT_PLAN_TIER,
            weekly_education_opt_in=weekly_education_opt_in,
        )

        self.repository.save(customer)

        return customer.to_dict()

    def list_customers(self):
        return [_as_dict(customer) for customer in self.repository.list_all()]

    def get_customer(self, phone):
        customer = self.repository.get_by_phone(phone)
        if customer is None:
            return None
        return _as_dict(customer)

    def update_customer(self, phone, fields):
        existing = self.repository.get_by_phone(phone)
        if existing is None:
            return None

        if not isinstance(fields, dict):
            raise ValueError("fields must be a dict")

        updates = {}
        for field_name in UPDATABLE_FIELDS:
            if field_name not in fields:
                continue
            updates[field_name] = fields[field_name]

        if not updates:
            raise ValueError("at least one updatable field is required")

        customer = _as_dict(existing)

        if "name" in updates:
            name = updates["name"]
            if name is not None and not isinstance(name, str):
                raise ValueError("name must be a string")
            if isinstance(name, str) and not name.strip():
                raise ValueError("name cannot be empty")
            customer["name"] = name.strip() if isinstance(name, str) else name

        if "status" in updates:
            status = updates["status"]
            if status not in (CustomerStatus.active, CustomerStatus.canceled):
                raise ValueError("status must be active or canceled")
            customer["status"] = status

        if "plan" in updates:
            plan = updates["plan"]
            if plan is not None and not isinstance(plan, str):
                raise ValueError("plan must be a string")
            if isinstance(plan, str) and not plan.strip():
                raise ValueError("plan cannot be empty")
            customer["plan"] = plan.strip() if isinstance(plan, str) else plan

        if "plan_tier" in updates:
            plan_tier = updates["plan_tier"]
            validate_plan_tier(plan_tier)
            customer["plan_tier"] = plan_tier

        if "weekly_education_opt_in" in updates:
            opt_in = updates["weekly_education_opt_in"]
            if not isinstance(opt_in, bool):
                raise ValueError("weekly_education_opt_in must be a boolean")
            customer["weekly_education_opt_in"] = opt_in

        if "preferences" in updates:
            customer["preferences"] = _normalize_preferences(updates["preferences"])

        self.repository.update(customer)
        return customer
