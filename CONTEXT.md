# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T012:** Rate limit **`POST /webhook/whatsapp`** only (COMMERCIAL-LAUNCH #10). In-process sliding window per client IP (router guard) and per sender phone (after valid Twilio signature).

## Acceptance criteria

- [x] Sliding-window limits configurable via env; sensible production defaults documented in DEPLOYMENT + PRODUCTION.
- [x] Excess traffic receives **429** JSON `{"error":"rate_limit_exceeded"}`; valid Twilio traffic under limits unchanged (200 / 403 signature flow preserved).
- [x] Unit tests: under, at, and over limit for limiter + webhook integration.
- [x] Lite spec under `docs/specs/`; T012 and CL #10 marked done.
- [x] pytest, ruff, import style pass locally.

## Decisions

| Topic | Decision |
|-------|----------|
| Scope | Only `/webhook/whatsapp` POST |
| IP limit | Checked in `api/routes.py` before handler |
| Phone limit | Checked in handler after signature validation |
| Store | In-process `SlidingWindowRateLimiter` in `core/rate_limit.py` (per Cloud Run instance; no new deps) |
| Disable | Set `WEBHOOK_RATE_LIMIT_*_MAX=0` to turn off a dimension |
| Defaults | IP: 120/min; phone: 30/min |

## Relevant files

| File | Action |
|------|--------|
| `core/config.py` | Rate limit env vars |
| `core/rate_limit.py` | Sliding window limiter |
| `api/webhook_rate_limit.py` | IP/phone checks + 429 response |
| `api/routes.py` | IP guard for webhook |
| `api/handlers/whatsapp_handler.py` | Phone guard |
| `docs/specs/webhook-rate-limit.md` | Behavior spec |
| `docs/DEPLOYMENT.md`, `docs/operations/PRODUCTION.md` | Env documentation |
| `docs/ROADMAP-TASKS.md`, `docs/COMMERCIAL-LAUNCH.md` | Mark done |

## Git policy (fixed)

- Branch: `cursor/webhook-rate-limit-afd2` → PR to `main`. See [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md).

## Next after T012

**T013** — threat model (CL #12). Then **T020** tier fields (CL #17–18), then **T024** — **product entitlements** in domain + Datastore (plan-based on-demand limits; not a duplicate of T012). Optional follow-up: env-based Claude/Twilio config (remove prod dependency on `config.json`).

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).
