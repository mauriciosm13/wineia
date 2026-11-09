# SDD — GitHub branch protection on main (T004)

**Status:** draft  
**Task:** [T004](../../ROADMAP-TASKS.md)

## Canonical specification

This SDD is summarized here. Full normative detail: [`No runtime code.`](No runtime code.).

## Problem

`main` can merge without PR or failing CI if repo settings are open.

## Goals

Require PR + status checks (pytest, ruff, coverage, conventional commits) before merge.

## Acceptance criteria

GitHub Settings: branch protection on `main`; document steps in SDD; optional BOT note in DEPLOYMENT.

## Related

- `docs/GIT_WORKFLOW.md`

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD |
