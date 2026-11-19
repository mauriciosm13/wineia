# SDD — Migrate IA stack to xAI Grok (T080)

**Status:** draft  
**Task:** [T080](../../ROADMAP-TASKS.md)  
**Commercial-launch:** Phase 5 item #29 (planned)

## Problem

WineAI today uses **two AI vendors** for customer-facing multimodal turns:

| Path | Provider | Notes |
|------|----------|--------|
| Text + image (vision) | Anthropic Claude (`claude_client`) | Sommelier + broadcast |
| Inbound audio STT | OpenAI Whisper (`whisper-1`) | ADR 0006; Anthropic has no audio input |

For **test / early launch** volumes, WhatsApp + GCP dominate the bill, but the team wants a **single cheaper all-in-one model** for text + vision + STT to simplify keys, billing, and ops — and cut IA unit cost vs Claude Sonnet + Whisper.

Reference prices (USD, public lists ~2026-11; verify at implement time):

| Capability | Current | Grok alternative |
|------------|---------|------------------|
| Chat / vision | Claude Sonnet ~$3 / $15 per 1M tok | Grok 4.7 ~$2 / $6 per 1M tok (image tokens billed as input) |
| STT | Whisper ~$0.006 / min | Grok Voice Transcribe REST ~$0.10 / hour (~$0.0017 / min) |

Claude Haiku can be cheaper on tokens alone but does not remove the second STT vendor; Grok covers **chat + vision + STT** under one `XAI_API_KEY`.

## Goals

1. Primary IA provider for on-demand text, image (bottle/label), and inbound voice STT becomes **xAI Grok**.
2. Keep Clean Architecture: domain injects callables; no `domain` → Grok SDK imports.
3. Prefer **HTTP via existing `requests`** (same pattern as Whisper) unless an ADR justifies a pip SDK.
4. Preserve Portuguese fail-closed customer copy, entitlements (T024/T060), and a **global daily call budget** (generalize T061 naming if needed).
5. Supersede ADR 0006 with a new ADR (T081); document secrets and ops (T084).
6. Do not silently break text-only or media paths during the cutover — ship behind clear env config / feature flags if a dual-run period is needed.

## Non-goals

- Replacing Twilio / GCP.
- Outbound TTS or Grok speech-to-speech realtime voice agents.
- Image/video **generation** (`grok-imagine-*`) — WineAI only needs understanding inbound photos.
- Guaranteeing Grok Portuguese sommelier quality equals Claude without a short human A/B in test; quality check is an acceptance step, not a blocker for scaffolding.

## Slices (do in order)

| Task | Scope |
|------|--------|
| **T081** | ADR 0007: Grok chat/vision + Grok STT; supersede ADR 0006 |
| **T082** | Grok chat + vision client; wire `ia_service` (text + image) |
| **T083** | Grok STT replaces Whisper; remove OpenAI key when unused |
| **T084** | Secret Manager, DEPLOYMENT / PRODUCTION, budget env docs |

Depends on inbound media download + routing (**T075–T078**). Prefer **T079** ops notes updated for Grok in T084 if T079 already landed Claude/Whisper wording.

## Current code anchors

| Area | File |
|------|------|
| Claude | `infrastructure/external/claude_client.py` |
| Whisper STT | `infrastructure/external/openai_whisper_client.py` (or equivalent) |
| IA orchestration | `domain/services/ia_service.py` |
| Messaging media | `domain/services/messaging_service.py` |
| Budget | `domain/claude_budget.py` / Datastore budget repo |
| ADR Whisper | `docs/adrs/0006-openai-whisper-stt.md` |

## Expected work (epic-level)

| ID | Work |
|----|------|
| EW-01 | ADR 0007 accepted (T081) |
| EW-02 | Text + vision paths call Grok; unit tests mocked (T082) |
| EW-03 | Audio path calls Grok STT; Whisper path removed or dead-code gated (T083) |
| EW-04 | Ops docs + `XAI_API_KEY`; OpenAI optional/removed; budget still enforceable (T084) |
| EW-05 | Short Portuguese smoke checklist for text / photo / voice note in test |

## Acceptance criteria (epic)

- [ ] Customer text, image, and voice-note turns work in test with **only** xAI credentials for IA (plus Twilio/GCP).
- [ ] No new long-term media persistence.
- [ ] ROADMAP / COMMERCIAL-LAUNCH #29 and T081–T084 marked done when slices merge.
- [ ] ADR 0006 status updated to superseded.

## Related

- [T081](./T081-grok-provider-adr-sdd.md) · [T082](./T082-grok-chat-vision-client-sdd.md) · [T083](./T083-grok-stt-replace-whisper-sdd.md) · [T084](./T084-grok-ops-docs-sdd.md)
- [T074 media epic](./T074-inbound-whatsapp-media-sdd.md) · [ADR 0006](../../adrs/0006-openai-whisper-stt.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-19 | Initial draft after test-cost comparison (Claude+Whisper vs Grok) |
