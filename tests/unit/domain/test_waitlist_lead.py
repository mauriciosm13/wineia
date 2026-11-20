from datetime import datetime, timezone

from domain.models.waitlist_lead import WaitlistLead, _as_utc_iso_z


def test_as_utc_iso_z_none_and_string():
    assert _as_utc_iso_z(None) is None
    assert _as_utc_iso_z("2026-01-01T00:00:00Z") == "2026-01-01T00:00:00Z"


def test_as_utc_iso_z_naive_and_aware():
    naive = datetime(2026, 6, 1, 12, 0, 0)
    assert _as_utc_iso_z(naive) == "2026-06-01T12:00:00Z"
    aware = datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc)
    assert _as_utc_iso_z(aware) == "2026-06-01T09:00:00Z"


def test_waitlist_lead_to_dict_defaults_timestamps():
    lead = WaitlistLead(
        phone="+5511999999999",
        name="Ana",
        email="ana@example.com",
        birth_date="1990-01-01",
    )
    payload = lead.to_dict()
    assert payload["phone"] == "+5511999999999"
    assert payload["created_at"].endswith("Z")
    assert payload["updated_at"].endswith("Z")
