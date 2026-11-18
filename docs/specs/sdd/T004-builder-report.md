# Builder report — T004 GitHub branch protection + CL #6 Dependabot

**SDD:** [T004-github-branch-protection-sdd.md](./T004-github-branch-protection-sdd.md)  
**Branch:** `feat/t004-branch-protection-dependabot`  
**Date:** 2026-11-18  
**Settings applied:** **no** (`gh api` HTTP 403 — Resource not accessible by integration)

## Expected work

| ID | Result | Files | What changed |
|----|--------|-------|--------------|
| EW-01 | done | `docs/specs/sdd/T004-github-branch-protection-sdd.md` | Expanded stub to T071-style SDD: Behavior runbook with require-PR, named checks (Quality checks, Commit messages, PR title, Test, Build image), no force push/deletion, UI label confirmation note, docs = deliverable / UI-API = ops. EW table includes Dependabot (no separate T074). |
| EW-02 | done | this report | Attempted GET + PUT `repos/mauriciosm13/wineia/branches/main/protection` via `gh api`. Both returned **HTTP 403** (`Resource not accessible by integration`). Token permissions: admin/maintain/push all false. **settings applied: no**. Does not block T004 `[x]` per SDD. |
| EW-03 | done | `.github/dependabot.yml` | New file: `version: 2`; weekly `pip` and `github-actions` at directory `/`. |
| EW-04 | done | `docs/DEPLOYMENT.md` | New section “Branch protection and Dependabot (ops)” linking T004 SDD + Dependabot yml; admin/BOT note that Settings may need a human. Related docs list includes T004 SDD. |
| EW-05 | done | `docs/GIT_WORKFLOW.md` | Replaced one-liner with require-PR + named checks link to T004 SDD; added Dependabot weekly note. |
| EW-06 | done | `docs/COMMERCIAL-LAUNCH.md` | Item 6 links `.github/dependabot.yml` and T004 SDD; wording keeps “pip-audit or Dependabot”. |
| EW-07 | done | `docs/ci/AI-RUNTIME-REFERENCE.md` | Notes Dependabot covers CL #6; pip-audit remains optional. |
| EW-08 | done | `docs/ROADMAP-TASKS.md`, `docs/COMMERCIAL-LAUNCH.md`, SDD, `docs/specs/sdd/INDEX.md` | After EW-01–EW-07 and EW-09: T004 checked with note “Settings still human”; CL #6 checked only; SDD status `implemented`; INDEX T004 `implemented`. Other tasks untouched. |
| EW-09 | done | whole diff | Docs + Dependabot + CONTEXT handoff only. No `api/` / `domain/` / `infrastructure/` product changes. No pip-audit job. No payments/LGPD/WhatsApp retention. |

## Deviations from the SDD

1. `gh api` could not apply protection (403). Runbook remains the ops path; ROADMAP-TASKS notes Settings still human.
2. CONTEXT.md updated for orchestrator handoff (allowed under EW-09).

## Files touched

| Path | EW |
|------|----|
| `CONTEXT.md` | handoff |
| `docs/specs/sdd/T004-github-branch-protection-sdd.md` | EW-01, EW-08 |
| `docs/specs/sdd/T004-builder-report.md` | this report / EW-02 |
| `.github/dependabot.yml` | EW-03 |
| `docs/DEPLOYMENT.md` | EW-04 |
| `docs/GIT_WORKFLOW.md` | EW-05 |
| `docs/COMMERCIAL-LAUNCH.md` | EW-06, EW-08 |
| `docs/ci/AI-RUNTIME-REFERENCE.md` | EW-07 |
| `docs/ROADMAP-TASKS.md` | EW-08 |
| `docs/specs/sdd/INDEX.md` | EW-08 |

## Verification

| Command | Result |
|---------|--------|
| `gh api repos/mauriciosm13/wineia/branches/main/protection` | HTTP 403 |
| `gh api -X PUT .../branches/main/protection` (JSON body with required checks) | HTTP 403 |
| `test -f .github/dependabot.yml` | present |
| YAML parse of dependabot.yml | OK |
| `git diff --name-only` vs EW-09 | no api/domain/infrastructure product paths |
