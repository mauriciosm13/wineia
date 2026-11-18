# T072 builder report — Operator API authentication

Branch: `feat/t072-operator-api-auth`

| ID | Result | Files | What changed |
|----|--------|-------|--------------|
| EW-01 | done | `api/internal_job_auth.py` | Extended `path_requires_internal_job_auth` for `/customers`, `/customers/*`, `/ia/suggestions`, `/recommendation-contents`; jobs/workers unchanged; health/webhook false. |
| EW-02 | done | `api/routes.py` (unchanged call site), `tests/unit/api/test_internal_job_auth.py` | Existing router gate covers new paths. Tests: 401 missing/wrong/unset secret before handler; valid secret reaches handler; jobs/workers still gated; health/webhook open. |
| EW-03 | done | `tests/unit/api/test_internal_job_auth.py`, `tests/unit/api/test_customer_routes.py` | Auth matrix for customers / ia / recommendation-contents; health + webhook open; fail-closed unset; accept valid. Customer route dispatch tests send secret header. |
| EW-04 | done | `docs/operations/PRODUCTION.md`, `docs/DEPLOYMENT.md`, `docs/threat-model.md`, `docs/decision.md`, `docs/LAUNCH-CHECKLIST.md`, `docs/operations/LGPD-EXPORT-DELETE.md`, `docs/operations/SECRET-MANAGER-MIGRATION.md` | Operator routes documented as secret-gated; DEPLOYMENT section renamed to include operator APIs; threat-model entry points + §4.5; decision.md closes unauthenticated-operator gap; LAUNCH-CHECKLIST checks; LGPD curls send header; SECRET-MANAGER anchor updated to renamed DEPLOYMENT heading. |
| EW-05 | done | `docs/ROADMAP-TASKS.md`, `docs/specs/sdd/INDEX.md`, `docs/specs/sdd/T072-operator-api-auth-sdd.md`, `docs/COMMERCIAL-LAUNCH.md`, `CONTEXT.md` | T072 checked/implemented; CL #19 authenticated operator API wording; CONTEXT reflects T072. |
| EW-06 | done | whole diff | No payments/T004/Dependabot/templates/retention. Coverage 96.45% (≥95%). Ruff + import style pass. |

## Files touched

- `CONTEXT.md`
- `api/internal_job_auth.py`
- `tests/unit/api/test_internal_job_auth.py`
- `tests/unit/api/test_customer_routes.py`
- `docs/specs/sdd/T072-operator-api-auth-sdd.md`
- `docs/specs/sdd/T072-builder-report.md`
- `docs/specs/sdd/INDEX.md`
- `docs/ROADMAP-TASKS.md`
- `docs/COMMERCIAL-LAUNCH.md`
- `docs/DEPLOYMENT.md`
- `docs/operations/PRODUCTION.md`
- `docs/operations/LGPD-EXPORT-DELETE.md`
- `docs/operations/SECRET-MANAGER-MIGRATION.md`
- `docs/LAUNCH-CHECKLIST.md`
- `docs/threat-model.md`
- `docs/decision.md`

## Test commands

```bash
source .venv/bin/activate
python -m pytest tests/unit/api/test_internal_job_auth.py tests/unit/api/test_customer_routes.py -q
# 24 passed
python quality/check_import_style.py
# Import style OK
ruff check api/internal_job_auth.py tests/unit/api/test_internal_job_auth.py tests/unit/api/test_customer_routes.py
# All checks passed
python -m pytest -q --cov=domain --cov=core --cov-fail-under=95
# Required test coverage of 95% reached. Total coverage: 96.45%
```
