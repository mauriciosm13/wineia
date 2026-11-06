# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T021** — ENTRY/SUPERIOR scheduled recommendation cadence (**max 2 sends / rolling 168h**), decoupled from `messages_sent_today`. Normative: [`docs/specs/entry-recommendation-cadence-sdd.md`](docs/specs/entry-recommendation-cadence-sdd.md). Implementation: `domain/recommendation_scheduled_cadence.py`, `domain/services/recommendation_service.py`.

## Acceptance criteria (T021)

- [x] Rolling 168h cap for `ENTRY` and `SUPERIOR`; 24h rule and `messages_sent_today` gating removed from recommendation job; scheduled sends do not increment `messages_sent_today`.
- [x] Option B fields: `recommendation_window_started_at`, `recommendation_send_count_7d`, keep `last_recommendation_at`; legacy backfill from `last_recommendation_at` on first evaluation (see module docstring).
- [x] Unit tests map to SDD acceptance table rows.
- [x] Docs: T021, CL #20, PRODUCTION, SDD status **implemented**; pytest, ruff, import style.

## Decisions (T021 — from SDD)

| Topic | Decision |
|-------|----------|
| Source of truth | [entry-recommendation-cadence-sdd.md](docs/specs/entry-recommendation-cadence-sdd.md) |
| Tiers in scope | `ENTRY` and `SUPERIOR` share scheduled cadence |
| Data model | Option B: window + count + `last_recommendation_at` |
| Counter separation | `messages_sent_today` not used for scheduled recommendations |

## Relevant files

| File | Role |
|------|------|
| `docs/specs/entry-recommendation-cadence-sdd.md` | SDD |
| `domain/recommendation_scheduled_cadence.py` | Rolling-window logic |
| `domain/services/recommendation_service.py` | Job loop |
| `domain/models/customer.py` | New fields on `Customer.to_dict()` |
| `tests/unit/domain/test_recommendation_service.py` | Acceptance tests |

## Git policy (fixed)

- Use readable branch names; avoid random suffixes. If automation requires `cursor/`, use `cursor/<type>-<topic-kebab>`. See [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md#branch-names-preferred).

## Next after T021

**T022** education weekly job; **T023** one Claude per broadcast slot; **T024** domain entitlements.

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).
