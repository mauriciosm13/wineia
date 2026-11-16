# Builder report — T061 Global Claude budget stop

**SDD:** [T061-global-claude-budget-stop-sdd.md](./T061-global-claude-budget-stop-sdd.md)  
**Branch:** `feat/t061-global-claude-budget`  
**Date:** 2026-11-16

## Expected work

| ID | Result | Files | What changed |
|----|--------|-------|--------------|
| EW-01 | done | `core/config.py`, `tests/unit/core/test_config_and_queues.py` | Added `CLAUDE_DAILY_CALL_BUDGET` via `_non_negative_int_env(..., 0)`. Unset/empty/non-integer/negative → `0`. Positive ints accepted. Tests: default unlimited, override 100, zero allowed, invalid fallback. Autouse fixture clears the new env var. |
| EW-02 | done | `domain/claude_budget.py`, `domain/repositories/claude_budget_repository.py`, `tests/unit/domain/test_claude_budget.py` | `ClaudeBudgetExceededError`, `utc_day_key`, `ensure_within_budget`, `record_successful_call`. ABC with `get_call_count` / `increment_call_count`. Domain has no `google.cloud` / Datastore client import. Fake-repo tests: unlimited skips repo, under-cap allows, at-cap raises, increment records UTC day. |
| EW-03 | done | `infrastructure/repositories/datastore_claude_budget_repository.py`, `tests/unit/infrastructure/test_datastore_claude_budget_repository.py` | Kind `ClaudeDailyBudget`, key = day_key, property `call_count`. Missing entity → 0; increment creates or updates and returns new count. Unit tests with mocked client. |
| EW-04 | done | `domain/services/ia_service.py`, `tests/unit/domain/test_ia_service.py` | Injectable `budget_repository` / `generate`; shared `_generate_with_budget` used by all three generate methods. Budget `> 0` → ensure then Claude then increment; budget `0` → no repo I/O. Lazy `_default_budget_repository` when budget `> 0` and repo unset. Tests: exceeded skips Claude; success increments; zero ignores repo; lazy default path. |
| EW-05 | done | `domain/services/messaging_service.py`, `tests/unit/domain/test_messaging_service.py` | Catch `ClaudeBudgetExceededError`; send exact `SERVICE_UNAVAILABLE_MESSAGE`; return `{"status":"budget_exceeded"}`; no `messages_sent_today` increment. Test proves copy + counter unchanged. |
| EW-06 | done | `domain/services/recommendation_service.py`, `domain/services/education_service.py`, `core/logging.py`, their unit tests, `tests/unit/api/test_routes_logging.py` | Jobs catch budget error, `log_info(... claude daily call budget exceeded)`, return without enqueue. Added `log_info` helper; covered by job mocks + direct logging test. |
| EW-07 | done | `docs/DEPLOYMENT.md`, `docs/operations/PRODUCTION.md`, `docs/threat-model.md`, `docs/decision.md` | Env table for `CLAUDE_DAILY_CALL_BUDGET`; PRODUCTION ops note (logs/Anthropic billing, no PagerDuty); threat-model §4.3 product rate limits + priority item marked implemented; decision.md product bullet + gap note updated for T061 call-count breaker. |
| EW-08 | done | `docs/ROADMAP-TASKS.md`, `docs/COMMERCIAL-LAUNCH.md`, `docs/specs/sdd/T061-global-claude-budget-stop-sdd.md`, `docs/specs/sdd/INDEX.md` | Flipped after EW-01–EW-07 and EW-09 gate: T061 checked, CL #28 checked (T060+T061), SDD `implemented`, INDEX `implemented`. Payments/Asaas untouched. |
| EW-09 | done | whole diff | No T012 algorithm changes; no T060 entitlement math rewrite; no payments ADR/Asaas; no LGPD. Gate commands below pass; domain/core coverage 96.23%. |

## Deviations from the SDD / SPEC

1. `IAService` still imports `ClaudeClient` from infrastructure (pre-existing pattern); budget persistence uses the domain port only.
2. `send_recommendations` still stamps wine `update_content_last_sent` before the generate call (pre-existing order); on budget exceed it returns after that stamp with no fan-out.
3. Handoff files `CONTEXT.md`, `PLAN.md`, `SPEC.md` are orchestrator artifacts (not EW products).

## Files touched

| Path | EW |
|------|----|
| `core/config.py` | EW-01 |
| `tests/unit/core/test_config_and_queues.py` | EW-01 |
| `domain/claude_budget.py` (new) | EW-02 |
| `domain/repositories/claude_budget_repository.py` (new) | EW-02 |
| `tests/unit/domain/test_claude_budget.py` (new) | EW-02 |
| `infrastructure/repositories/datastore_claude_budget_repository.py` (new) | EW-03 |
| `tests/unit/infrastructure/test_datastore_claude_budget_repository.py` (new) | EW-03 |
| `domain/services/ia_service.py` | EW-04 |
| `tests/unit/domain/test_ia_service.py` | EW-04 |
| `domain/services/messaging_service.py` | EW-05 |
| `tests/unit/domain/test_messaging_service.py` | EW-05 |
| `domain/services/recommendation_service.py` | EW-06 |
| `domain/services/education_service.py` | EW-06 |
| `core/logging.py` | EW-06 |
| `tests/unit/domain/test_recommendation_service.py` | EW-06 |
| `tests/unit/domain/test_education_service.py` | EW-06 |
| `tests/unit/api/test_routes_logging.py` | EW-06 |
| `docs/DEPLOYMENT.md` | EW-07 |
| `docs/operations/PRODUCTION.md` | EW-07 |
| `docs/threat-model.md` | EW-07 |
| `docs/decision.md` | EW-07 |
| `docs/ROADMAP-TASKS.md` | EW-08 |
| `docs/COMMERCIAL-LAUNCH.md` | EW-08 |
| `docs/specs/sdd/T061-global-claude-budget-stop-sdd.md` | EW-08 (status; body is orchestrator SDD expand) |
| `docs/specs/sdd/INDEX.md` | EW-08 |
| `docs/specs/sdd/T061-builder-report.md` (new) | this report |
| `CONTEXT.md` | handoff |
| `PLAN.md` | handoff |
| `SPEC.md` | handoff |

Not included: untracked `docs/design/`, `frontend/` (pre-existing, unrelated).

## Test commands and results

Run from the repo root with the repo virtualenv (`.venv`):

| Command | Result |
|---------|--------|
| `PYTHONPATH=. .venv/bin/python -m pytest --override-ini='addopts=' -q` | 217 passed |
| `PYTHONPATH=. .venv/bin/python -m pytest --cov --cov-report=term-missing:skip-covered` | passed; total coverage **96.23%** (`fail_under` 95) |
| `.venv/bin/ruff check api core domain infrastructure tests quality` | All checks passed |
| `.venv/bin/python quality/check_import_style.py` | Import style OK |
