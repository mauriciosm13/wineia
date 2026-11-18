# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T051** — Export/delete tooling (COMMERCIAL-LAUNCH #62). Operator-facing HTTP under the existing customer API (same auth model as `/customers`: no app auth — internal/operator only) to export customer PII as JSON and anonymize (erase) a customer by phone, with an ops runbook.

The comparison contract is [`docs/specs/sdd/T051-export-delete-tooling-sdd.md`](docs/specs/sdd/T051-export-delete-tooling-sdd.md). Its **Expected work** list (EW-01…) is what the reviewer checks against the builder report. Do not add behavior that list does not name. On conflict, the SDD Expected work table wins over PLAN.md / SPEC.md.

**Parallel note:** Do **not** own T070 (parallel agent). Do **not** implement T040–T043 or T004. If touching `docs/ROADMAP-TASKS.md`, `docs/specs/sdd/INDEX.md`, or `docs/COMMERCIAL-LAUNCH.md`, change **only the T051 / #62 line/row**. Updating `PRODUCTION.md` for the new routes in this PR is required and helps T070.

## Priority / skip (parent, 2026-11-18)

| Item | Action |
|------|--------|
| **T040–T043** (payments) | **Parked.** Do not work. |
| **T004** | Skip (GitHub admin). |
| **T070** | Do **not** own (parallel agent). |
| **This run** | **T051** only. |

## Decisions already made (parent defaults, 2026-11-18)

| Topic | Decision |
|-------|----------|
| Auth / surface | Operator-facing HTTP under existing customer API auth model (no app auth — document as internal/operator only, like `/customers`). Prefer customer paths, not `/jobs` (job internal secret not required). Document unauthenticated risk in PRODUCTION + runbook. |
| Export | `GET /customers/{phone}/export` → JSON dump of customer PII fields: phone, name, email if any (via linked pre-sale), preferences, plan_tier, consent fields, counters — no secrets. |
| Erase | `POST /customers/{phone}/erase` → **anonymize** (not hard-delete of all history): clear name/preferences/email-like fields; set status `canceled`; keep phone key; display fields use `REDACTED` where applicable. Document that recommendation history / financial records (when they exist) are not hard-deleted without policy. For now anonymize customer + remove/anonymize pre-sale if present. |
| Layering | Domain service owns export/erase rules; handlers thin; Datastore repos via existing patterns. |
| Ops | New runbook `docs/operations/LGPD-EXPORT-DELETE.md` + link from PRODUCTION + CL #62. |
| Tests | Unit tests with fakes. Coverage ≥ 95% if code; ruff + import style. |
| Out of scope | No payment code. No T070 PR template ownership beyond leaving PRODUCTION accurate for new paths. |
| Git | English Conventional Commits; never `main`. Branch: `feat/t051-export-delete-tooling` (**no** `cursor/` prefix). |

## Decisions made by the orchestrator

| Topic | Decision |
|-------|----------|
| Erase verb | `POST /customers/{phone}/erase` (not `DELETE`) — safer on an unauthenticated operator surface. |
| Domain module | New `domain/services/customer_privacy_service.py` owns export payload shape and erase/anonymize rules; `CustomerService` / pre-sale create-activate stay unchanged for normal CRUD. |
| Pre-sale link | Lookup pre-sale by `whatsapp == phone` via new repository method `get_by_whatsapp`. |
| Pre-sale on erase | Delete the pre-sale entity when found (lead key is email; leaving a REDACTED row would retain the email Datastore key). Customer row is anonymized in place (phone key kept). Not hard-delete of recommendation history or future financial records. |
| REDACTED | Customer `name` → `"REDACTED"`; `preferences` → `[]`; consent fields → `None`; `weekly_education_opt_in` → `False`; `status` → `canceled`. Phone and operational counters/plan_tier retained on the customer entity. |
| Export 404 | Missing customer → 404. Pre-sale-only leads are not exported via this path. |
| Handlers | Extend `api/handlers/customer_handler.py` routing for `/export` and `/erase` suffixes; thin parse/respond only. |
| CL #62 | Check complete when EW hold; touch only #62 in COMMERCIAL-LAUNCH. |

## Out of scope

- T040–T043 payments / provider choice.
- T004 GitHub admin.
- T070 ownership (may update PRODUCTION routes only as needed for T051).
- Hard-delete of recommendation history or financial records.
- App auth / OIDC / job-internal-secret on these paths.
- New pip dependencies.

## Relevant files

| File | Role |
|------|------|
| `docs/specs/sdd/T051-export-delete-tooling-sdd.md` | Stub → expand to T031-style with Expected work EW-xx |
| `docs/specs/sdd/T031-scheduler-deploy-cd-sdd.md` | Template for SDD + EW style |
| `docs/specs/sdd/T031-builder-report.md` | Template for builder report |
| `domain/services/customer_privacy_service.py` | Export + erase rules (new) |
| `domain/repositories/pre_sale_customer_repository.py` | Add `get_by_whatsapp` (+ `delete` if needed) |
| `infrastructure/repositories/datastore_pre_sale_customer_repository.py` | Datastore impl |
| `tests/fakes/repositories.py` | Fake pre-sale methods |
| `api/handlers/customer_handler.py` | Routes for export/erase |
| `docs/operations/LGPD-EXPORT-DELETE.md` | Ops runbook (new) |
| `docs/operations/PRODUCTION.md` | Routes + link to runbook |
| `docs/COMMERCIAL-LAUNCH.md` | Item #62 only |
| `docs/ROADMAP-TASKS.md`, `docs/specs/sdd/INDEX.md` | T051 status only |
| `PLAN.md`, `SPEC.md` | Plan/spec updates for T051 |
| `docs/specs/sdd/T051-builder-report.md` | Builder report for reviewer judge |

## Acceptance criteria

See EW-01… in the SDD. In short:

- [ ] `GET /customers/{phone}/export` returns JSON PII dump (no secrets); 404 if missing customer.
- [ ] `POST /customers/{phone}/erase` anonymizes customer (REDACTED / canceled) and removes linked pre-sale if present; does not hard-delete recommendation/financial history.
- [ ] Domain owns rules; handlers thin; unit tests with fakes; coverage ≥ 95%; ruff + import style.
- [ ] Ops runbook `LGPD-EXPORT-DELETE.md` + PRODUCTION link; document unauthenticated operator risk.
- [ ] No payments / T070 ownership / T004; ROADMAP-TASKS / INDEX / CL touch **only** T051 / #62.
- [ ] Builder report + reviewer judge accept (each EW vs change list AND diff → match|gap|extra).

## Git policy (fixed)

Branch: `feat/t051-export-delete-tooling` from `origin/main` (no `cursor/` prefix — see [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md)). **Never push to `main`.** Conventional Commits, English, lowercase subject. Parent creates the GitHub PR when ManagePullRequest is parent-owned; this agent still commits and pushes the branch. Commit bodies wrap at 72 characters (commitlint `body-max-line-length` is 100).

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).

Builder report path: `docs/specs/sdd/T051-builder-report.md` (one row per Expected work ID, files, done or skipped, plus Files touched). The reviewer reads that file, the SDD, and the diff, and is the judge. The reviewer does not edit any file.
