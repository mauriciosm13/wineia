from datetime import datetime, timezone

PRIVACY_TERMS_VERSION = "2026-11-18"

_NOTICE_TEMPLATE = (
    "Ao continuar, você concorda com nossa Política de Privacidade ({privacy_url}) "
    "e Termos de Uso ({terms_url})."
)


def build_privacy_terms_notice(privacy_url, terms_url):
    return _NOTICE_TEMPLATE.format(privacy_url=privacy_url, terms_url=terms_url)


def _as_utc_iso_z(moment):
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    else:
        moment = moment.astimezone(timezone.utc)
    return moment.isoformat().replace("+00:00", "Z")


def privacy_terms_consent_metadata(now=None):
    moment = now if now is not None else datetime.now(timezone.utc)
    return {
        "privacy_terms_version": PRIVACY_TERMS_VERSION,
        "privacy_terms_accepted_at": _as_utc_iso_z(moment),
    }
