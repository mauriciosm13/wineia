# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T004** — GitHub branch protection on `main` (document exact Settings steps; optional `gh api` enable) **and** **CL #6** — Dependabot (pip + github-actions weekly). Comparison contract: [`docs/specs/sdd/T004-github-branch-protection-sdd.md`](docs/specs/sdd/T004-github-branch-protection-sdd.md). Its **Expected work** list (EW-01…) is what the reviewer checks against the builder report. Do not add behavior that list does not name. On conflict, the SDD Expected work table wins over PLAN.md / SPEC.md.

**Simplest scope:** T004 SDD Expected work covers branch-protection runbook **and** Dependabot config; mark **T004** + **CL #6**.

## Priority / skip (parent, 2026-11-18)

| Item | Action |
|------|--------|
| **T004 + CL #6** | **This run.** |
| Operator auth | Do **not** own. |
| WhatsApp / retention docs | Do **not** own. |
| T040–T043, T050, T051, T070, T071 | Do **not** flip or rework. |

## Decisions already made (parent defaults, 2026-11-18)

| Topic | Decision |
|-------|----------|
| T004 deliverable | **Documentation / runbook** of exact GitHub Settings steps (require PR; require status checks: Quality checks, Commit messages, PR title, Docker Test/Build as applicable). Optional BOT note in DEPLOYMENT. |
| `gh api` | **Try** to enable branch protection on `main` if permissions allow. If API fails (expected without admin), leave ops runbook + record “settings applied: no” in builder report. Still mark T004 `[x]` when runbook is complete **and** SDD says deliverable is the runbook (docs = done; API is bonus). |
| CL #6 | Add `.github/dependabot.yml` for **pip** + **github-actions**, **weekly**. Optionally note in CI docs. **pip-audit in CI is optional** — Dependabot alone satisfies “or Dependabot”. |
| Links | Link from `DEPLOYMENT.md`, `GIT_WORKFLOW.md`, and `COMMERCIAL-LAUNCH.md` #6. |
| Out of scope | No runtime product code. No operator auth. No WhatsApp/retention docs. No separate T074 SDD unless needed — Prefer Dependabot EW inside T004. |
| Git | English Conventional Commits; never `main`. Branch: `feat/t004-branch-protection-dependabot` (**no** `cursor/` prefix). |

## Decisions made by the orchestrator

| Topic | Decision |
|-------|----------|
| SDD shape | Expand T004 stub to T071-style with Expected work; include Dependabot as EW (no separate T074). |
| Status checks (runbook) | Exact job names from workflows: **Quality checks** (`ci.yml`), **Commit messages** + **PR title** (`conventional-commits.yml`), **Test** + **Build image** (`docker.yml`). Document that GitHub may show workflow/job labels; ops should select the live check names after a green PR. |
| Protection rules (runbook) | Require a pull request before merging; require the status checks above; dismiss stale reviews optional; do not allow force pushes / deletions on `main`. |
| API attempt | Orchestrator/builder runs `gh api` once; on 403, builder notes failure; do not block T004 `[x]`. |
| Marking complete | After EW hold: T004 `[x]` in ROADMAP-TASKS; CL #6 `[x]` in COMMERCIAL-LAUNCH; SDD + INDEX `implemented`. ROADMAP may note “Settings still human” if API failed. |
| pip-audit | Not required in this PR. |

## Out of scope

- Operator auth / WhatsApp policy / retention docs.
- pip-audit CI step (optional; Dependabot satisfies CL #6).
- Runtime `api/`, `domain/`, `infrastructure/`, product tests.
- T040–T043, T050, T051, T070, T071 status flips.
- New pip dependencies for the app.

## Relevant files

| File | Role |
|------|------|
| `docs/specs/sdd/T004-github-branch-protection-sdd.md` | Stub → expand with EW + Dependabot |
| `docs/specs/sdd/T004-builder-report.md` | Builder report for reviewer |
| `docs/specs/sdd/T071-launch-checklist-doc-sdd.md` | Template for docs-only SDD + EW |
| `.github/dependabot.yml` | New — pip + github-actions weekly |
| `docs/operations/` or runbook section in SDD / DEPLOYMENT | Exact Settings steps |
| `docs/DEPLOYMENT.md` | Link / BOT note for branch protection + Dependabot |
| `docs/GIT_WORKFLOW.md` | Link protection runbook + Dependabot |
| `docs/COMMERCIAL-LAUNCH.md` | Item #6 only |
| `docs/ci/AI-RUNTIME-REFERENCE.md` | Optional note that Dependabot covers #6 |
| `docs/ROADMAP-TASKS.md`, `docs/specs/sdd/INDEX.md` | T004 status only |
| `.github/workflows/ci.yml` | Check name: Quality checks |
| `.github/workflows/conventional-commits.yml` | Commit messages, PR title |
| `.github/workflows/docker.yml` | Test, Build image |

## Acceptance criteria

See EW-01… in the SDD. In short:

- [ ] T004 SDD expanded with Expected work covering branch-protection runbook + Dependabot.
- [ ] Exact GitHub Settings steps documented (require PR + named status checks).
- [ ] `.github/dependabot.yml` weekly for pip and github-actions.
- [ ] Links from DEPLOYMENT, GIT_WORKFLOW, COMMERCIAL-LAUNCH #6.
- [ ] `gh api` attempted; result recorded in builder report.
- [ ] T004 + CL #6 marked complete when EW hold; SDD/INDEX `implemented`.
- [ ] Builder report + reviewer judge accept (each EW vs change list AND diff → match|gap|extra).

## Git policy (fixed)

Branch: `feat/t004-branch-protection-dependabot` from `origin/main` (no `cursor/` prefix — see [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md)). **Never push to `main`.** Conventional Commits, English, lowercase subject. Parent creates the GitHub PR when ManagePullRequest is parent-owned; this agent still commits and pushes the branch. Commit bodies wrap at 72 characters (commitlint `body-max-line-length` is 100).

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).

Builder report path: `docs/specs/sdd/T004-builder-report.md` (one row per Expected work ID, files, done or skipped, plus Files touched). The reviewer reads that file, the SDD, and the diff, and is the judge. The reviewer does not edit any file.

## Roadmap pointer

- [docs/ROADMAP-TASKS.md](docs/ROADMAP-TASKS.md) — T004
- [docs/COMMERCIAL-LAUNCH.md](docs/COMMERCIAL-LAUNCH.md) — #6
- [docs/ROADMAP.md](docs/ROADMAP.md) — M0 engineering baseline (no separate code milestone for T004)
