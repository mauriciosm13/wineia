# SPEC — T061 Global Claude budget stop

**Status:** ready for implementation  
**Task:** T061 ([docs/ROADMAP-TASKS.md](docs/ROADMAP-TASKS.md))  
**Branch:** `feat/t061-global-claude-budget`  
**Binding sources:** [CONTEXT.md](CONTEXT.md), [PLAN.md](PLAN.md),
[docs/specs/sdd/T061-global-claude-budget-stop-sdd.md](docs/specs/sdd/T061-global-claude-budget-stop-sdd.md)
(Expected work EW-01–EW-09).

This file is the implementation contract. If it ever disagrees with the SDD
Expected work table, the SDD wins.

## Problem

Per-user IA caps (T024/T060) do not stop fleet-wide Claude spend if many
customers or jobs generate in one UTC day. CL #28 needs a global stop.

## Goals

- Env `CLAUDE_DAILY_CALL_BUDGET`: call-count ceiling per UTC day; `0`/unset =
  unlimited; `> 0` fail-closed before Claude.
- Domain port + Datastore day counter; increment after successful generate.
- Single `IAService` choke point for all generations.
- Jobs log skip and do not fan-out; messaging sends Portuguese unavailable copy.
- Document and mark T061 + CL #28 complete when EW hold.

## Scope

| Slice | EW | Files |
|-------|----|-------|
| Config env parse + tests | EW-01 | `core/config.py`, core unit tests |
| Domain port + helpers + tests | EW-02 | `domain/claude_budget.py`, repository ABC, domain tests |
| Datastore repository | EW-03 | `infrastructure/repositories/datastore_claude_budget_repository.py` |
| IAService choke point | EW-04 | `domain/services/ia_service.py`, IA tests |
| Messaging unavailable | EW-05 | `messaging_service.py`, messaging tests |
| Job skip + log | EW-06 | recommendation + education services/tests |
| Ops / threat / decision docs | EW-07 | DEPLOYMENT, PRODUCTION, threat-model, decision |
| Status flips | EW-08 | ROADMAP-TASKS, COMMERCIAL-LAUNCH #28, SDD, INDEX |
| Diff gate | EW-09 | whole diff |
| Builder report | EW-01–EW-09 | `docs/specs/sdd/T061-builder-report.md` |

## Out of scope

- Payments; LGPD; T004; T012 algorithms; T060 rewrite.
- Monthly/USD budget; PagerDuty; new pip deps.

## Expected behavior (summary)

1. Budget `0` → unlimited; no counter I/O.
2. Budget `N > 0` and today's count `>= N` → `ClaudeBudgetExceededError` before Claude.
3. Successful generate → increment once.
4. Messaging → Portuguese unavailable; no `messages_sent_today` bump.
5. Jobs → log `claude daily call budget exceeded`; no enqueue.

## Acceptance

All EW-01–EW-09 true; builder report written; reviewer judge accepts; pytest +
ruff + import style; domain/core coverage ≥ 95%.
