# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T013:** **`docs/threat-model.md`** (COMMERCIAL-LAUNCH #12). Documentation only — no runtime changes.

## Acceptance criteria

- [x] `docs/threat-model.md` covers: WhatsApp webhook abuse, forged job/worker calls, LLM prompt injection / exfil, secrets + trust boundaries (api / domain / infra).
- [x] Mitigations reference existing or planned controls: T010, T011, T012, T024 entitlements, related CL items.
- [x] Linked from `COMMERCIAL-LAUNCH.md`, `docs/operations/PRODUCTION.md`, and `docs/DEPLOYMENT.md`.
- [x] T013 and COMMERCIAL-LAUNCH item **12** marked done in checklist docs.
- [x] No runtime code changes.

## Decisions

| Topic | Decision |
|-------|----------|
| Scope | STRIDE-lite tables + architecture diagram in `docs/threat-model.md` |
| Unauthenticated APIs | Documented as residual risk (`/customers`, `/ia/suggestions`) |

## Relevant files

| File | Action |
|------|--------|
| `docs/threat-model.md` | Created |
| `docs/COMMERCIAL-LAUNCH.md` | #12 done + link |
| `docs/ROADMAP-TASKS.md` | T013 done |
| `docs/operations/PRODUCTION.md` | Security section + link |
| `docs/DEPLOYMENT.md` | Threat model pointer |

## Git policy (fixed)

- Branch: `cursor/threat-model-afd2` → PR to `main`. See [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md).

## Next after T013

**T020** tier fields (CL #17–18), then **T024** product entitlements. **CL #11** IAM least privilege (optional doc). Optional follow-up: env-based Claude/Twilio config (remove prod dependency on `config.json`).

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md). Security: [threat-model.md](docs/threat-model.md), [SECRET-MANAGER-MIGRATION.md](docs/operations/SECRET-MANAGER-MIGRATION.md).
