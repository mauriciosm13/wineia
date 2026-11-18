from datetime import datetime, timezone

from domain.privacy_terms import PRIVACY_TERMS_VERSION, build_privacy_terms_notice, privacy_terms_consent_metadata


def test_privacy_terms_version_constant():
    assert PRIVACY_TERMS_VERSION == "2026-11-18"


def test_build_privacy_terms_notice_includes_both_urls():
    notice = build_privacy_terms_notice(
        "https://example.com/privacy",
        "https://example.com/terms",
    )
    assert "https://example.com/privacy" in notice
    assert "https://example.com/terms" in notice
    assert "Política de Privacidade" in notice
    assert "Termos de Uso" in notice
    assert notice.startswith("Ao continuar, você concorda")


def test_privacy_terms_consent_metadata_shape_and_utc_z():
    fixed = datetime(2026, 11, 18, 12, 30, 0, tzinfo=timezone.utc)
    meta = privacy_terms_consent_metadata(now=fixed)
    assert meta["privacy_terms_version"] == "2026-11-18"
    assert meta["privacy_terms_accepted_at"] == "2026-11-18T12:30:00Z"


def test_privacy_terms_consent_metadata_naive_now_treated_as_utc():
    fixed = datetime(2026, 11, 18, 8, 0, 0)
    meta = privacy_terms_consent_metadata(now=fixed)
    assert meta["privacy_terms_accepted_at"].endswith("Z")
    assert "2026-11-18T08:00:00" in meta["privacy_terms_accepted_at"]
