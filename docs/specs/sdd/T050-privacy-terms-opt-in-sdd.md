# SDD — Privacy/terms at opt-in (T050)

**Status:** implemented  
**Task:** [T050](../../ROADMAP-TASKS.md)  
**Comparison contract:** this Expected work list is what the reviewer checks against [T050-builder-report.md](./T050-builder-report.md).

## Problem

LGPD / commercial launch item #60 requires that privacy policy and terms of service are linked at opt-in, and that consent metadata is persisted. Pre-sale create and activation currently store only name, email, WhatsApp, and preferences — no notice text, no URLs, no consent version or timestamp.

## Goals

- Surface a Portuguese privacy/terms notice with links at **pre-sale create** and at **pre-sale activation** (first customer promotion path).
- Read URLs from env via `core/config`; use documented placeholders when unset; **never block** registration when URLs are unset.
- Persist `privacy_terms_version` and `privacy_terms_accepted_at` when the user opts in (pre-sale create / activation).
- Domain owns notice text and consent rules; handlers stay thin.

## Non-goals

- T051 export/delete tooling.
- T070 / T071 (another agent may own T071 in parallel). Do not edit COMMERCIAL-LAUNCH item 68 / T071 files.
- T040–T043 payments; T004.
- Full legal PDF or long legal markdown in the repo.
- Blocking registration when privacy/terms URLs are unset.
- Changing webhook IA / messaging cancel flow beyond returning notice text on opt-in surfaces.
- New pip dependencies.

## Behavior

### Config

| Environment variable | Default when unset/empty | Meaning |
|----------------------|--------------------------|---------|
| `PRIVACY_POLICY_URL` | `https://example.com/privacy` | Public privacy policy URL used in notice copy |
| `TERMS_OF_SERVICE_URL` | `https://example.com/terms` | Public terms URL used in notice copy |

Whitespace-only values fall back to the same placeholders. Registration must not fail because these env vars are missing.

### Domain

| Constant / helper | Rule |
|-------------------|------|
| `PRIVACY_TERMS_VERSION` | Stable string `"2026-11-18"` (domain module) |
| `build_privacy_terms_notice(privacy_url, terms_url)` | Portuguese notice including both URLs |
| `privacy_terms_consent_metadata(now=None)` | Returns `privacy_terms_version` + `privacy_terms_accepted_at` (UTC ISO-8601 with `Z`) |

Notice copy (Portuguese), with URLs interpolated:

```text
Ao continuar, você concorda com nossa Política de Privacidade ({privacy_url}) e Termos de Uso ({terms_url}).
```

### Pre-sale create

`PreSaleCustomerService.create_customer`:

1. If email already exists → return existing lead copy (unchanged; no re-stamp required).
2. Else create `PreSaleCustomer` with consent metadata stamped (`privacy_terms_version`, `privacy_terms_accepted_at`).
3. Response dict includes those fields plus `privacy_terms_notice` built from config URLs (placeholders OK).

### Activation

`PreSaleCustomerService.activate`:

1. Missing lead → `None` (unchanged).
2. Existing customer by phone → merge preferences as today; if customer lacks consent fields and lead has them, copy lead consent onto customer and `update`; include `privacy_terms_notice` in returned dict.
3. New customer → create `Customer` with consent copied from lead when present, otherwise stamp fresh consent metadata; include `privacy_terms_notice` in returned dict.

Handlers remain parse/validate/respond only; they do not build notice text or invent consent timestamps.

### Models

- `PreSaleCustomer` / `Customer` serialize `privacy_terms_version` and `privacy_terms_accepted_at` (may be `None` until accepted).
- Migration-on-read does **not** invent consent; missing fields stay absent/`None`.

## Expected work

The builder implements only these items. The reviewer marks each **match**, **gap**, or **extra**.

