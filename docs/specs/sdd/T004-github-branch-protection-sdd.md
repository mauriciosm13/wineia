# SDD — GitHub branch protection on main (T004)

**Status:** implemented  
**Task:** [T004](../../ROADMAP-TASKS.md)  
**Commercial:** [COMMERCIAL-LAUNCH.md](../../COMMERCIAL-LAUNCH.md) item **#6** (Dependabot)  
**Comparison contract:** this Expected work list is what the reviewer checks against [T004-builder-report.md](./T004-builder-report.md).

## Canonical specification

No runtime application code. Deliverables are documentation (branch-protection runbook) and repository config (Dependabot). Enabling protection in the GitHub UI (or via API) is an **ops step**; the SDD deliverable is complete when the runbook and Dependabot config exist.

## Problem

`main` can merge without a PR or with failing CI if repository branch protection is open. Supply-chain updates for pip and GitHub Actions are also untracked (CL #6).

## Goals

- Document exact GitHub Settings steps so an admin can require PRs and named status checks on `main`.
- Optionally attempt `gh api` to apply the same rules; if permissions fail, keep the runbook and record the failure.
- Add Dependabot for **pip** and **github-actions** on a **weekly** schedule (satisfies CL #6 without requiring pip-audit in CI).
- Link the runbook and Dependabot from DEPLOYMENT, GIT_WORKFLOW, and COMMERCIAL-LAUNCH #6.

## Non-goals

- Operator auth, WhatsApp policy, or retention docs.
- pip-audit CI step (optional; Dependabot alone satisfies “or Dependabot”).
- Runtime `api/`, `domain/`, `infrastructure/`, or product tests.
- Flipping T040–T043, T050, T051, T070, T071.
- Guaranteeing that the integration token can mutate Settings (admin may be required).

## Behavior

### Branch protection runbook (ops)

Document in this SDD (and summary links from DEPLOYMENT / GIT_WORKFLOW) these **GitHub UI** steps for repository `mauriciosm13/wineia` (or the current origin):

1. Open **Settings → Branches → Add branch protection rule** (or **Branch rules** / **Rulesets** if the UI uses that label).
2. Branch name pattern: `main`.
3. Enable **Require a pull request before merging**.
4. Enable **Require status checks to pass before merging**, and require these check names (job `name:` from workflows; after one green PR, confirm labels in the UI if GitHub prefixes the workflow name):

| Check name (job) | Workflow |
|------------------|----------|
| `Quality checks` | `.github/workflows/ci.yml` |
| `Commit messages` | `.github/workflows/conventional-commits.yml` |
| `PR title` | `.github/workflows/conventional-commits.yml` |
| `Test` | `.github/workflows/docker.yml` |
| `Build image` | `.github/workflows/docker.yml` |

5. Enable **Do not allow bypassing the above settings** if available to admins who should not skip checks.
6. Disable force pushes and branch deletion on `main`.
7. Save the rule.

Optional API (bonus; not required for T004 `[x]`):

```bash
# Inspect current protection (fails with 403 without admin)
gh api repos/:owner/:repo/branches/main/protection
```

If API enable fails, ops must complete the UI steps. ROADMAP-TASKS may note “Settings still human” while T004 remains checked because the **documentation deliverable** is done.

### Dependabot (CL #6)

`.github/dependabot.yml`:

- `package-ecosystem: pip`, `directory: /`, `schedule.interval: weekly`
- `package-ecosystem: github-actions`, `directory: /`, `schedule.interval: weekly`

No pip-audit workflow step required in this change.

## Expected work

The builder implements only these items. The reviewer marks each **match**, **gap**, or **extra**.

| ID | Must be true when the work is done | Where |
|----|-------------------------------------|--------|
| EW-01 | This SDD documents the exact GitHub Settings steps for `main`: require PR before merge; require status checks **Quality checks**, **Commit messages**, **PR title**, **Test**, **Build image** (mapped to the three workflow files); no force push / deletion; notes that live UI labels may need confirmation after a green PR; states that docs are the T004 deliverable and UI/API apply is ops. | `docs/specs/sdd/T004-github-branch-protection-sdd.md` |
| EW-02 | Builder attempts `gh api` read and/or update of `main` branch protection and records success or failure (including HTTP status) in the builder report. Failure does not block T004 completion. | builder report |
| EW-03 | `.github/dependabot.yml` exists with weekly updates for `pip` and `github-actions` at directory `/`. | `.github/dependabot.yml` |
| EW-04 | `docs/DEPLOYMENT.md` links the T004 branch-protection runbook (this SDD) and notes Dependabot (CL #6). Optional short “BOT / admin” note that Settings may need a human with admin. | `docs/DEPLOYMENT.md` |
| EW-05 | `docs/GIT_WORKFLOW.md` points to the T004 runbook for enabling protection (replace or expand the one-liner) and mentions Dependabot weekly updates. | `docs/GIT_WORKFLOW.md` |
| EW-06 | `docs/COMMERCIAL-LAUNCH.md` item **6** links Dependabot config and/or this SDD; wording remains “pip-audit or Dependabot”. | `docs/COMMERCIAL-LAUNCH.md` |
| EW-07 | Optional: `docs/ci/AI-RUNTIME-REFERENCE.md` notes that Dependabot covers CL #6 (pip-audit still optional). | `docs/ci/AI-RUNTIME-REFERENCE.md` |
| EW-08 | Only after EW-01–EW-07 and EW-09 hold: `ROADMAP-TASKS.md` checks **only** T004 (may note Settings still human if API failed); `COMMERCIAL-LAUNCH.md` checks **only** item 6; this SDD status is `implemented`; `INDEX.md` T004 row is `implemented`. Do not flip other tasks. | those files |
| EW-09 | Diff is docs + `.github/dependabot.yml` (+ CONTEXT handoff). No runtime product code under `api/`, `domain/`, `infrastructure/`. No pip-audit job required. No payments / LGPD / WhatsApp retention work. | whole diff |

## Builder report

After implementation, write `docs/specs/sdd/T004-builder-report.md`:

| ID | Result (`done` or `skipped`) | Files | What changed |
|----|-------------------------------|-------|----------------|

Add a **Files touched** list of every path in the diff and the verification commands with results. Record **settings applied: yes|no** and the `gh api` outcome. The reviewer treats any path not justified by an ID as **extra**.

## Reviewer comparison

Read this file, the builder report, and the diff. Return only:

- One line per ID: `EW-xx match|gap — evidence`
- Extras: paths or behavior not in the table
- Bugs that break an ID or would mislead an admin enabling protection
- Verdict: accept or reject

Do not implement.

## Related

- [CONTEXT.md](../../../CONTEXT.md)
- [GIT_WORKFLOW.md](../../GIT_WORKFLOW.md)
- [DEPLOYMENT.md](../../DEPLOYMENT.md)
- [COMMERCIAL-LAUNCH.md](../../COMMERCIAL-LAUNCH.md) — #6
- [ci/AI-RUNTIME-REFERENCE.md](../../ci/AI-RUNTIME-REFERENCE.md)
- `.github/workflows/ci.yml`
- `.github/workflows/conventional-commits.yml`
- `.github/workflows/docker.yml`

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD stub |
| 2026-11-18 | Expand Expected work: runbook + Dependabot (CL #6); docs deliverable; optional gh api |
