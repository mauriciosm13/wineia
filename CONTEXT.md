# CONTEXT — WineAI (wineia)

## Primary (completed this branch)

**T084** — Grok ops cleanup: Secret Manager / DEPLOYMENT / PRODUCTION / LAUNCH-CHECKLIST; `IA_DAILY_CALL_BUDGET` (+ `CLAUDE_DAILY_CALL_BUDGET` alias); OpenAI not required; xAI in DATA-RETENTION.

## Still for humans (ops)

1. Create SM secret `wine-concierge-xai-api-key` and bind `XAI_API_KEY` on Cloud Run (or plain env for smoke).
2. Deploy `main` revision that includes Grok (T082/T083) if not already live.
3. Optionally set `IA_DAILY_CALL_BUDGET=500`.

## Next product

- Asaas payments T040–T044
- Waitlist T085–T088

Branch: `cursor/t084-grok-ops-cleanup-afd2`
