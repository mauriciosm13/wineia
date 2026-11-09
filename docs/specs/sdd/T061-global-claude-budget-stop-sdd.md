# SDD — Global Claude budget stop (T061)

**Status:** draft  
**Task:** [T061](../../ROADMAP-TASKS.md)

## Problem

Runaway LLM cost if abuse or bug loops.

## Goals

Daily/monthly spend guardrail: stop new Claude calls when budget exceeded; alert ops.

## Acceptance criteria

Env-configured thresholds; fail closed for new generations; jobs log skip reason.

## Related

- `docs/COMMERCIAL-LAUNCH.md #28`
- `../threat-model.md`

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD |
