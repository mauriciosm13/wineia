# SPEC — T060 Per-tier IA caps (ops-tunable)

**Status:** ready for implementation  
**Task:** T060 ([docs/ROADMAP-TASKS.md](docs/ROADMAP-TASKS.md))  
**Branch:** `feat/t060-per-tier-ia-caps`  
**Binding sources:** [CONTEXT.md](CONTEXT.md), [PLAN.md](PLAN.md),
[docs/specs/sdd/T060-per-tier-ia-caps-sdd.md](docs/specs/sdd/T060-per-tier-ia-caps-sdd.md)
(Expected work EW-01–EW-06).

This file is the implementation contract. If it ever disagrees with the SDD
Expected work table, the SDD wins.

## Problem

T024 hardcodes ENTRY=2 / SUPERIOR=10. Ops cannot tune daily on-demand IA caps
without a deploy of new constants.

## Goals

- Env-tunable caps via `ON_DEMAND_DAILY_LIMIT_ENTRY` /
  `ON_DEMAND_DAILY_LIMIT_SUPERIOR` in `core/config.py`.
- Defaults remain 2 / 10 when unset or invalid.
- `on_demand_entitlements` consumes config; messaging path unchanged.
- Document for operators; mark T060 implemented when EW hold.

## Scope

| Slice | EW | Files |
|-------|----|-------|
| Config env parse + tests | EW-01 | `core/config.py`, core unit tests |
| Domain consume config + tests | EW-02, EW-03 | `domain/on_demand_entitlements.py`, entitlement tests |
| Ops / decision / detail SDD | EW-04 | DEPLOYMENT, PRODUCTION, decision, on-demand-entitlements-sdd |
| Status flips | EW-05 | ROADMAP-TASKS, COMMERCIAL-LAUNCH #28 wording, this SDD, INDEX |
| Diff gate | EW-06 | whole diff |
| Builder report | EW-01–EW-06 | `docs/specs/sdd/T060-builder-report.md` |

## Out of scope

- T061 global budget; T012; T021; payments; LGPD; T004.
- Per-customer Datastore overrides; new pip deps; root `config.py` cleanup.

## Expected behavior (summary)

1. Unset env → ENTRY 2, SUPERIOR 10 (T024 defaults).
2. Set env to valid ints ≥ 0 → those caps apply at runtime.
3. Invalid / negative / empty → fall back to defaults.
4. `can_send_on_demand` uses the configured caps; reset and status rules unchanged.

## Acceptance

All EW-01–EW-06 true; builder report written; reviewer judge accepts; pytest +
ruff + import style; domain/core coverage ≥ 95%.
