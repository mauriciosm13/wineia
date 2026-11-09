# SDD — No direct commits to main (T001)

**Status:** implemented  
**Task:** [T001](../../ROADMAP-TASKS.md)

## Problem

Agents or humans could push to `main` and bypass review.

## Goals

Add `.cursor/rules/no-direct-main.mdc` and document PR-only workflow in GIT_WORKFLOW.

## Acceptance criteria

Rule file exists; linked from AGENTS.md and COMMERCIAL-LAUNCH #5.

## Related

- `.cursor/rules/no-direct-main.mdc`
- `docs/GIT_WORKFLOW.md`

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD |
