# SDD — Global Claude budget stop (T061)

**Status:** implemented  
**Task:** [T061](../../ROADMAP-TASKS.md)  
**Depends on:** T060 (per-user caps remain; this adds a global call ceiling)  
**Comparison contract:** this Expected work list is what the reviewer checks against [T061-builder-report.md](./T061-builder-report.md).

## Problem

Runaway Claude cost if abuse, bugs, or loops fire many generations in one day. Per-user caps (T024/T060) do not bound total fleet spend. COMMERCIAL-LAUNCH #28 still needs a global daily budget stop after T060 delivered ops-tunable per-tier caps.

## Goals

- Cap Claude API **call count** per **UTC calendar day** via env `CLAUDE_DAILY_CALL_BUDGET`.
- Fail closed: when budget `> 0` and today's count is already ≥ budget, do **not** call Claude.
- Single choke point for webhook, scheduled recommendation, weekly education, and `/ia/suggestions`.
- Jobs log an explicit skip reason and do not fan-out text from a missing generation.
- Messaging sends a short Portuguese unavailable message without burning Claude or incrementing the on-demand counter.
- Document ops knobs; mark T061 and CL #28 complete when EW hold.

## Non-goals

- USD / monthly budget tracking; mapping calls→cost in-product (ops do this offline).
- PagerDuty or alerting webhooks (ops watch logs + Anthropic billing).
- T012 webhook IP/phone abuse limit algorithms.
- Rewriting T060 / T024 per-tier caps.
- T040–T043 payments; T004; T050/T051 LGPD.
- New pip dependencies; `docs/MVP_SCOPE.md`.
- Changing Twilio outbound, Cloud Tasks, or Scheduler CD.

## Behavior

### Environment

| Variable | Default | Meaning |
|----------|---------|---------|
| `CLAUDE_DAILY_CALL_BUDGET` | `0` | Max Claude API calls (successful generations) per UTC day. **`0` or unset = unlimited**. |

Parsing (in `core/config.py`): unset, empty, non-integer, or value `< 0` → `0` (unlimited). When value `> 0`, enforce fail-closed.

### Persistence

- Kind: `ClaudeDailyBudget`.
- Entity key name: UTC day `YYYY-MM-DD`.
- Property: `call_count` (int, default 0).
- Accessed only through domain port `ClaudeBudgetRepository` (`get_call_count`, `increment_call_count`). Infrastructure implements with Datastore. Domain must not import the Datastore **client**.

### Enforcement (choke point)

All `IAService.generate_response` / `generate_recommendation` / `generate_weekly_education` paths share one helper that:

1. Reads `CLAUDE_DAILY_CALL_BUDGET` from `core.config`.
2. If budget `<= 0`: call `ClaudeClient.generate` and return (no counter I/O).
3. If budget `> 0`: load today's count; if `count >= budget`, raise `ClaudeBudgetExceededError` **before** Claude.
4. On successful Claude response: `increment_call_count` for today, then return text.
5. Failed Claude calls (exceptions before a successful return) do **not** increment. Empty string responses still count as a successful API round-trip if `generate` returns normally — treat normal return as success for increment.

Accepted residual: concurrent instances may slightly overshoot the budget (increment-after-success).

### Over-budget UX

| Path | Behavior |
|------|----------|
| `process_incoming_message` | Catch `ClaudeBudgetExceededError`; `message_sender` with Portuguese `Desculpe, o serviço está temporariamente indisponível. Tente novamente em breve.`; return `{"status":"budget_exceeded"}`; do **not** increment `messages_sent_today`. |
| `send_recommendations` | Catch; `log_info` skip reason containing `claude daily call budget exceeded`; return without fan-out. |
| `send_weekly_education` | Same as recommendations. |
| `/ia/suggestions` | Same choke point; uncaught domain error is acceptable (no Twilio burn of Claude text). |

## Expected work

The builder implements only these items. The reviewer marks each **match**, **gap**, or **extra**.

