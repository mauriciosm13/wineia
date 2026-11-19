# SDD — Grok ops + docs (T084)

**Status:** draft  
**Task:** [T084](../../ROADMAP-TASKS.md) · parent [T080](./T080-grok-ia-stack-sdd.md) · depends **T082–T083** (or land docs as each merges)

## Goals

- Document `XAI_API_KEY` (and model env vars if any) in `DEPLOYMENT.md`, `PRODUCTION.md`, Secret Manager migration notes, and launch checklist.
- Update media/ops docs if they still say Claude vision + Whisper exclusively (coordinate with **T079**).
- Keep a **global daily IA call budget** enforceable after Claude→Grok rename (prefer generic name e.g. `IA_DAILY_CALL_BUDGET` with legacy `CLAUDE_DAILY_CALL_BUDGET` alias, or document that the existing env still counts Grok calls).
- Threat-model / retention: ephemeral media + third-party xAI processing note (LGPD / processor list).

## Acceptance criteria

- [ ] Ops docs list xAI as primary IA vendor for text/vision/STT.
- [ ] OpenAI key removed from required secrets when Whisper is gone.
- [ ] Budget stop still documented and testable.

## Related

- [T080](./T080-grok-ia-stack-sdd.md) · [T061 budget](./T061-global-claude-budget-stop-sdd.md) · [T079 media ops](./T079-inbound-media-ops-tests-sdd.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-19 | Initial draft |
