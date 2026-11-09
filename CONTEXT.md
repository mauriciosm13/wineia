# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T030** — Implement **`POST /workers/send-campaign`** for queue `wine-campaigns`. **Normative spec:** [`docs/specs/send-campaign-worker-sdd.md`](docs/specs/send-campaign-worker-sdd.md).

## Acceptance criteria (T030)

- [ ] Worker matches SDD HTTP contract and auth.
- [ ] Twilio send via existing client pattern; 200/400 responses per SDD table.
- [ ] Unit tests cover SDD acceptance checklist.
- [ ] PRODUCTION route table; T030 + CL #26; SDD status **implemented**.
- [ ] pytest, ruff, import style; domain/core coverage ≥ 95% if code touched.

## Decisions (T030 — from SDD)

| Topic | Decision |
|-------|----------|
| Scope | Worker endpoint only; no new job enqueue in T030 |
| Payload | `{phone, message}` parity with `send-message` worker |
| Handler location | Extend `worker_handler` or sibling; thin HTTP layer |

## Git policy (fixed)

SDD branch: `feat/sdd-send-campaign-worker`. Implementation branch: `feat/implement-send-campaign-worker` (no `cursor/` unless automation requires). See [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md#branch-names-preferred).

## Next after T030

**T031** Scheduler/CD queues; **T032** async webhook replies; merge **T024** (`feat/tier-on-demand-entitlements`) if not on `main`.

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).