| ID | Must be true when the work is done | Where |
|----|-------------------------------------|--------|
| EW-01 | `core/config.py` defines `CLAUDE_DAILY_CALL_BUDGET` from env of the same name, defaulting to `0`. Unset, empty, non-integer, and negative values fall back to `0`. Positive integers are accepted. Unit tests reload config under monkeypatched env and assert defaults + overrides + invalid fallback. | `core/config.py`, `tests/unit/core/test_config_and_queues.py` |
| EW-02 | Domain module `domain/claude_budget.py` defines `ClaudeBudgetExceededError`, `utc_day_key(now=None)` → `YYYY-MM-DD` UTC, `ensure_within_budget(repository, budget, now=None)` (raises when `budget > 0` and `get_call_count(day) >= budget`), and `record_successful_call(repository, now=None)` (increments). Port `domain/repositories/claude_budget_repository.py` ABC with `get_call_count(day_key)` and `increment_call_count(day_key)`. Domain does not import Datastore client or `google.cloud`. Unit tests with an in-memory fake cover allow / deny / increment / unlimited (`budget<=0` never calls repo). | `domain/claude_budget.py`, `domain/repositories/claude_budget_repository.py`, `tests/unit/domain/test_claude_budget.py` |
| EW-03 | `infrastructure/repositories/datastore_claude_budget_repository.py` implements the port: kind `ClaudeDailyBudget`, key = day_key, property `call_count`. `get_call_count` returns 0 when missing; `increment_call_count` creates or updates and returns the new count. No domain import of the Datastore client. | that module (+ thin unit test with fakes/mocks if needed) |
| EW-04 | `IAService` routes every Claude generation through one shared helper that applies EW-02 against `CLAUDE_DAILY_CALL_BUDGET` and an injectable `budget_repository` (default lazy Datastore impl when budget `> 0`). Over budget → raise before `ClaudeClient.generate`. Success → increment after generate returns. Existing IA prompt tests still pass with budget `0`. New tests: budget exceeded skips Claude; success increments once per call. | `domain/services/ia_service.py`, `tests/unit/domain/test_ia_service.py` |
| EW-05 | `process_incoming_message` catches `ClaudeBudgetExceededError`, sends the exact Portuguese unavailable string from Behavior, returns `{"status":"budget_exceeded"}`, does not increment `messages_sent_today`, and does not treat the turn as processed. Unit test proves sender called with that copy and counter unchanged. | `domain/services/messaging_service.py`, `tests/unit/domain/test_messaging_service.py` |
| EW-06 | `send_recommendations` and `send_weekly_education` catch `ClaudeBudgetExceededError` from IA, call `core.logging.log_info` with a message containing `claude daily call budget exceeded`, and return without enqueue fan-out (no `enqueue_send_message`). Unit tests prove no enqueue and that log was invoked. | `domain/services/recommendation_service.py`, `domain/services/education_service.py`, their unit tests |
| EW-07 | Docs: `DEPLOYMENT.md` documents `CLAUDE_DAILY_CALL_BUDGET` (default 0 = unlimited) near other runtime env. `PRODUCTION.md` notes global daily Claude call budget + ops watch logs/Anthropic billing (no PagerDuty). `threat-model.md` §4.3 marks global budget stop implemented (T061). `decision.md` notes global UTC call ceiling via env. | those files |
| EW-08 | Only after EW-01–EW-07 and EW-09 hold: `ROADMAP-TASKS.md` checks T061; this SDD status is `implemented`; `INDEX.md` matches; `COMMERCIAL-LAUNCH.md` item 28 is checked complete (T060 per-user caps + T061 global call budget). Do not touch T040–T043 / Asaas / PR #36. | those files |
| EW-09 | Diff does not change T012 rate-limit algorithms, rewrite T060 entitlement math, payments docs/ADR as decided, or LGPD tasks. Domain/core coverage ≥ 95%. ruff + import style pass. | whole diff |

## Builder report

After implementation, write `docs/specs/sdd/T061-builder-report.md`:

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
- [COMMERCIAL-LAUNCH.md](../../COMMERCIAL-LAUNCH.md) — #28
- [threat-model.md](../../threat-model.md) — §4.3
- [T060-per-tier-ia-caps-sdd.md](./T060-per-tier-ia-caps-sdd.md)
- [on-demand-entitlements-sdd.md](../on-demand-entitlements-sdd.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial stub |
| 2026-11-16 | Expanded to T031-style Expected work EW-01–EW-09 (UTC call-count budget, choke point, job skip, messaging unavailable) |
