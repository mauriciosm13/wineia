# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T077 + T078** — turn downloaded inbound WhatsApp media into product IA replies.

| Order | Task | Focus | Branch |
|-------|------|--------|--------|
| 1 | **T077** | Audio → STT → existing text IA path | `feat/t077-inbound-audio-stt` (active) |
| 2 | **T078** | Image → multimodal Claude (+ optional `Body` caption) | stack on T077: `feat/t078-inbound-image-vision` |

Epic research: [`docs/specs/sdd/T074-inbound-whatsapp-media-sdd.md`](docs/specs/sdd/T074-inbound-whatsapp-media-sdd.md).  
Already on `main`: **T075** parser + **T076** download. After successful download, `_handle_media_only` still sends `MEDIA_UNAVAILABLE_MESSAGE` — replace that with STT/vision paths.

SDDs:

- [T077](docs/specs/sdd/T077-inbound-audio-stt-sdd.md) — EW-01…EW-10 locked
- [T078](docs/specs/sdd/T078-inbound-image-vision-sdd.md) — expand EW before implement

Process per slice: expand SDD EW → implement only EW → builder report → **reviewer (Composer 2.5 contract)** judges EW + report + diff → PR on `feat/...` (no `cursor/`).

## Priority / skip (parent, 2026-11-18)

| Item | Action |
|------|--------|
| **T040–T043** payments | **Parked** (user contacting Asaas). Do not implement. |
| **T079** ops/docs | Optional if time after T077/T078; not required this run. |
| **This run** | **T077 then T078** fully. |

## Decisions already made (parent defaults + orchestrator locks)

| Topic | Decision |
|-------|----------|
| STT provider (T077) | Claude **cannot** STT (no audio content block). **ADR 0006:** OpenAI `/v1/audio/transcriptions` via existing `requests` (no new pip dep); model `whisper-1`; `language=pt`. |
| STT MIME | Attempt: ogg/opus/mpeg/mp4/aac. Fail closed (PT copy): amr/3gpp. |
| Vision (T078) | **Claude multimodal** via infrastructure client; JPEG/PNG; optional `Body` caption; prefer vision when image present (caption = Body). Cap = T076 image max 5 MiB. |
| Quota | One on-demand IA turn per successful media→reply path. STT alone does not increment. Claude daily budget at Claude call sites. |
| Fail closed | STT/vision failure → Portuguese unavailable/error copy. |
| Architecture | Clean Architecture; domain never imports infrastructure. Inject download/STT; vision via IAService/ClaudeClient (existing Claude coupling). |
| Non-goals | Outbound media; video/PDF/sticker processing; long-term Datastore blob storage. |
| Git | English Conventional Commits; never commit to `main`. Branch `feat/<topic-kebab>`; ManagePullRequest with `skip_branch_prefix_check: true`, `base_branch: main`. Stack T078 on T077 if both land as separate PRs. |

## Open decisions (for T078 SDD lock)

| Topic | Guidance |
|-------|----------|
| Exact Claude multimodal size cap | Align with T076 image max (5MB) and Anthropic docs; document in T078 SDD |
| Image + non-empty Body | Prefer vision with caption=Body (update text+media regression) |

## Relevant files

| File | Role |
|------|------|
| `domain/services/messaging_service.py` | `_handle_media_only` — STT/vision after download |
| `domain/services/ia_service.py` | Text generation; extend for vision in T078 |
| `infrastructure/external/claude_client.py` | Extend for vision |
| `infrastructure/external/openai_stt_client.py` | T077 STT (new) |
| `infrastructure/external/twilio_media_client.py` | Download (done) |
| `api/handlers/whatsapp_handler.py` | Composition / DI |
| `core/utils/twilio_media.py` | MIME allowlists / size caps / STT-compatible helper |
| `docs/adrs/0006-openai-whisper-stt.md` | STT ADR |
| `docs/specs/sdd/T077-*.md`, `T078-*.md` | Contracts |

## Acceptance criteria (run)

- [ ] T077: voice-note → transcription → IA reply (or explicit PT failure); entitlements + budget; tests; SDD EW + builder report + reviewer accept; PR
- [ ] T078: image → multimodal IA reply with optional caption (or PT failure); unsupported still clear; tests; SDD EW + builder report + reviewer accept; PR
- [ ] Text-only and download guards from T075/T076 unchanged in spirit
- [ ] Coverage ≥ 95% domain/core; ruff + import style
- [ ] CONTEXT.md kept current

## Parent note

User asked to dispatch orchestrator specifically for these two activities after confirming download alone is not enough for product readiness.
