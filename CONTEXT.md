# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**Documentation port:** commercial tiers, payment gate, operations runbooks, and agent git policy (from wine-concierge planning work), **adapted to this repo** (Twilio, Claude, existing M0–M5).

**Next implementer focus:** see open items in `docs/ROADMAP-TASKS.md` — likely **payment provider (#53)**, **tier cadence 2×/week**, **education add-on**, **M5** (`/workers/send-campaign`, Scheduler in CD).

## Git policy (fixed)

- **No direct commits to `main`** — feature branch + PR only. See [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md) and [`.cursor/rules/no-direct-main.mdc`](.cursor/rules/no-direct-main.mdc).

## Product decisions (commercial — owner confirmed)

| Code | Offering |
|------|-----------|
| `ENTRY` | Recommendation messages **2× per week** (evolve from current daily/weekly job semantics) |
| `SUPERIOR` | Entry + **on-demand AI** in WhatsApp for wine choices (Gastón / `ia_service`) |
| `weekly_education_opt_in` | Optional **1 didactic message / week** (opt-in) |
| Copy language | **Portuguese** |
| Batch AI cost | One generation **per send slot**, shared text to all eligible customers when broadcasting |
| Payment API | **TBD** — evaluate in [`docs/payments-evaluation.md`](docs/payments-evaluation.md); CNPJ available |
| Job/worker auth | Recommend `JOB_INTERNAL_SECRET` header (document in ops) |

## Engineering baseline (already in repo)

- CI: pytest, ruff, coverage, import style; Docker build; conventional commits; deploy via tag/OIDC ([`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md))
- Twilio webhook + signature validation; Claude recommendations; Cloud Tasks partial wiring

## Production truth

[`docs/operations/PRODUCTION.md`](docs/operations/PRODUCTION.md) — update in the same PR when runtime behavior changes.

## Agent handoff

Orchestrator updates this file when priority shifts. On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).
