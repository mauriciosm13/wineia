from datetime import datetime, timezone


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


class WaitlistLead:

    def __init__(
        self,
        phone,
        name,
        email,
        birth_date,
        created_at=None,
        updated_at=None,
    ):
        now = _utc_now()
        self.phone = phone
        self.name = name
        self.email = email
        self.birth_date = birth_date
        self.created_at = created_at if created_at is not None else now
        self.updated_at = updated_at if updated_at is not None else now

    def to_dict(self):
        return {
            "phone": self.phone,
            "name": self.name,
            "email": self.email,
            "birth_date": self.birth_date,
            "created_at": _as_utc_iso_z(self.created_at),
            "updated_at": _as_utc_iso_z(self.updated_at),
        }
