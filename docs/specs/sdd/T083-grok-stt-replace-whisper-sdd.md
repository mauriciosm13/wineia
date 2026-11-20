# SDD — Grok STT replaces Whisper (T083)

**Status:** implemented  
**Task:** [T083](../../ROADMAP-TASKS.md) · parent [T080](./T080-grok-ia-stack-sdd.md) · depends **T081**; media download **T076**

## Goals

- Replace OpenAI Whisper transcription with **Grok Voice Transcribe** REST (`POST https://api.x.ai/v1/stt`, model `grok-voice-transcribe-2.0` or current default).
- Language: Portuguese (`pt` — Brazilian Portuguese per xAI language table).
- Injectable `audio_transcriber` in messaging domain unchanged in shape.
- Stop requiring `OPENAI_API_KEY` once Whisper path is removed; document in T084.
- MIME allowlist remains T076 audio types; fail closed with existing Portuguese copy when STT fails.

## Non-goals

- Streaming / realtime STT WebSocket.
- Speech-to-speech Grok Voice agents.

## Acceptance criteria

- [x] Unit tests mock Grok STT; Whisper client removed or unreachable in default config.
- [x] ADR 0006 superseded note already present from T081.
- [x] No new pip dependency by default.

## Related

- [T077 Whisper](./T077-inbound-audio-stt-sdd.md) · [T080](./T080-grok-ia-stack-sdd.md) · [ADR 0007](../../adrs/0007-xai-grok-ia-stack.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-19 | Initial draft |
| 2026-11-20 | Implemented: `grok_stt_client`, handler wiring, Whisper removed |
