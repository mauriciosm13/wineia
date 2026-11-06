# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T021** — ENTRY scheduled recommendation cadence **2× per rolling 7 days** (COMMERCIAL-LAUNCH #20). Implementation must follow the Spec-Driven Document [entry-recommendation-cadence-sdd.md](docs/specs/entry-recommendation-cadence-sdd.md). **T020** (`plan_tier`, `weekly_education_opt_in`) is merged — [customer-plan-tier.md](docs/specs/customer-plan-tier.md).

## Acceptance criteria (T021)

- [ ] Behavior matches the SDD: rolling 168h cap for `ENTRY` and `SUPERIOR`; no 24h-only rule for recommendations; decouple from `messages_sent_today` in the recommendation job path.
- [ ] Data model and backfill strategy documented in PR (see SDD options).
- [ ] Unit tests cover SDD acceptance table.
- [ ] Docs: mark T021 + CL #20 when done; update PRODUCTION if customer shape changes.
- [ ] pytest, ruff, import style pass.

## Decisions (T021 — from SDD)

| Topic | Decision |
|-------|----------|
| Source of truth | [entry-recommendation-cadence-sdd.md](docs/specs/entry-recommendation-cadence-sdd.md) |
| Tiers in scope | `ENTRY` and `SUPERIOR` share scheduled cadence; on-demand IA is separate |
| Counter separation | Do not use `messages_sent_today` to gate scheduled recommendations |

## Relevant files

| File | Action |
|------|--------|
| `docs/specs/entry-recommendation-cadence-sdd.md` | SDD (normative) |
| `domain/services/recommendation_service.py` | Primary logic change |
| `domain/models/customer.py` / repository | New fields if Option B (see SDD) |
| `tests/unit/domain/test_recommendation_service.py` | Acceptance tests |

## Git policy (fixed)

- Use readable branch names; avoid random suffixes. If automation requires `cursor/`, use `cursor/<type>-<topic-kebab>`. See [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md#branch-names-preferred).

## Next after T021

**T022** education weekly job; **T023** one Claude per broadcast slot; **T024** domain entitlements.

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).
