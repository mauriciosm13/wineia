# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T071** — Launch checklist document (COMMERCIAL-LAUNCH #68). Create an operator go-live checklist that verifies tag deploy, secrets/env, Scheduler smoke, Twilio signature, Cloud Tasks workers, health, entitlements/budget notes, and links to threat-model + SDDs + DEPLOYMENT + PRODUCTION.

The comparison contract is [`docs/specs/sdd/T071-launch-checklist-doc-sdd.md`](docs/specs/sdd/T071-launch-checklist-doc-sdd.md). Its **Expected work** list (EW-01…) is what the reviewer checks against the builder report. Do not add behavior that list does not name. On conflict, the SDD Expected work table wins over PLAN.md / SPEC.md.

## Priority / skip (parent, 2026-11-18)

| Item | Action |
|------|--------|
| **T040–T043** (payments) | **Parked.** Do not implement. Checklist must say payments are deferred and manual provisioning continues until later. |
| **T004** | Skip (GitHub admin). |
| **T050 / T051** | Do **not** implement code paths. Another agent may run T050 in parallel — do not flip T050 status. |
| **T070** | Do not own fully. Optional short note that PRODUCTION.md must stay in sync (GIT_WORKFLOW or PR template) only if it does not conflict with parallel work. |
| **This run** | **T071** only (docs-focused). |

## Decisions already made (parent defaults, 2026-11-18)

| Topic | Decision |
|-------|----------|
| Deliverable | New `docs/LAUNCH-CHECKLIST.md` — operator go-live verification steps (not a rewrite of COMMERCIAL-LAUNCH phases). |
| Checklist contents | Verify tag deploy; Secret Manager / env (incl. `JOB_INTERNAL_SECRET`, `ON_DEMAND_DAILY_LIMIT_*`, `CLAUDE_DAILY_CALL_BUDGET`); Scheduler jobs smoke; Twilio webhook signature; Cloud Tasks workers; health; entitlements/budget notes; link threat-model + SDDs + DEPLOYMENT + PRODUCTION. |
| Payments section | **Explicitly deferred** (T040–T043 parked). Checklist states manual provisioning until payments land. |
| Cross-links | Link from `docs/COMMERCIAL-LAUNCH.md` item 68 and `docs/ENGINEERING_MANUAL.md`. |
| Optional T070 spirit | Short note in `docs/GIT_WORKFLOW.md` or PR template that PRODUCTION.md must stay in sync — only if no conflict with parallel T070 work. |
| Status flips | Mark T071 + CL #68 when EW hold. Change **only the T071 line/row** in ROADMAP-TASKS and INDEX. Do not flip T050. |
| Runtime code | No runtime code unless a tiny docs-only change. |
| Git | English Conventional Commits; never `main`. Branch: `feat/t071-launch-checklist` (**no** `cursor/` prefix). |

## Decisions made by the orchestrator

| Topic | Decision |
|-------|----------|
| SDD style | Expand stub to T031-style with Expected work EW-xx; reviewer judges each EW vs builder report + diff. |
| Checklist scope | Ops verification after a production tag/dispatch deploy — complements COMMERCIAL-LAUNCH, does not replace it. |
| `/ia/suggestions` | Include threat-model note: must not be public in production (network restriction or auth). |
| Payments wording | Dedicated deferred section; pointer to parked T040–T043 / manual provisioning (no Asaas decision claimed). |
| ROADMAP-TASKS / INDEX | Touch **only** the T071 checkbox/row when flipping; leave T050/T070/T040–T043 unchanged. |
| T070 note | Prefer a one-line reminder in `docs/GIT_WORKFLOW.md` (docs sync) if the file already discusses ops docs; skip PR template if it would conflict. |

## Out of scope

- T040–T043 payments implementation / provider choice / Asaas.
- T004 GitHub admin.
- T050 / T051 LGPD code or status flips.
- T070 full PRODUCTION.md refresh ownership.
- Runtime API/domain/infrastructure code changes.
- New pip dependencies; `docs/MVP_SCOPE.md`.

## Relevant files

| File | Role |
|------|------|
| `docs/specs/sdd/T071-launch-checklist-doc-sdd.md` | Stub → expand to T031-style with Expected work EW-xx |
| `docs/specs/sdd/T031-scheduler-deploy-cd-sdd.md` | Template for SDD + EW style |
| `docs/specs/sdd/T031-builder-report.md` | Template for builder report |
| `docs/LAUNCH-CHECKLIST.md` | **New** operator go-live checklist |
| `docs/COMMERCIAL-LAUNCH.md` | Item #68 link + check when done |
| `docs/ENGINEERING_MANUAL.md` | Link to launch checklist |
| `docs/operations/PRODUCTION.md` | Source of truth linked from checklist (do not rewrite for T070) |
| `docs/DEPLOYMENT.md` | Tag deploy / env / Scheduler source linked from checklist |
| `docs/threat-model.md` | Linked; `/ia/suggestions` note |
| `docs/GIT_WORKFLOW.md` | Optional PRODUCTION.md sync note |
| `docs/ROADMAP-TASKS.md`, `docs/specs/sdd/INDEX.md` | T071 status only |
| `PLAN.md`, `SPEC.md` | Plan/spec updates for T071 |
| `docs/specs/sdd/T071-builder-report.md` | Builder report for reviewer judge |

## Acceptance criteria

See EW-01… in the SDD. In short:

- [x] `docs/LAUNCH-CHECKLIST.md` exists with operator go-live steps covering deploy, secrets/env, Scheduler, Twilio, workers, health, entitlements/budget, deferred payments, and doc links.
- [x] COMMERCIAL-LAUNCH #68 links to the checklist; ENGINEERING_MANUAL links it.
- [x] Payments explicitly deferred; manual provisioning called out.
- [x] Optional GIT_WORKFLOW note on PRODUCTION.md sync if safe.
- [x] T071 + CL #68 marked when EW hold; only T071 rows flipped in ROADMAP-TASKS / INDEX.
- [x] No runtime code; no T050 flip; no payments implementation.
- [x] Builder report + reviewer judge accept (each EW vs change list AND diff → match|gap|extra).

## Git policy (fixed)

Branch: `feat/t071-launch-checklist` from `origin/main` (no `cursor/` prefix — see [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md)). **Never push to `main`.** Conventional Commits, English, lowercase subject. Parent creates the GitHub PR if ManagePullRequest is parent-owned; this run may still push the branch. Commit bodies wrap at 72 characters (commitlint `body-max-line-length` is 100).

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).

Builder report path: `docs/specs/sdd/T071-builder-report.md` (one row per Expected work ID, files, done or skipped, plus Files touched). The reviewer reads that file, the SDD, and the diff, and is the judge. The reviewer does not edit any file.
