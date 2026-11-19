# ADR 0007: xAI Grok for chat, vision, and STT

**Status:** Accepted  
**Date:** 2026-11-19  
**Deciders:** WineAI team  
**Related:** T080–T084 · [T080 epic SDD](../specs/sdd/T080-grok-ia-stack-sdd.md) · [T081 SDD](../specs/sdd/T081-grok-provider-adr-sdd.md) · [ADR 0006](./0006-openai-whisper-stt.md)

---

## Context

WineAI’s customer-facing IA path today uses **two vendors**:

| Path | Provider | Basis |
|------|----------|--------|
| Text + image (vision) | Anthropic Claude | Messages API; image blocks |
| Inbound audio STT | OpenAI Whisper | [ADR 0006](./0006-openai-whisper-stt.md) — Claude has no audio input |

For **test and early launch** volumes, the team wants **one cheaper all-in-one vendor** for chat + vision + STT to simplify keys, billing, and ops, and to cut IA unit cost versus Claude Sonnet plus Whisper.

Claude Haiku can be cheaper on **tokens alone** but does not unify STT; a second speech vendor would remain. Product chose a single stack that covers text, image understanding, and voice-note transcription under one credential.

---

## Decision

1. **Chat + vision provider:** xAI **Grok** via the chat/completions (or equivalent Messages-compatible) HTTP API. Pin a current flagship chat model with **text + image input** (e.g. `grok-4.7`). Exact model id is set in config/env at implement time (T082) and may be bumped without a new ADR if capability and pricing family stay the same.
2. **STT provider:** **Grok Voice Transcribe** REST — `POST https://api.x.ai/v1/stt` with a pinned voice-transcribe model (e.g. `grok-voice-transcribe-2.0`). This replaces OpenAI Whisper for inbound WhatsApp audio (T083).
3. **Credential:** `XAI_API_KEY` from environment (Secret Manager / Cloud Run wiring in T084). Optional local `config.json` fallback may follow the same pattern as other AI keys.
4. **Dependency:** Prefer **HTTP via the existing `requests` library**. Do **not** add a new pip SDK (e.g. `xai-sdk`) by default; justify any SDK in a follow-up ADR if needed.
5. **Architecture:** Domain keeps **injectable callables** (chat/vision completer, audio transcriber). Infrastructure owns Grok HTTP clients; `domain` must not import xAI client modules.
6. **Scope of this ADR:** Provider **choice** only. Implementation slices are T082 (chat/vision), T083 (STT cutover), T084 (ops/secrets/budget docs).

This ADR **supersedes [ADR 0006](./0006-openai-whisper-stt.md)** (OpenAI Whisper for STT).

---

## Consequences

### Positive

- One IA vendor and one secret (`XAI_API_KEY`) for text, vision, and STT in test/launch
- Lower published unit cost vs Claude Sonnet + Whisper at reference list prices (~2026-11)
- Same Clean Architecture pattern as Whisper/Claude: HTTP + injectable callables, no domain SDK imports
- No new pip dependency by default (smaller supply chain)

### Negative

- Portuguese sommelier quality vs Claude needs a short human A/B in test (acceptance for epic, not a blocker for scaffolding)
- Anthropic and OpenAI clients remain until T082/T083 land and dead code / keys are removed
- Grok rate limits, outages, and pricing are a single point of failure for IA until a fallback policy is defined

### Neutral

- Claude Haiku remains a viable **token-cost** alternative for text-only, but was rejected for this ADR because it does not remove the STT vendor
- Daily call budget (T061) should be generalized or aliased to cover Grok calls (T084); STT and chat may share or split counters as ops decides
- Implementation work is sliced: T082 → T083 → T084 after this ADR

---

## Alternatives

| Alternative | Why not chosen |
|-------------|----------------|
| Keep Claude + Whisper (ADR 0006) | Two vendors, higher combined cost for test volumes |
| Claude Haiku + Whisper | Cheaper tokens possible, but still a second STT vendor and key |
| Add `xai-sdk` (or OpenAI-compat SDK) | Heavier than needed; `requests` already present (same as Whisper ADR) |
| Google Cloud Speech + Claude | New GCP product surface; does not unify chat/vision/STT |
| Local Whisper / open models on Cloud Run | Image size, CPU/GPU, ops burden out of scope for launch |

---

## Tradeoffs

We accept migrating off Anthropic Claude and OpenAI Whisper for the **primary** on-demand and broadcast IA paths in favor of **ops simplicity and lower test/launch unit cost**, with quality verification as an epic acceptance step. Revisit if Grok Portuguese quality or pricing regresses, or if Anthropic ships native audio input that reunifies Claude-only STT without a second vendor.
