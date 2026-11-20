from datetime import date, datetime, timezone

from core import config
from domain.models.waitlist_lead import WaitlistLead
from domain.phone import normalize_phone
from domain.privacy_terms import build_privacy_terms_notice


class WaitlistValidationError(ValueError):
    """User-facing validation failure (Portuguese message)."""


def _utc_now():
    return datetime.now(timezone.utc)


def _as_utc_iso_z(moment):
    if moment is None:
        return None
    if isinstance(moment, str):
        return moment
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    else:
        moment = moment.astimezone(timezone.utc)
    return moment.isoformat().replace("+00:00", "Z")


def _as_dict(record):
    if isinstance(record, dict):
        return dict(record)
    if hasattr(record, "to_dict"):
        return record.to_dict()
    return dict(record)


def _privacy_terms_notice():
    return build_privacy_terms_notice(config.PRIVACY_POLICY_URL, config.TERMS_OF_SERVICE_URL)


def _with_notice(payload):
    result = dict(payload)
    result["privacy_terms_notice"] = _privacy_terms_notice()
    return result


def _normalize_email(email):
    if email is None or not isinstance(email, str):
        raise WaitlistValidationError("email é obrigatório")
    value = email.strip().lower()
    if not value:
        raise WaitlistValidationError("email não pode ser vazio")
    if "@" not in value or "." not in value.split("@")[-1]:
        raise WaitlistValidationError("email deve ser um endereço válido")
    return value


def _normalize_name(name):
    if name is None or not isinstance(name, str):
        raise WaitlistValidationError("name é obrigatório")
    value = name.strip()
    if not value:
        raise WaitlistValidationError("name não pode ser vazio")
    return value


def _parse_birth_date(birth_date):
    if birth_date is None:
        raise WaitlistValidationError("birth_date é obrigatório")
    if isinstance(birth_date, date) and not isinstance(birth_date, datetime):
        return birth_date
    if not isinstance(birth_date, str):
        raise WaitlistValidationError("birth_date deve estar no formato ISO (AAAA-MM-DD)")
    value = birth_date.strip()
    if not value:
        raise WaitlistValidationError("birth_date não pode ser vazio")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise WaitlistValidationError(
            "birth_date deve estar no formato ISO (AAAA-MM-DD)"
        ) from exc


def _age_on(birth, today):
    years = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        years -= 1
    return years


def validate_minimum_age(birth_date, min_age=None, today=None):
    """Return ISO birth_date string if age >= min_age; else raise WaitlistValidationError."""
    birth = _parse_birth_date(birth_date)
    threshold = config.WAITLIST_MIN_AGE if min_age is None else int(min_age)
    if threshold < 0:
        threshold = config.DEFAULT_WAITLIST_MIN_AGE
    reference = today if today is not None else date.today()
    if birth > reference:
        raise WaitlistValidationError("birth_date não pode ser no futuro")
    age = _age_on(birth, reference)
    if age < threshold:
        raise WaitlistValidationError(
            f"É necessário ter pelo menos {threshold} anos para se cadastrar."
        )
    return birth.isoformat()


def normalize_waitlist_input(phone, name, email, birth_date, min_age=None, today=None):
    normalized_phone = normalize_phone(phone)
    if not normalized_phone:
        raise WaitlistValidationError(
            "phone deve ser um número WhatsApp válido (formato E.164)"
        )
    return {
        "phone": normalized_phone,
        "name": _normalize_name(name),
        "email": _normalize_email(email),
        "birth_date": validate_minimum_age(birth_date, min_age=min_age, today=today),
    }


class WaitlistService:

    def __init__(self, repository):
        self.repository = repository

    def upsert_lead(self, phone, name, email, birth_date, now=None):
        fields = normalize_waitlist_input(phone, name, email, birth_date)
        moment = now if now is not None else _utc_now()
        existing = self.repository.get_by_phone(fields["phone"])

        if existing:
            lead = _as_dict(existing)
            lead["name"] = fields["name"]
            lead["email"] = fields["email"]
            lead["birth_date"] = fields["birth_date"]
            lead["updated_at"] = _as_utc_iso_z(moment)
            if "created_at" in lead:
                lead["created_at"] = _as_utc_iso_z(lead["created_at"])
            self.repository.update(lead)
            return _with_notice(lead), False

        lead = WaitlistLead(
            phone=fields["phone"],
            name=fields["name"],
            email=fields["email"],
            birth_date=fields["birth_date"],
            created_at=moment,
            updated_at=moment,
        )
        self.repository.save(lead)
        return _with_notice(lead.to_dict()), True

    def list_leads(self):
        leads = self.repository.list_all()
        return [_as_dict(lead) for lead in leads]
