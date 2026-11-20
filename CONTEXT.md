# CONTEXT — WineAI (wineia)

## Primary objective (this run)

**Launch waitlist (pré-lista)** so the frontend can POST leads; ops later send discounted Asaas links.

| Order | Task | Focus | Status |
|-------|------|--------|--------|
| 0 | **T085** | Epic | draft SDD on `main` |
| 1 | **T086** | Domain model + Datastore `WaitlistLead` + age validation | **THIS RUN** |
| 2 | **T087** | Public `POST /waitlist` + rate limit + privacy notice | **THIS RUN** |
| 3 | **T088** | Operator GET/export + discount-link runbook | **THIS RUN** (same PR) |

Epic: [`docs/specs/sdd/T085-launch-waitlist-sdd.md`](docs/specs/sdd/T085-launch-waitlist-sdd.md)  
Slices: T086 · T087 · T088 SDDs under `docs/specs/sdd/`

## Fields (required)

- WhatsApp `phone` (E.164 normalize)
- `name`
- `email` (lower-case)
- `birth_date` (ISO date; min age default **18**, env `WAITLIST_MIN_AGE`)
- `created_at` / `updated_at` (ISO)

## Decisions locked

| Topic | Decision |
|-------|----------|
| Public create | **No** `JOB_INTERNAL_SECRET` on POST |
| Distinct from | Operator `POST /customers/pre-sale` (keep both) |
| Path | `POST /waitlist` public; operator `GET /waitlist` with job secret |
| Upsert key | **Phone** (E.164) as unique key / Datastore entity id; email updated on upsert |
| Rate limit | IP-based `WAITLIST_RATE_LIMIT_IP_MAX` / `WAITLIST_RATE_LIMIT_IP_WINDOW_SECONDS` (reuse SlidingWindowRateLimiter) |
| Privacy | T050-style `privacy_terms_notice` on success using `PRIVACY_POLICY_URL` / `TERMS_OF_SERVICE_URL` |
| Architecture | Handler thin → domain service → repository interface; Datastore impl in infrastructure |
| Validation messages | Portuguese for user-facing errors |
| Git | Branch `cursor/t085-launch-waitlist-afd2` from `main`; never commit to `main`; Conventional Commits EN |
| Tests | Unit tests + fakes; no Datastore emulator; import style one-line; ruff |

## Key files (expected)

| Area | Paths |
|------|--------|
| Domain | `domain/models/waitlist_lead.py`, `domain/repositories/waitlist_repository.py`, `domain/services/waitlist_service.py`, `domain/phone.py` (normalize) |
| Infra | `infrastructure/repositories/datastore_waitlist_repository.py` |
| API | `api/handlers/waitlist_handler.py`, `api/waitlist_rate_limit.py`, `api/routes.py`, `api/internal_job_auth.py` |
| Config | `core/config.py` (`WAITLIST_MIN_AGE`, rate-limit envs) |
| Tests | `tests/fakes/repositories.py`, `tests/unit/domain/test_waitlist_*`, `tests/unit/api/test_waitlist_*` |
| Docs | `PRODUCTION.md`, `ROADMAP-TASKS.md`, SDD INDEX + statuses, ops runbook, DATA-RETENTION |

## Priority / skip

| Item | Action |
|------|--------|
| Payments T040–T044 | Do not implement |
| Asaas checkout send automation | Out of scope (T088 docs/manual OK) |
| Frontend HTML in this run | Out of scope — API only so front can wire later |

## Acceptance criteria

- [x] Waitlist lead persisted with required fields + age gate
- [x] `POST /waitlist` works without job secret; validation errors in Portuguese
- [x] Rate limit on public POST
- [x] `GET /waitlist` operator-only with job secret + short ops note
- [x] PRODUCTION.md / ROADMAP-TASKS / INDEX updated (T085–T088)
- [x] pytest + import-style green; push branch (ManagePullRequest unavailable — parent opens PR)

## Out of scope

- Removing Claude client
- Payment webhooks
- Asking for secrets in chat
- Untracked `frontend/` / `docs/design/` (not part of this API PR)
