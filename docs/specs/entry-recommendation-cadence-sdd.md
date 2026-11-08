# SDD — ENTRY recommendation cadence (T021)

**Status:** implemented (see `domain/recommendation_scheduled_cadence.py`, `domain/services/recommendation_service.py`)  
**Task:** [T021](../ROADMAP-TASKS.md) · COMMERCIAL-LAUNCH [#20](../COMMERCIAL-LAUNCH.md)  
**Depends on:** T020 (`plan_tier`, `weekly_education_opt_in`) — [customer-plan-tier.md](./customer-plan-tier.md)

## Why this document

This is a **Spec-Driven Document (SDD)** for T021: one place for **problem, decisions, behavior, and acceptance tests** before and during implementation.

## Problem

- Product promise: **ENTRY** tier = **2 recommendation (broadcast) messages per week** — [commercial.md](../commercial.md).
- Today `send_recommendations()` uses a **24-hour** minimum interval between sends and a **`messages_sent_today >= 2` skip**, which matches an older “daily” mental model, not 2×/week.

## Goals

1. Enforce **at most two scheduled recommendation sends per customer per rolling 7-day window** for **`plan_tier` in (`ENTRY`, `SUPERIOR`)** (both receive the same scheduled recommendation cadence; SUPERIOR adds on-demand IA elsewhere).
2. **Do not** use `messages_sent_today` to gate the recommendation job (that counter is for **inbound / on-demand** messaging; separating concerns avoids blocking recommendations incorrectly — aligns with [T024](../ROADMAP-TASKS.md) entitlements later).
3. **One shared** Claude generation + fan-out per job invocation — [recommendation-broadcast-slot.md](./recommendation-broadcast-slot.md) (T023).

## Non-goals

- Fixed weekday/time slots (e.g. Mon/Thu) — needs Scheduler/CD alignment (**T031**).
- Education weekly job (**T022**).
- `plan_tier` values beyond `ENTRY` | `SUPERIOR` in this phase.

## Definitions

| Term | Meaning |
|------|---------|
| **Scheduled recommendation send** | A message produced by `send_recommendations()` and enqueued via `enqueue_send_message` for an active customer. |
| **Rolling week** | The **168-hour** interval ending at the instant the job evaluates that customer. |

## Behavior (normative)

### Eligibility

For each **active** customer (`status == active`):

1. If `plan_tier` is missing after normalization, treat as **`ENTRY`** (see [customer-plan-tier.md](./customer-plan-tier.md)).
2. If `plan_tier` is not `ENTRY` or `SUPERIOR`, **skip** (no scheduled recommendation for unknown tiers until explicitly supported).
3. **Count** scheduled sends in the rolling week: any send that counted updates **`last_recommendation_at`**; eligibility requires fewer than **2** sends in the last **168 hours** by comparing timestamps. **Implementation note:** with **at most one send per job run per customer** and a single `last_recommendation_at`, use **`first_recommendation_at_in_period`** or **`recommendation_send_count_7d`** — see §Data model below. **Preferred minimal approach:** store **two timestamps** `recommendation_sent_at_1` and `recommendation_sent_at_2` (last two sends), drop older than 168h when evaluating, skip if two non-expired timestamps exist. **Simpler alternative acceptable for T021:** store **one** `last_recommendation_at` and a **`recommendation_sends_in_window` int** with **`recommendation_window_started_at`**; reset window when `now - window_start >= 168h`; increment on send. Pick one approach in implementation and document in code comments.

4. Remove the **24-hour** rule; replace with the rolling-week rule above.
5. Remove **`messages_sent_today >= 2`** from the recommendation send path.

### After a successful send

- Update persisted fields so the next run enforces the cap.
- Do **not** increment `messages_sent_today` for this path (optional: document in code that recommendation sends are excluded from daily on-demand cap until T024).

### Timezone

- All comparisons use **UTC** (`datetime.now(timezone.utc)`), consistent with existing code. Naive datetimes from legacy data continue to be treated as UTC.

## Data model options (pick one in implementation PR)

| Option | Fields | Pros | Cons |
|--------|--------|------|------|
| **A — Two timestamps** | `rec_sent_1`, `rec_sent_2` (optional second) | Clear, no drift | Two new fields / migration |
| **B — Window + count** | `rec_window_start`, `rec_window_count` | Compact | Slightly more edge-case logic |

Default recommendation for this SDD: **Option B** with namespaced keys, e.g. `recommendation_window_started_at`, `recommendation_send_count_7d`, and keep **`last_recommendation_at`** for ops/debug (last send time).

## API / HTTP

No new routes required unless operators need visibility; **optional** follow-up: expose new fields on GET `/customers` — not required for T021 minimum.

## Tests (acceptance)

| # | Case | Expect |
|---|------|--------|
| 1 | ENTRY, no prior sends | Send |
| 2 | ENTRY, one send 3d ago | Send (second in week) |
| 3 | ENTRY, two sends in last 168h | Skip |
| 4 | ENTRY, one send 8d ago (window rolled) | Send |
| 5 | SUPERIOR, same as ENTRY | Same cadence for scheduled job |
| 6 | Inactive / canceled | Skip |
| 7 | `messages_sent_today == 2` but cadence allows | Still send if within 2/week rule (proves decoupling) |
| 8 | Unknown tier (future value) | Skip |

## Rollout

- Backfill: customers with only `last_recommendation_at` — on first run after deploy, **seed** `recommendation_window_started_at` / count from `last_recommendation_at` or treat as zero sends in current window (document choice; prefer seeding from `last_recommendation_at` to avoid surprise double-send).

## Related

- [ROADMAP.md](../ROADMAP.md) M3 / M1
- [webhook-rate-limit.md](./webhook-rate-limit.md) — abuse limits (orthogonal)
- [threat-model.md](../threat-model.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-06 | Initial SDD |
| 2026-11-06 | Implementation: `send_recommendations(now_utc=None)` optional arg for unit tests only; production uses wall-clock UTC when omitted |
