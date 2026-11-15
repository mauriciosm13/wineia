# Builder report — T060 Per-tier IA caps (ops-tunable)

**SDD:** [T060-per-tier-ia-caps-sdd.md](./T060-per-tier-ia-caps-sdd.md)  
**Branch:** `feat/t060-per-tier-ia-caps`  
**Date:** 2026-11-15

## Expected work

| ID | Result | Files | What changed |
|----|--------|-------|--------------|
| EW-01 | done | `core/config.py`, `tests/unit/core/test_config_and_queues.py` | Added `DEFAULT_ON_DEMAND_DAILY_LIMIT_ENTRY/SUPERIOR` (2/10) and `_non_negative_int_env`. Exposed `ON_DEMAND_DAILY_LIMIT_ENTRY` / `ON_DEMAND_DAILY_LIMIT_SUPERIOR` from env of the same names. Unset, empty, non-integer, negative → defaults; `0` accepted. Tests: defaults when unset, override 5/20, zero allowed, invalid/empty/negative fall back. Autouse fixture reloads defaults after each test. |
| EW-02 | done | `domain/on_demand_entitlements.py`, `tests/unit/domain/test_on_demand_entitlements.py` | Removed hardcode-only `ON_DEMAND_DAILY_LIMIT_BY_TIER` as sole source. `on_demand_daily_limit` reads `core.config` at call time (ENTRY → ENTRY limit, SUPERIOR → SUPERIOR limit; unknown → ENTRY). Domain imports `core.config` only (no infrastructure). Tests: defaults 2/10; env override 5/20 on `on_demand_daily_limit`; `can_send_on_demand` respects ENTRY=1 / SUPERIOR=3 caps. |
| EW-03 | done | same entitlement tests; existing `tests/unit/domain/test_messaging_service.py` (unchanged, still green) | UTC day reset, inactive blocked, unknown tier → ENTRY default preserved. Messaging still gates via `can_send_on_demand` / `can_send_message` (no parallel limit system). |
| EW-04 | done | `docs/DEPLOYMENT.md`, `docs/operations/PRODUCTION.md`, `docs/decision.md`, `docs/specs/on-demand-entitlements-sdd.md` | DEPLOYMENT: new "On-demand IA daily caps" env table. PRODUCTION: webhook row notes defaults + env names + T060 link. decision.md: env-tunable via core/config; T061 called out. Detail entitlements SDD: env override path + T060 link. |
| EW-05 | done | `docs/ROADMAP-TASKS.md`, `docs/COMMERCIAL-LAUNCH.md`, `docs/specs/sdd/T060-per-tier-ia-caps-sdd.md`, `docs/specs/sdd/INDEX.md` | Flipped only after EW-01–EW-04 and EW-06 gate: T060 checked; CL #28 wording notes T060 caps done and T061 budget remaining (checkbox left unchecked); SDD status `implemented`; INDEX `implemented`. No T061 / payments / Asaas / PR #36 changes. |
| EW-06 | done | whole diff | Diff does not touch T012 rate-limit modules/algorithms, T021 cadence, T061 SDD, payments ADR, LGPD, or root `config.py` `ESSENTIAL_DAILY_LIMIT`. Gate commands below pass; domain/core coverage 95.61%. |

## Deviations from the SDD / SPEC

None material. Handoff files `CONTEXT.md`, `PLAN.md`, `SPEC.md` are orchestrator artifacts (same pattern as T031/T032), not Expected work products.

## Files touched

Handoff (not Expected work products): `CONTEXT.md`, `PLAN.md`, `SPEC.md`.

| Path | EW |
|------|----|
| `core/config.py` | EW-01 |
| `tests/unit/core/test_config_and_queues.py` | EW-01 |
| `domain/on_demand_entitlements.py` | EW-02, EW-03 |
| `tests/unit/domain/test_on_demand_entitlements.py` | EW-02, EW-03 |
| `docs/DEPLOYMENT.md` | EW-04 |
| `docs/operations/PRODUCTION.md` | EW-04 |
| `docs/decision.md` | EW-04 |
| `docs/specs/on-demand-entitlements-sdd.md` | EW-04 |
| `docs/ROADMAP-TASKS.md` | EW-05 |
| `docs/COMMERCIAL-LAUNCH.md` | EW-05 |
| `docs/specs/sdd/T060-per-tier-ia-caps-sdd.md` | EW-05 (status; body is SDD expansion) |
| `docs/specs/sdd/INDEX.md` | EW-05 |
| `docs/specs/sdd/T060-builder-report.md` (new) | this report |

## Test commands and results

Run from the repo root with `.venv`:

| Command | Result |
|---------|--------|
| `PYTHONPATH=. .venv/bin/python -m pytest` | **195 passed**, 23 warnings |
| `PYTHONPATH=. .venv/bin/python -m pytest --cov --cov-report=term-missing` | 195 passed; total coverage **95.61%** (`fail_under` 95); `core/config.py` 100%; `domain/on_demand_entitlements.py` 100% |
| `.venv/bin/ruff check api core domain infrastructure tests quality` | All checks passed |
| `.venv/bin/python quality/check_import_style.py` | Import style OK |
