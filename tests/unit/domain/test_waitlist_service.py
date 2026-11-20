from datetime import date, datetime, timezone

import pytest

from domain.models.waitlist_lead import WaitlistLead
from domain.services.waitlist_service import WaitlistService, WaitlistValidationError, _as_dict, _as_utc_iso_z, validate_minimum_age
from tests.fakes.repositories import FakeWaitlistRepository


def test_validate_minimum_age_accepts_adult():
    assert validate_minimum_age("2000-01-15", min_age=18, today=date(2026, 11, 20)) == "2000-01-15"


def test_validate_minimum_age_rejects_underage_portuguese():
    with pytest.raises(WaitlistValidationError) as exc:
        validate_minimum_age("2015-05-01", min_age=18, today=date(2026, 11, 20))
    assert "pelo menos 18 anos" in str(exc.value)


def test_validate_minimum_age_rejects_future_date():
    with pytest.raises(WaitlistValidationError) as exc:
        validate_minimum_age("2099-01-01", min_age=18, today=date(2026, 11, 20))
    assert "futuro" in str(exc.value)


def test_upsert_creates_lead_and_returns_privacy_notice():
    repo = FakeWaitlistRepository()
    service = WaitlistService(repo)
    now = datetime(2026, 11, 20, 12, 0, tzinfo=timezone.utc)

    lead, created = service.upsert_lead(
        "whatsapp:+55 11 98888-7777",
        "  Ana  ",
        "Ana@Example.COM",
        "1990-04-10",
        now=now,
    )

    assert created is True
    assert lead["phone"] == "+5511988887777"
    assert lead["name"] == "Ana"
    assert lead["email"] == "ana@example.com"
    assert lead["birth_date"] == "1990-04-10"
    assert lead["created_at"] == "2026-11-20T12:00:00Z"
    assert lead["updated_at"] == "2026-11-20T12:00:00Z"
    assert "Política de Privacidade" in lead["privacy_terms_notice"]
    assert repo.save_calls == 1
    assert repo.update_calls == 0


def test_upsert_updates_existing_by_phone_bumps_updated_at():
    repo = FakeWaitlistRepository()
    repo.seed(
        {
            "phone": "+5511999999999",
            "name": "Old",
            "email": "old@example.com",
            "birth_date": "1988-01-01",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }
    )
    service = WaitlistService(repo)
    later = datetime(2026, 11, 20, 15, 30, tzinfo=timezone.utc)

    lead, created = service.upsert_lead(
        "+5511999999999",
        "New Name",
        "new@example.com",
        "1988-01-01",
        now=later,
    )

    assert created is False
    assert lead["name"] == "New Name"
    assert lead["email"] == "new@example.com"
    assert lead["created_at"] == "2026-01-01T00:00:00Z"
    assert lead["updated_at"] == "2026-11-20T15:30:00Z"
    assert repo.save_calls == 0
    assert repo.update_calls == 1


def test_upsert_rejects_invalid_phone():
    service = WaitlistService(FakeWaitlistRepository())
    with pytest.raises(WaitlistValidationError) as exc:
        service.upsert_lead("123", "Ana", "ana@example.com", "1990-01-01")
    assert "phone" in str(exc.value)


def test_upsert_rejects_missing_name():
    service = WaitlistService(FakeWaitlistRepository())
    with pytest.raises(WaitlistValidationError) as exc:
        service.upsert_lead("+5511999999999", "  ", "ana@example.com", "1990-01-01")
    assert "name" in str(exc.value)


def test_list_leads_returns_all():
    repo = FakeWaitlistRepository()
    repo.seed(
        {
            "phone": "+5511111111111",
            "name": "A",
            "email": "a@example.com",
            "birth_date": "1990-01-01",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }
    )
    service = WaitlistService(repo)
    leads = service.list_leads()
    assert len(leads) == 1
    assert leads[0]["phone"] == "+5511111111111"


def test_validate_age_accepts_date_object():
    assert validate_minimum_age(date(2000, 1, 1), min_age=18, today=date(2018, 1, 1)) == "2000-01-01"


def test_validate_age_birthday_not_yet_still_underage():
    with pytest.raises(WaitlistValidationError):
        validate_minimum_age(date(2000, 12, 31), min_age=18, today=date(2018, 12, 30))


def test_validate_age_on_birthday_counts_as_adult():
    assert validate_minimum_age("2000-11-20", min_age=18, today=date(2018, 11, 20)) == "2000-11-20"


def test_validate_age_negative_min_falls_back_to_default():
    with pytest.raises(WaitlistValidationError) as exc:
        validate_minimum_age("2015-01-01", min_age=-1, today=date(2026, 11, 20))
    assert "anos" in str(exc.value)


def test_upsert_rejects_bad_email_and_name_types():
    service = WaitlistService(FakeWaitlistRepository())
    with pytest.raises(WaitlistValidationError) as exc:
        service.upsert_lead("+5511999999999", "Ana", None, "1990-01-01")
    assert "email" in str(exc.value)
    with pytest.raises(WaitlistValidationError) as exc:
        service.upsert_lead("+5511999999999", "Ana", "not-an-email", "1990-01-01")
    assert "email" in str(exc.value)
    with pytest.raises(WaitlistValidationError) as exc:
        service.upsert_lead("+5511999999999", None, "ana@example.com", "1990-01-01")
    assert "name" in str(exc.value)


def test_upsert_rejects_bad_birth_date_formats():
    service = WaitlistService(FakeWaitlistRepository())
    with pytest.raises(WaitlistValidationError):
        service.upsert_lead("+5511999999999", "Ana", "ana@example.com", None)
    with pytest.raises(WaitlistValidationError):
        service.upsert_lead("+5511999999999", "Ana", "ana@example.com", "  ")
    with pytest.raises(WaitlistValidationError):
        service.upsert_lead("+5511999999999", "Ana", "ana@example.com", "20-01-1990")
    with pytest.raises(WaitlistValidationError):
        service.upsert_lead("+5511999999999", "Ana", "ana@example.com", 19900101)


def test_as_dict_and_as_utc_helpers():
    assert _as_utc_iso_z(None) is None
    assert _as_utc_iso_z("already") == "already"
    naive = datetime(2026, 1, 2, 3, 4, 5)
    assert _as_utc_iso_z(naive) == "2026-01-02T03:04:05Z"
    lead = WaitlistLead("+5511999999999", "A", "a@b.co", "1990-01-01")
    assert _as_dict(lead)["phone"] == "+5511999999999"
    assert _as_dict({"phone": "+1"})["phone"] == "+1"


def test_upsert_update_path_with_model_existing():
    repo = FakeWaitlistRepository()
    existing = WaitlistLead(
        phone="+5511888777666",
        name="Old",
        email="old@example.com",
        birth_date="1985-02-02",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    repo.save(existing)
    repo.save_calls = 0
    service = WaitlistService(repo)
    later = datetime(2026, 11, 20, 18, 0, tzinfo=timezone.utc)
    lead, created = service.upsert_lead(
        "+5511888777666",
        "New",
        "new@example.com",
        "1985-02-02",
        now=later,
    )
    assert created is False
    assert lead["name"] == "New"
    assert lead["updated_at"] == "2026-11-20T18:00:00Z"
