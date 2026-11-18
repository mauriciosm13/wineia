# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T072** — Operator API authentication (launch blocker from threat-model / `decision.md`). Protect operator HTTP surfaces with the **same** `JOB_INTERNAL_SECRET` + header `X-Job-Internal-Secret`, reusing `api/internal_job_auth.py` patterns. Fail closed if the secret is unset (same as jobs/workers).

The comparison contract is [`docs/specs/sdd/T072-operator-api-auth-sdd.md`](docs/specs/sdd/T072-operator-api-auth-sdd.md). Its **Expected work** list (EW-01…) is what the reviewer checks against the builder report. Do not add behavior that list does not name. On conflict, the SDD Expected work table wins over PLAN.md / SPEC.md.

## Priority / skip (parent, 2026-11-18)

| Item | Action |
|------|--------|
| **T040–T043** (payments) | **Parked.** Do not work. |
| **T004** | Skip (GitHub admin; other agent). |
| **Dependabot / WhatsApp templates / retention docs** | Do **not** own (other agents). |
| **This run** | **T072** only. |

## Decisions already made (parent defaults, 2026-11-18)

| Topic | Decision |
|-------|----------|
| Auth mechanism | Reuse `JOB_INTERNAL_SECRET` + `X-Job-Internal-Secret` (same as jobs/workers). Constant-time compare; 401 JSON `{"error":"unauthorized"}`; fail closed if secret unset. |
| Protected paths | `/customers` and `/customers/*` (CRUD, export/erase, pre-sale); `/ia/suggestions`; `/recommendation-contents`. |
| Unchanged (no new gate here) | `/health` (open); `/webhook/whatsapp` (Twilio signature stays; rate limits stay); `/jobs/*` and `/workers/*` (already gated — keep working). |
| Implementation locus | Extend `api/internal_job_auth.py` path predicate + existing router check in `api/routes.py`. Do not invent a second secret or OIDC. |
| Docs | Update PRODUCTION, DEPLOYMENT, threat-model, decision.md, LAUNCH-CHECKLIST; LGPD runbook auth notes; mark CL #19 if operator API is authenticated (or note partial). |
| Tests | Unit tests for router auth matrix (protected vs open paths). Coverage ≥ 95%; ruff + import style. |
| Out of scope | Payments T040–T043; T004; Dependabot; WhatsApp templates; retention docs; new pip deps; OIDC/IAP. |
| Git | English Conventional Commits; never `main`. Branch: `feat/t072-operator-api-auth` (**no** `cursor/` prefix). |

## Decisions made by the orchestrator

| Topic | Decision |
|-------|----------|
| Path helper | Extend `path_requires_internal_job_auth` to also return True for operator surfaces (`/customers`, `/customers/*`, `/ia/suggestions`, `/recommendation-contents`). Keep function name to avoid churn; jobs/workers behavior unchanged. |
| CL #19 | Update wording to “operator API authenticated (`JOB_INTERNAL_SECRET`)” and check complete: tier is already set via authenticated `PATCH /customers/{phone}`; dedicated “add-on” product surface remains out of scope / N/A until product defines add-ons. |
| LGPD runbook | Replace “no app auth” guidance with curl examples that send `X-Job-Internal-Secret`. |
| decision.md / threat-model | Close the “operator surface unauthenticated” gap; document residual risk of single shared secret (same as jobs). |
| INDEX / ROADMAP-TASKS | Add **T072** row + micro-task under Security & jobs. |

## Out of scope

- T040–T043 payments / provider choice.
- T004 GitHub admin.
- Dependabot, WhatsApp template work, retention-policy docs.
- Separate operator secret, OIDC, or Cloud Run IAM changes in app code.
- New product “add-on” APIs.
- New pip dependencies.

## Relevant files

| File | Role |
|------|------|
| `docs/specs/sdd/T072-operator-api-auth-sdd.md` | Full SDD + Expected work EW-xx (create) |
| `docs/specs/sdd/T072-builder-report.md` | Builder report for reviewer judge (create) |
| `docs/specs/sdd/INDEX.md` | Add T072 row |
| `docs/ROADMAP-TASKS.md` | Add T072 micro-task |
| `api/internal_job_auth.py` | Extend path predicate for operator routes |
| `api/routes.py` | Already calls path helper before handlers — verify matrix |
| `tests/unit/api/test_internal_job_auth.py` | Expand auth matrix unit tests |
| `docs/operations/PRODUCTION.md` | Routes + auth notes for operator paths |
| `docs/DEPLOYMENT.md` | Document secret covers operator APIs too |
| `docs/threat-model.md` | Update entry points + §4.5 |
| `docs/decision.md` | Close unauthenticated-operator gap |
| `docs/LAUNCH-CHECKLIST.md` | Operator API secret checks |
| `docs/operations/LGPD-EXPORT-DELETE.md` | Auth header on export/erase curls |
| `docs/COMMERCIAL-LAUNCH.md` | Item #19 only (T072 touch) |

## Acceptance criteria

See EW-01… in the SDD. In short:

- [ ] Operator paths require `X-Job-Internal-Secret`; wrong/missing/unset → 401 fail closed.
- [ ] `/health`, `/webhook/whatsapp` unchanged; `/jobs/*` `/workers/*` still gated as today.
- [ ] Docs updated (PRODUCTION, DEPLOYMENT, threat-model, decision.md, LAUNCH-CHECKLIST, LGPD runbook); CL #19 marked appropriately; INDEX + ROADMAP-TASKS T072.
- [ ] Router auth matrix unit tests; coverage ≥ 95%; ruff + import style.
- [ ] No payments / T004 / Dependabot / templates / retention ownership.
- [ ] Builder report + reviewer judge accept (each EW vs change list AND diff → match|gap|extra).

## Git policy (fixed)

Branch: `feat/t072-operator-api-auth` from `origin/main` (no `cursor/` prefix — see [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md)). **Never push to `main`.** Conventional Commits, English, lowercase subject. Parent/cloud creates the GitHub PR when ManagePullRequest is parent-owned; this agent still commits and pushes the branch. Commit bodies wrap at 72 characters (commitlint `body-max-line-length` is 100).

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).

Builder report path: `docs/specs/sdd/T072-builder-report.md` (one row per Expected work ID, files, done or skipped, plus Files touched). The reviewer reads that file, the SDD, and the diff, and is the judge. The reviewer does not edit any file.
