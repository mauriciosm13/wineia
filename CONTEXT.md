# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T023** — One Claude call per recommendation **broadcast slot** + fan-out. Maps to COMMERCIAL-LAUNCH #24 and [`docs/commercial.md`](docs/commercial.md) shared-copy rules.

**T022** is merged on `main`. **T021** cadence unchanged.

## Acceptance criteria (T023)

- [x] `send_recommendations()`: `select_wine` then **one** `generate_recommendation(wine)` per job (no per-customer preferences for broadcast).
- [x] Same message body enqueued to every cadence/tier-eligible customer; state persisted per recipient as today.
- [x] Unit tests: `generate_recommendation` called once per job with N eligibles; same body enqueued N times.
- [x] Lite spec `docs/specs/recommendation-broadcast-slot.md`; PRODUCTION.md; T023 + CL #24 marked done.
- [x] pytest, ruff, import style pass; domain/core coverage ≥ 95%.

## Decisions (T023)

| Topic | Decision |
|-------|----------|
| Preferences | Omit for scheduled broadcast (match `education_service` shared-copy pattern) |
| Cadence / tier | Unchanged from T021 (`should_send_scheduled_recommendation`, ENTRY/SUPERIOR) |
| Claude calls | Exactly one per `/jobs/send-recommendations` invocation |

## Relevant files

| File | Action |
|------|--------|
| `domain/services/recommendation_service.py` | Move `generate_recommendation` before fan-out loop |
| `docs/specs/recommendation-broadcast-slot.md` | Lite spec (new) |
| `tests/unit/domain/test_recommendation_service.py` | One-call + N-enqueue tests |
| `docs/COMMERCIAL-LAUNCH.md` | Mark #24 |
| `docs/ROADMAP-TASKS.md` | Mark T023 |
| `docs/operations/PRODUCTION.md` | Note shared copy |

## Git policy (fixed)

Branch: `cursor/feat-one-claude-broadcast-slot` from `origin/main`. See [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md#branch-names-preferred).

## Next after T023

**T024** domain entitlements.

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).
