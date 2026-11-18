# Builder report — T050 Privacy/terms at opt-in

**SDD:** [T050-privacy-terms-opt-in-sdd.md](./T050-privacy-terms-opt-in-sdd.md)  
**Branch:** `feat/t050-privacy-terms-opt-in`  
**Date:** 2026-11-18

## Expected work

| ID | Result | Files | What changed |
|----|--------|-------|--------------|
| EW-01 | done | `core/config.py`, `tests/unit/core/test_config_and_queues.py` | Added `PRIVACY_POLICY_URL` / `TERMS_OF_SERVICE_URL` via `_url_env` with placeholders `https://example.com/privacy` and `https://example.com/terms`. Unset/empty/whitespace → placeholders; non-empty stripped strings used as-is. Autouse fixture clears the new env vars. Tests: defaults, override, whitespace fallback. |
| EW-02 | done | `domain/privacy_terms.py`, `tests/unit/domain/test_privacy_terms.py` | `PRIVACY_TERMS_VERSION = "2026-11-18"`; `build_privacy_terms_notice` Portuguese copy with both URLs; `privacy_terms_consent_metadata` returns version + UTC ISO `Z`. Tests cover constant, notice content, fixed UTC timestamp, naive→UTC. |
| EW-03 | done | `domain/models/pre_sale_customer.py`, `domain/services/pre_sale_customer_service.py`, `tests/unit/domain/test_pre_sale_customer_service.py` | Pre-sale model serializes consent fields. New create stamps consent and returns `privacy_terms_notice` from config URLs. Existing email returns copy without save. Tests assert version, `accepted_at` ending in `Z`, both placeholder URLs in notice. |
| EW-04 | done | `domain/models/customer.py`, `domain/services/pre_sale_customer_service.py`, `tests/unit/domain/test_pre_sale_customer_service.py`, `tests/unit/domain/test_models_and_repositories.py` | Customer model optional consent fields (default `None`). Activate: new customer copies lead consent or stamps fresh; existing without consent copies from lead when present; preference merge unchanged; response includes `privacy_terms_notice`. Tests cover new activate, consent copy on existing phone, missing lead, preference merge. |
| EW-05 | done | `api/handlers/pre_sale_customer_handler.py` | Unchanged. Handler still validates HTTP and returns service JSON; no notice/consent logic in API layer. |
| EW-06 | done | `docs/DEPLOYMENT.md`, `docs/operations/PRODUCTION.md` | DEPLOYMENT section for the two URL env vars + placeholder defaults. PRODUCTION pre-sale route note + config note for privacy/terms opt-in. CL #68 / T071 untouched. |
| EW-07 | done | `docs/ROADMAP-TASKS.md`, `docs/COMMERCIAL-LAUNCH.md`, `docs/specs/sdd/T050-privacy-terms-opt-in-sdd.md`, `docs/specs/sdd/INDEX.md` | After EW-01–EW-06 and EW-08 gate: T050 checked; CL #60 checked only; SDD status `implemented`; INDEX T050 `implemented`. |
| EW-08 | done | whole diff | No T051/T070/T071/payments/legal PDF. Gate commands below pass; total coverage **96.59%**. |

## Deviations from the SDD / SPEC

None material. Notice is returned on create/activate JSON (`privacy_terms_notice`) rather than enqueued as WhatsApp text (no send path exists on those endpoints today).

## Files touched

Handoff: `CONTEXT.md`, `PLAN.md`, `SPEC.md`.

| Path | EW |
|------|----|
| `core/config.py` | EW-01 |
| `tests/unit/core/test_config_and_queues.py` | EW-01 |
| `domain/privacy_terms.py` (new) | EW-02 |
| `tests/unit/domain/test_privacy_terms.py` (new) | EW-02 |
| `domain/models/pre_sale_customer.py` | EW-03 |
| `domain/services/pre_sale_customer_service.py` | EW-03, EW-04 |
| `tests/unit/domain/test_pre_sale_customer_service.py` | EW-03, EW-04 |
| `domain/models/customer.py` | EW-04 |
| `tests/unit/domain/test_models_and_repositories.py` | EW-04 |
| `api/handlers/pre_sale_customer_handler.py` | EW-05 (unchanged) |
| `docs/DEPLOYMENT.md` | EW-06 |
| `docs/operations/PRODUCTION.md` | EW-06 |
| `docs/ROADMAP-TASKS.md` | EW-07 |
| `docs/COMMERCIAL-LAUNCH.md` | EW-07 |
| `docs/specs/sdd/T050-privacy-terms-opt-in-sdd.md` | EW-07 (+ Expected work expansion) |
| `docs/specs/sdd/INDEX.md` | EW-07 |
| `docs/specs/sdd/T050-builder-report.md` (new) | report |

## Test commands and results

Run from the repo root with the repo virtualenv (`.venv`):

| Command | Result |
|---------|--------|
| `PYTHONPATH=. .venv/bin/python -m pytest --override-ini='addopts=' -q` | **227 passed** |
| `PYTHONPATH=. .venv/bin/python -m pytest --cov --cov-report=term-missing:skip-covered` | passed; total coverage **96.59%** (`fail_under` 95) |
| `.venv/bin/ruff check api core domain infrastructure tests quality` | All checks passed |
| `.venv/bin/python quality/check_import_style.py` | Import style OK |
