# Builder report — T051 Export/delete tooling

**SDD:** [T051-export-delete-tooling-sdd.md](./T051-export-delete-tooling-sdd.md)  
**Branch:** `feat/t051-export-delete-tooling`  
**Date:** 2026-11-18

## Expected work

| ID | Result | Files | What changed |
|----|--------|-------|--------------|
| EW-01 | done | `domain/repositories/pre_sale_customer_repository.py`, `infrastructure/repositories/datastore_pre_sale_customer_repository.py`, `tests/fakes/repositories.py` | Abstract `get_by_whatsapp` + `delete`. Datastore queries `whatsapp ==` and deletes by email key. Fake indexes by email, looks up by whatsapp (dict or model), tracks `delete_calls`. Covered via privacy-service tests. |
| EW-02 | done | `domain/services/customer_privacy_service.py`, `tests/unit/domain/test_customer_privacy_service.py` | `export_customer` returns customer PII fields + optional `pre_sale`; `None` when missing; no secrets. Tests: missing, without pre-sale, with pre-sale, model objects. |
| EW-03 | done | same | `erase_customer` sets name `REDACTED`, preferences `[]`, status `canceled`, opt-in false, clears consent; updates customer; deletes linked pre-sale; returns `erased` + `pre_sale_deleted`. No recommendation-history delete. Tests: missing, without/with pre-sale. |
| EW-04 | done | `api/handlers/customer_handler.py`, `tests/unit/api/test_customer_routes.py` | Routes `GET .../export` and `POST .../erase` with URL-decoded phone; thin handlers; 200/404. Route tests for export and erase dispatch. |
| EW-05 | done | `docs/operations/LGPD-EXPORT-DELETE.md`, `docs/operations/PRODUCTION.md` | Runbook: curl, unauthenticated operator risk, anonymize vs retain. PRODUCTION routes table + Related link. |
| EW-06 | done | `docs/ROADMAP-TASKS.md`, `docs/COMMERCIAL-LAUNCH.md`, SDD, `docs/specs/sdd/INDEX.md` | T051 checked; CL #62 checked; SDD + INDEX `implemented`. Only those status lines. |
| EW-07 | done | whole diff | No payments T040–T043, T004, or T070 deliverables beyond PRODUCTION route accuracy. Gate commands below pass; total coverage **96.45%**. |

## Deviations from the SDD / SPEC

1. Handoff files `CONTEXT.md`, `PLAN.md`, `SPEC.md` updated for T051 (orchestrator process; not Expected work products).
2. Dead `else` branches in `_as_dict` / `_pre_sale_as_dict` (non-dict, non-`to_dict`) remain uncovered — same pattern as other services; total coverage still ≥ 95%.

## Files touched

| Path | EW |
|------|----|
| `domain/repositories/pre_sale_customer_repository.py` | EW-01 |
| `infrastructure/repositories/datastore_pre_sale_customer_repository.py` | EW-01 |
| `tests/fakes/repositories.py` | EW-01 |
| `domain/services/customer_privacy_service.py` (new) | EW-02, EW-03 |
| `tests/unit/domain/test_customer_privacy_service.py` (new) | EW-01–EW-03 |
| `api/handlers/customer_handler.py` | EW-04 |
| `tests/unit/api/test_customer_routes.py` | EW-04 |
| `docs/operations/LGPD-EXPORT-DELETE.md` (new) | EW-05 |
| `docs/operations/PRODUCTION.md` | EW-05 |
| `docs/ROADMAP-TASKS.md` | EW-06 |
| `docs/COMMERCIAL-LAUNCH.md` | EW-06 |
| `docs/specs/sdd/T051-export-delete-tooling-sdd.md` | EW-06 (status; body is orchestrator handoff) |
| `docs/specs/sdd/INDEX.md` | EW-06 |
| `docs/specs/sdd/T051-builder-report.md` (new) | this report |
| `CONTEXT.md`, `PLAN.md`, `SPEC.md` | handoff (not EW products) |

## Test commands and results

Run from the repo root with `.venv`, after EW-01–EW-05 and before/with EW-06 flips:

| Command | Result |
|---------|--------|
| `PYTHONPATH=. .venv/bin/python -m pytest` | **237 passed** |
| `PYTHONPATH=. .venv/bin/python -m pytest --cov --cov-report=term-missing` | 237 passed; total coverage **96.45%** (`fail_under` 95); `customer_privacy_service.py` 95% |
| `.venv/bin/ruff check api core domain infrastructure tests quality` | All checks passed |
| `.venv/bin/python quality/check_import_style.py` | Import style OK |
