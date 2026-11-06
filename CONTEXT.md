# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T020:** Add **`plan_tier`** (`ENTRY` | `SUPERIOR`) and **`weekly_education_opt_in`** (bool) to Customer model, Datastore persistence, and HTTP API (create/get/list/update). Maps to COMMERCIAL-LAUNCH #17–18 and [`docs/commercial.md`](docs/commercial.md).

## Acceptance criteria

- [x] `PlanTier` enum validated in domain; `weekly_education_opt_in` is boolean.
- [x] Legacy **`plan`** string field retained; `plan_tier` defaults to **`ENTRY`** for new customers and on read when missing.
- [x] Mapping documented: `plan` = legacy/operator label; commercial tier code is `plan_tier`.
- [x] CRUD API accepts and returns both new fields; PATCH can update them.
- [x] Unit tests: model, service validation, API serialization.
- [x] Lite spec under `docs/specs/`; PRODUCTION.md customer JSON; T020 + CL #17–18 marked done.
- [x] pytest, ruff, import style pass.

## Decisions

| Topic | Decision |
|-------|----------|
| Default tier | `ENTRY` for creates and migration-on-read |
| Legacy `plan` | No auto-inference to SUPERIOR; operators set `plan_tier` via API |
| Backward compat | `normalize_customer_fields()` on every service read |
| T004 | Skipped (branch protection) |

## Relevant files

| File | Action |
|------|--------|
| `domain/models/customer.py` | `PlanTier`, fields, normalize helper |
| `domain/services/customer_service.py` | create/update/validate, normalize on read |
| `api/handlers/customer_handler.py` | POST body fields |
| `docs/specs/customer-plan-tier.md` | New lite spec |
| `docs/operations/PRODUCTION.md` | Customer JSON shape |
| `docs/COMMERCIAL-LAUNCH.md`, `docs/ROADMAP-TASKS.md` | Mark done |

## Git policy (fixed)

- Use readable branch names; avoid random suffixes. If automation requires `cursor/`, use `cursor/<type>-<topic-kebab>`. See [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md#branch-names-preferred).

## Next after T020

**T021** ENTRY cadence 2×/week enforcement (CL #20), or **T024** domain entitlements (depends on T020).

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).