| ID | Must be true when the work is done | Where |
|----|-------------------------------------|--------|
| EW-01 | `core/config.py` defines `PRIVACY_POLICY_URL` and `TERMS_OF_SERVICE_URL` from env of the same names. Unset or empty/whitespace → `https://example.com/privacy` and `https://example.com/terms`. Non-empty strings are used as-is (stripped). Unit tests reload config under monkeypatched env and assert defaults + overrides. | `core/config.py`, `tests/unit/core/test_config_and_queues.py` |
| EW-02 | Domain module defines `PRIVACY_TERMS_VERSION = "2026-11-18"`, `build_privacy_terms_notice(privacy_url, terms_url)` returning the Portuguese notice with both URLs, and `privacy_terms_consent_metadata(now=None)` returning `{"privacy_terms_version": ..., "privacy_terms_accepted_at": ...}` with UTC ISO ending in `Z`. Unit tests cover notice content and metadata shape. | `domain/privacy_terms.py`, `tests/unit/domain/test_privacy_terms.py` |
| EW-03 | New pre-sale create stamps consent metadata on the lead, persists via repository `save`, and returns those fields plus `privacy_terms_notice` (from config URLs). Existing email path still returns a copy without saving. Creating never raises solely because URLs were unset. Tests cover new create + existing email. | `domain/models/pre_sale_customer.py`, `domain/services/pre_sale_customer_service.py`, `tests/unit/domain/test_pre_sale_customer_service.py` |
| EW-04 | Activate creates/updates `Customer` with consent: new customer gets lead consent when present else fresh stamp; existing customer without consent copies from lead when lead has it. Returned dict includes `privacy_terms_notice`. Preference merge behavior unchanged. Tests cover new activate, existing phone merge, missing lead. | `domain/models/customer.py`, `domain/services/pre_sale_customer_service.py`, `tests/unit/domain/test_pre_sale_customer_service.py` (and customer model tests if needed) |
| EW-05 | API pre-sale handlers stay thin: no new business rules for notice/consent in the handler; create/activate still return JSON from the service. No handler-only consent logic. | `api/handlers/pre_sale_customer_handler.py` (verify unchanged or only pass-through) |
| EW-06 | Docs: `DEPLOYMENT.md` documents the two URL env vars (defaults = placeholders). `PRODUCTION.md` notes privacy/terms notice at pre-sale opt-in and the env vars (light touch). Do not edit COMMERCIAL-LAUNCH item 68 or T071 files. | those files |
| EW-07 | Only after EW-01–EW-06 and EW-08 hold: `ROADMAP-TASKS.md` checks **only** the T050 line; `COMMERCIAL-LAUNCH.md` checks **only** item 60; this SDD status is `implemented`; `INDEX.md` T050 row is `implemented`. | those files (T050 / #60 only) |
| EW-08 | Diff does not implement T051 export/delete, T070/T071, payments T040–T043, or add a legal PDF. Domain/core coverage stays ≥ 95%. Ruff + import style pass. | whole diff |

## Builder report

After implementation, write `docs/specs/sdd/T050-builder-report.md`:

| ID | Result (`done` or `skipped`) | Files | What changed |
|----|-------------------------------|-------|----------------|

Add a **Files touched** list of every path in the diff and the exact test commands with results. The reviewer treats any path not justified by an ID as **extra**.

## Reviewer comparison

Read this file, the builder report, and the diff. Return only:

- One line per ID: `EW-xx match|gap — evidence`
- Extras: paths or behavior not in the table
- Bugs that break an ID
- Verdict: accept or reject

Do not implement.

## Related

- [CONTEXT.md](../../../CONTEXT.md)
- [COMMERCIAL-LAUNCH.md](../../COMMERCIAL-LAUNCH.md) item 60
- [docs/commercial.md](../../commercial.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD stub |
| 2026-11-18 | Expand to T031-style Expected work EW-01–EW-08 (parent T050 decisions) |
| 2026-11-18 | Mark implemented after EW hold |
