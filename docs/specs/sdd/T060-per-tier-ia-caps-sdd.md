# SDD — Per-user daily IA turn limit by tier (T060)

**Status:** implemented  
**Task:** [T060](../../ROADMAP-TASKS.md)  
**Depends on:** T024 ([on-demand-entitlements-sdd.md](../on-demand-entitlements-sdd.md))  
**Comparison contract:** this Expected work list is what the reviewer checks against [T060-builder-report.md](./T060-builder-report.md).

## Problem

T024 shipped MVP hardcode-only caps (ENTRY=2 / SUPERIOR=10) in `domain/on_demand_entitlements.py`. Operators cannot tune per-tier daily on-demand IA limits without a code change. COMMERCIAL-LAUNCH #28 still needs ops-tunable caps (global Claude budget remains T061).

## Goals

- Keep T024 defaults (ENTRY=2, SUPERIOR=10) when env is unset.
- Make caps configurable via env (`ON_DEMAND_DAILY_LIMIT_ENTRY`, `ON_DEMAND_DAILY_LIMIT_SUPERIOR`) through `core/config.py`, consumed by `on_demand_entitlements`.
- Document defaults and env vars for ops (PRODUCTION / DEPLOYMENT).
- Unit-test defaults and env overrides; preserve T012 / T021 / messaging paths.

## Non-goals

- T061 global Claude/Twilio budget stop.
- T012 webhook IP/phone abuse limits (algorithms or env).
- T021 entry recommendation cadence.
- T040–T043 payments; T004; T050/T051 LGPD.
- Per-customer Datastore overrides of daily caps.
- New pip dependencies; `docs/MVP_SCOPE.md`.
- Deleting or rewriting unused root `config.py` `ESSENTIAL_DAILY_LIMIT` (legacy, unused — do not invent a second limit system).
- Changing `messaging_service` flow beyond reading updated entitlement caps.

## Behavior

### Defaults (when env unset or invalid)

| `plan_tier` | Max on-demand IA replies / UTC day |
|-------------|-------------------------------------|
| `ENTRY` | 2 |
| `SUPERIOR` | 10 |

Unknown / missing tier → ENTRY default (unchanged from T024).

### Environment variables

| Variable | Default | Meaning |
|----------|---------|---------|
| `ON_DEMAND_DAILY_LIMIT_ENTRY` | `2` | Daily on-demand IA cap for ENTRY |
| `ON_DEMAND_DAILY_LIMIT_SUPERIOR` | `10` | Daily on-demand IA cap for SUPERIOR |

Parsing (in `core/config.py`): unset, empty, non-integer, or value `< 0` → use the default for that tier. `0` is valid (blocks all on-demand sends for that tier).

### Runtime

1. `core/config.py` exposes `ON_DEMAND_DAILY_LIMIT_ENTRY` and `ON_DEMAND_DAILY_LIMIT_SUPERIOR` (ints).
2. `on_demand_daily_limit(plan_tier)` reads those config values (via `core.config` module attributes at call time), not a hardcode-only map as the sole source when env is set.
3. `can_send_on_demand` / `messaging_service.can_send_message` keep existing semantics; only the numeric caps change with config.
4. Daily UTC read-path reset unchanged.

## Expected work

The builder implements only these items. The reviewer marks each **match**, **gap**, or **extra**.

| ID | Must be true when the work is done | Where |
|----|-------------------------------------|--------|
| EW-01 | `core/config.py` defines `ON_DEMAND_DAILY_LIMIT_ENTRY` and `ON_DEMAND_DAILY_LIMIT_SUPERIOR` from env of the same names, defaulting to `2` and `10`. Unset, empty, non-integer, and negative values fall back to those defaults. Zero is accepted. Unit tests reload config under monkeypatched env and assert defaults + overrides + invalid fallback. | `core/config.py`, `tests/unit/core/test_config_and_queues.py` (or dedicated config test module) |
| EW-02 | `on_demand_daily_limit` / `can_send_on_demand` consume `core.config` limits (not a private hardcode-only dict as the sole source). With env unset, ENTRY=2 and SUPERIOR=10. With env overrides (e.g. ENTRY=5, SUPERIOR=20), `can_send_on_demand` allows/blocks at the new caps. Domain does not import infrastructure. | `domain/on_demand_entitlements.py`, `tests/unit/domain/test_on_demand_entitlements.py` |
| EW-03 | Existing entitlement behaviors preserved: UTC day reset, inactive customers blocked, unknown tier → ENTRY default. `messaging_service` still gates via `can_send_on_demand` (no parallel limit system). | entitlements + messaging tests (existing or thin updates) |
| EW-04 | Docs: `DEPLOYMENT.md` documents the two env vars + defaults in the runtime env table (near webhook rate-limit env). `PRODUCTION.md` notes ops-tunable per-tier on-demand caps and points at T060 / entitlements SDD. `decision.md` product bullet notes caps are env-tunable via `core/config` (defaults 2/10). Detail spec `on-demand-entitlements-sdd.md` records env override path. | those files |
| EW-05 | Only after EW-01–EW-04 and EW-06 hold: `ROADMAP-TASKS.md` checks T060; this SDD status is `implemented`; `INDEX.md` matches; `COMMERCIAL-LAUNCH.md` item 28 is updated to reflect per-user ops-tunable caps delivered (T060) while leaving global daily budget to T061 (item may stay unchecked with clarified wording, or note partial). Do not check T061. Do not touch T040–T043 / Asaas / PR #36. | those files |
| EW-06 | Diff does not change T012 rate-limit algorithms, T021 cadence modules, T061, payments docs/ADR as decided, or LGPD tasks. Root `config.py` `ESSENTIAL_DAILY_LIMIT` left alone (unused legacy). Domain/core coverage ≥ 95%. ruff + import style pass. | whole diff |

## Builder report

After implementation, write `docs/specs/sdd/T060-builder-report.md`:

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
- [on-demand-entitlements-sdd.md](../on-demand-entitlements-sdd.md)
- [COMMERCIAL-LAUNCH.md](../../COMMERCIAL-LAUNCH.md) — #28
- [T024-on-demand-entitlements-sdd.md](./T024-on-demand-entitlements-sdd.md)
- [T061-global-claude-budget-stop-sdd.md](./T061-global-claude-budget-stop-sdd.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial stub |
| 2026-11-15 | Expanded to T031-style Expected work EW-01–EW-06 (env-tunable caps on T024 defaults) |
