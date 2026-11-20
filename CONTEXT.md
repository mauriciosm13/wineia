# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (this run)

**T083 only** — Replace OpenAI Whisper with **Grok Voice Transcribe** STT per SDD and ADR 0007.

| Order | Task | Focus | Status |
|-------|------|--------|--------|
| 0 | **T080** | Epic SDD | draft (docs on `main`) |
| 1 | **T081** | ADR 0007 + supersede 0006 | DONE |
| 2 | **T082** | Grok chat + vision client | DONE on `main` (#77) |
| 3 | **T083** | Grok STT replaces Whisper | **THIS RUN** |
| 4 | **T084** | Ops/docs / secrets / budget | out of scope |

Slice: [`docs/specs/sdd/T083-grok-stt-replace-whisper-sdd.md`](docs/specs/sdd/T083-grok-stt-replace-whisper-sdd.md)  
ADR: [`docs/adrs/0007-xai-grok-ia-stack.md`](docs/adrs/0007-xai-grok-ia-stack.md)  
Branch: `cursor/t083-grok-stt-afd2` (from latest `main`, includes T082)

## Requirements

1. Grok STT client under `infrastructure/external/` using `requests` + `XAI_API_KEY`.
2. REST `POST https://api.x.ai/v1/stt`, model e.g. `grok-voice-transcribe-2.0`, Portuguese language.
3. No new pip SDK dependency.
4. Wire messaging composition so `audio_transcriber` uses Grok STT (injectable callable shape unchanged).
5. Fail closed with existing Portuguese copy on STT failure.
6. Stop requiring `OPENAI_API_KEY` for default path; leave Whisper unused or remove if safe.
7. Update `config.example.json`.
8. Unit tests mock HTTP — no live xAI. MIME allowlist remains T076 audio types.
9. Brief PRODUCTION/DEPLOYMENT note that STT is Grok (no large Secret Manager rewrite — T084).
10. Mark T083 in ROADMAP-TASKS + INDEX + T083 SDD. Run pytest/ruff/import-style.
11. Conventional Commits EN. Push. PR via ManagePullRequest if available.

## Decisions locked

| Topic | Decision |
|-------|----------|
| STT provider | Grok Voice Transcribe REST (`POST /v1/stt`) |
| Model | `grok-voice-transcribe-2.0` |
| Language | `pt` (Brazilian Portuguese per xAI docs) |
| HTTP | `requests` only; no new pip SDK |
| Credential | `XAI_API_KEY` (full Secret Manager table = T084) |
| Domain shape | Injectable `audio_transcriber` callable unchanged |
| Fail closed | Existing Portuguese copy when STT fails |
| MIME | T076 STT-compatible audio allowlist unchanged |
| Whisper | Remove unused client + tests (safe; no other callers) |
| Git | Branch `cursor/t083-grok-stt-afd2`; never commit to `main` |

## Relevant files

- `infrastructure/external/openai_stt_client.py` — remove after cutover
- `infrastructure/external/grok_stt_client.py` — new
- `infrastructure/external/grok_client.py` — T082 `XAI_API_KEY` pattern
- `api/handlers/whatsapp_handler.py` — inject Grok STT
- `config.example.json`, `config.py`
- `docs/operations/PRODUCTION.md`, `docs/DEPLOYMENT.md`
- `docs/ROADMAP-TASKS.md`, `docs/specs/sdd/INDEX.md`, T083 SDD
- Tests: replace Whisper STT unit tests with Grok mocks

## Acceptance criteria (this run)

- [x] Grok STT client in `infrastructure/external/` (`requests` + `XAI_API_KEY`, no new SDK)
- [x] Default `audio_transcriber` uses Grok STT; injectable shape preserved
- [x] Fail closed with existing Portuguese copy
- [x] `OPENAI_API_KEY` not required for default path; Whisper removed
- [x] `config.example.json` updated
- [x] Unit tests mock HTTP (no live xAI); MIME allowlist = T076 audio types
- [x] Brief PRODUCTION/DEPLOYMENT STT=Grok note (no full T084 secrets rewrite)
- [x] T083 marked in ROADMAP-TASKS + INDEX + SDD
- [x] pytest + ruff + import-style pass
- [ ] Branch pushed; PR opened (or needs parent ManagePullRequest)

## Out of scope

- Payments (T040–T043)
- T079 media ops docs epic (parallel agent)
- Full T084 Secret Manager migration table
- Asking for or logging API key values
- Streaming / realtime STT WebSocket
- Speech-to-speech Grok Voice agents
