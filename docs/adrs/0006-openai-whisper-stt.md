# ADR 0006: OpenAI Whisper for inbound audio STT

**Status:** Superseded by [ADR 0007](./0007-xai-grok-ia-stack.md)  
**Date:** 2026-11-18  
**Deciders:** WineAI team  
**Related:** T077 · [T077 SDD](../specs/sdd/T077-inbound-audio-stt-sdd.md) · [T074 epic](../specs/sdd/T074-inbound-whatsapp-media-sdd.md) · [ADR 0007](./0007-xai-grok-ia-stack.md)

> **Superseded 2026-11-19:** Product chose xAI Grok for chat + vision + STT (single vendor for test/launch). See [ADR 0007](./0007-xai-grok-ia-stack.md). This document is retained for history; do not delete.

---

## Context

Inbound WhatsApp voice notes (T076 download) must become Portuguese text for the existing on-demand IA path. Parent defaults prefer Anthropic/Claude for STT when feasible to avoid a new vendor.

Anthropic's Messages API accepts **text and image** content blocks only. There is no audio content type; Claude cannot transcribe OGG/Opus/MPEG voice notes directly (confirmed against current API docs and SDK types in anthropic 0.84.0).

WineAI therefore needs a dedicated speech-to-text provider for T077.

---

## Decision

1. **Provider:** OpenAI Audio Transcriptions API (`POST https://api.openai.com/v1/audio/transcriptions`).
2. **Model:** `whisper-1` with `language=pt` (pt-BR target).
3. **Dependency:** **No new pip package.** Call the HTTP API with the existing `requests` client under `infrastructure/external/`.
4. **Credentials:** `OPENAI_API_KEY` from environment (optional `config.json` fallback for local/dev, same operational family as Anthropic key loading).
5. **MIME:** Attempt STT only for Whisper-compatible types from the T076 audio allowlist (`audio/ogg`, `audio/opus`, `audio/mpeg`, `audio/mp4`, `audio/aac`). `audio/amr` / `audio/3gpp` fail closed with Portuguese copy without calling OpenAI.
6. **Architecture:** Domain receives an injectable `audio_transcriber` callable; domain must not import the OpenAI client module.

---

## Consequences

### Positive

- Unblocks voice-note → Gastón replies without inventing unsupported Claude audio input
- Zero new pip dependency / smaller supply-chain surface than adding `openai` or `google-cloud-speech`
- Whisper supports WhatsApp-common `ogg` / `mpeg` / `mp4` payloads

### Negative

- Second AI vendor (OpenAI) besides Anthropic; new secret to store and rotate
- AMR/3GPP voice notes are accepted for download but cannot be transcribed in v1
- OpenAI billing and rate limits are separate from Claude daily budget (STT does not consume Claude budget; successful product reply still counts one on-demand turn)

### Neutral

- Image vision remains Claude multimodal (T078); STT is audio-only

---

## Alternatives

| Alternative | Why not chosen |
|-------------|----------------|
| Claude multimodal / Files API for audio | API has no audio content block; feature request open, not shippable |
| Add `openai` Python SDK | Heavier than needed; `requests` already present |
| Google Cloud Speech-to-Text | New GCP product + pip dep; parent prefers avoid Google/Whisper unless required — Whisper via HTTP is smaller |
| Local/open-source Whisper in Cloud Run | Large image, CPU/GPU cost, ops burden out of scope for T077 |

---

## Tradeoffs

We accept a second vendor for **correct product behavior** on voice notes, while keeping the dependency surface minimal (HTTP + env key only). Revisit if Anthropic ships native audio input.
