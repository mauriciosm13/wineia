# PLAN — T061 Global Claude budget stop

Source of truth: `CONTEXT.md` and Expected work EW-01–EW-09 in
`docs/specs/sdd/T061-global-claude-budget-stop-sdd.md`. On conflict, the SDD
Expected work table wins.

Branch: `feat/t061-global-claude-budget` from `origin/main` (no `cursor/`
prefix).

`PLAN.md` is this handoff. It is not an Expected work product.

## Order

| # | Task | EW | Depends on |
|---|------|----|------------|
| 1 | Config: `CLAUDE_DAILY_CALL_BUDGET` parse + tests | EW-01 | — |
| 2 | Domain port + budget helpers + tests | EW-02 | — |
| 3 | Datastore repository implementation | EW-03 | 2 |
| 4 | IAService choke point + tests | EW-04 | 1, 2, 3 |
| 5 | Messaging unavailable path + tests | EW-05 | 4 |
| 6 | Jobs skip + log + tests | EW-06 | 4 |
| 7 | Ops / threat-model / decision docs | EW-07 | 4–6 |
| 8 | Diff and coverage gate | EW-09 | 1–7 |
| 9 | Status flips (T061, INDEX, CL #28) | EW-08 | 8 |
| 10 | Builder report | EW-01–EW-09 | 9 |

## Tasks

### 1. Config (EW-01)

Files: `core/config.py`, `tests/unit/core/test_config_and_queues.py`.

- Add `CLAUDE_DAILY_CALL_BUDGET` (default 0).
- Invalid / negative / empty → 0; positive ints accepted.

### 2–3. Domain + infrastructure (EW-02, EW-03)

- `domain/claude_budget.py`, `domain/repositories/claude_budget_repository.py`.
- `infrastructure/repositories/datastore_claude_budget_repository.py`.
- In-memory fake tests for domain; mock/fake for infra as needed.

### 4–6. Choke point, messaging, jobs (EW-04–EW-06)

- Shared helper in `IAService`; injectable budget repo.
- Messaging PT unavailable; jobs `log_info` skip + no fan-out.

### 7–10. Docs, gate, status, report

- DEPLOYMENT / PRODUCTION / threat-model / decision.
- pytest, ruff, import style; domain/core coverage ≥ 95%.
- Flip T061 / SDD / INDEX; check CL #28 complete.
- Write `docs/specs/sdd/T061-builder-report.md`.

## Out of scope (do not do)

Payments T040–T043; T004; T050/T051; T012 algorithms; T060 rewrite;
monthly/USD budget; PagerDuty; new pip deps.
