# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T011:** Document a **Secret Manager migration plan** for production secrets (COMMERCIAL-LAUNCH #8). No runtime or deploy workflow code changes in this task.

## Acceptance criteria

- [x] Inventory maps every **sensitive** runtime value to a proposed Secret Manager secret id and Cloud Run env var name.
- [x] Runbook covers: create secrets, IAM for Cloud Run runtime SA, mount secrets on `wine-concierge`, Scheduler/Tasks header secret, verification, rollback.
- [x] ADR records the decision (Secret Manager + Cloud Run secret refs; defer in-app SDK until optional later phase).
- [x] `docs/DEPLOYMENT.md` and `docs/operations/PRODUCTION.md` link to the runbook.
- [x] T011 and COMMERCIAL-LAUNCH item **8** marked done in checklist docs.
- [x] No breaking runtime change; existing env/`config.json` local dev path unchanged.

## Decisions

| Topic | Decision |
|-------|----------|
| Secret storage | Google Secret Manager in project `wineia-490200` |
| Cloud Run integration | `--set-secrets` / console “Reference a secret” → env vars (same names as today) |
| `config.json` | Production must not rely on baked-in `config.json`; migrate Anthropic/Twilio fields to env + secrets (code change deferred to post-plan task) |
| Naming | `wine-concierge/<ENV_VAR_NAME>` (lowercase slug) e.g. `wine-concierge/twilio-auth-token` |
| Local dev | Keep gitignored `config.example.json` → `config.json`; no Secret Manager required locally |

## Relevant files

| File | Action |
|------|--------|
| `docs/operations/SECRET-MANAGER-MIGRATION.md` | New runbook + mapping |
| `docs/adrs/0004-secret-manager-runtime-secrets.md` | New ADR |
| `docs/DEPLOYMENT.md` | Link to runbook |
| `docs/operations/PRODUCTION.md` | Link to runbook |
| `docs/ROADMAP-TASKS.md` | Mark T011 done |
| `docs/COMMERCIAL-LAUNCH.md` | Mark #8 done (plan + runbook) |

## Git policy (fixed)

- Branch: `cursor/secret-manager-plan-afd2` → PR to `main`. See [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md).

## Next after T011

**T012** — Rate limit webhook (CL #10), or **T020** tier fields (CL #17–18). Optional follow-up: implement env-based Claude/Twilio config (remove prod dependency on `config.json`).

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).
