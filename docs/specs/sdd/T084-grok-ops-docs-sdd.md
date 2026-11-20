# SDD — Grok ops + docs (T084)

**Status:** implemented  
**Task:** [T084](../../ROADMAP-TASKS.md) · parent [T080](./T080-grok-ia-stack-sdd.md) · depends **T082–T083**

## Goals

- Document `XAI_API_KEY` (and model env vars) in `DEPLOYMENT.md`, `PRODUCTION.md`, Secret Manager migration notes, and launch checklist.
- Confirm media/ops docs describe **Grok** (not Whisper/Claude as primary).
- Global daily IA call budget: prefer `IA_DAILY_CALL_BUDGET` with legacy `CLAUDE_DAILY_CALL_BUDGET` alias.
- Threat-model / retention: xAI as primary subprocessor; OpenAI not required.

## Acceptance criteria

- [x] Ops docs list xAI as primary IA vendor for text/vision/STT
- [x] OpenAI key removed from required secrets
- [x] Budget stop still documented and testable (`IA_DAILY_CALL_BUDGET` / alias)

## Related

- [T080](./T080-grok-ia-stack-sdd.md) · [T061 budget](./T061-global-claude-budget-stop-sdd.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-19 | Initial draft |
| 2026-11-20 | Implemented: SM mapping, IA_DAILY_CALL_BUDGET alias, docs refresh |
