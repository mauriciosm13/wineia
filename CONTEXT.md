# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T081** — write and accept **ADR 0007**: xAI Grok for chat + vision + STT; mark **ADR 0006** (OpenAI Whisper) superseded. First implementable slice of epic **T080**.

| Order | Task | Focus | Status |
|-------|------|--------|--------|
| 0 | **T080** | Epic SDD | draft (docs on `main`) |
| 1 | **T081** | ADR 0007 + supersede 0006 | **DONE (this run)** |
| 2 | **T082** | Grok chat + vision client | next |
| 3 | **T083** | Grok STT replaces Whisper | later |
| 4 | **T084** | Ops/docs / secrets / budget | later |

Epic: [`docs/specs/sdd/T080-grok-ia-stack-sdd.md`](docs/specs/sdd/T080-grok-ia-stack-sdd.md)  
Slice: [`docs/specs/sdd/T081-grok-provider-adr-sdd.md`](docs/specs/sdd/T081-grok-provider-adr-sdd.md)  
ADR: [`docs/adrs/0007-xai-grok-ia-stack.md`](docs/adrs/0007-xai-grok-ia-stack.md)

## Priority / skip

| Item | Action |
|------|--------|
| **T040–T043** payments | **Parked**. Do not implement. |
| **T079** media ops/docs | Still open; do **not** block T081; can parallel later or with T084. |
| **T082–T084** | Do **not** implement in this run unless T081 finishes early and parent re-scopes. |

## Decisions locked

| Topic | Decision |
|-------|----------|
| IA vendor (test/launch) | **xAI Grok** for chat + vision + STT (T080–T084). |
| Chat/vision model | Prefer current flagship chat model with image input (e.g. `grok-4.7`); pin exact id in ADR. |
| STT | Grok Voice Transcribe REST (`POST /v1/stt`, e.g. `grok-voice-transcribe-2.0`); supersedes Whisper ADR 0006. |
| Dependency | Prefer **HTTP + `requests`**; no new pip SDK unless ADR justifies. |
| Credential | `XAI_API_KEY` (ops wiring is T084). |
| Architecture | Domain injectable callables; infrastructure clients only. |
| Git | Branch `cursor/<topic>-afd2` from `main`; never commit to `main`; PR via ManagePullRequest; Conventional Commits English. |

## Relevant files

- `docs/adrs/0006-openai-whisper-stt.md` — Superseded by ADR 0007
- `docs/adrs/0007-xai-grok-ia-stack.md` — Accepted
- `docs/specs/sdd/T081-grok-provider-adr-sdd.md` — implemented
- `docs/specs/sdd/INDEX.md` / `docs/ROADMAP-TASKS.md` — T081 done

## Acceptance criteria (this run)

- [x] ADR 0007 exists, Accepted, documents Grok chat/vision + Grok STT + no-SDK-by-default + supersedes 0006
- [x] ADR 0006 header Status = Superseded by ADR 0007 (history kept)
- [x] ROADMAP-TASKS T081 checked; SDD INDEX T081 → implemented (or equivalent)
- [ ] PR opened against `main`; CI green — branch pushed; ManagePullRequest unavailable in this run (gh createPullRequest 403)
- [x] No runtime code changes in this slice (ADR/docs only)

## Out of scope

- Implementing Grok HTTP clients (T082/T083)
- Removing Anthropic/OpenAI from `requirements.txt`
- Payments, media T079 content rewrite (unless one-line cross-link)
