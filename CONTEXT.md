# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T077 + T078** — turn downloaded inbound WhatsApp media into product IA replies.

| Order | Task | Focus | Branch | Status |
|-------|------|--------|--------|--------|
| 1 | **T077** | Audio → STT → existing text IA path | `feat/t077-inbound-audio-stt` | implemented; reviewer **accept**; pushed |
| 2 | **T078** | Image → multimodal Claude (+ optional `Body` caption) | `feat/t078-inbound-image-vision` (stacked on T077) | implemented; reviewer **accept** |

Epic: [`docs/specs/sdd/T074-inbound-whatsapp-media-sdd.md`](docs/specs/sdd/T074-inbound-whatsapp-media-sdd.md).

## Priority / skip (parent, 2026-11-18)

| Item | Action |
|------|--------|
| **T040–T043** payments | **Parked**. Do not implement. |
| **T079** ops/docs | Optional; not required this run (PRODUCTION/DEPLOYMENT already note media). |

## Decisions locked

| Topic | Decision |
|-------|----------|
| STT (T077) | Claude cannot STT. **ADR 0006:** OpenAI Whisper via `requests` (`whisper-1`, `language=pt`). No new pip dep. |
| Vision (T078) | Claude multimodal base64; JPEG/PNG; caption=`Body`; 5 MiB raw (T076). |
| Quota | One on-demand turn per successful media→reply. Claude budget at Claude call sites. |
| Fail closed | Portuguese STT/vision failure copy. |
| Git | `feat/<topic-kebab>`; never `main`. ManagePullRequest unavailable in this environment (`gh pr create` denied); branches pushed for PR. |

## Acceptance criteria (run)

- [x] T077: voice-note → transcription → IA reply (or PT failure); EW + builder + reviewer accept; branch pushed
- [x] T078: image → multimodal IA (+ caption) (or PT failure); EW + builder + reviewer accept; branch pushed
- [x] Text-only / download guards preserved in spirit
- [x] Coverage ≥ 95% domain/core; ruff + import style
- [x] CONTEXT.md kept current

## Open items for parent

- Open/merge PRs: ManagePullRequest tool not available; `gh pr create` returned `Resource not accessible by integration`. Compare URLs:
  - T077: https://github.com/mauriciosm13/wineia/pull/new/feat/t077-inbound-audio-stt
  - T078: https://github.com/mauriciosm13/wineia/compare/main...feat/t078-inbound-image-vision?expand=1 (stack: base can be `feat/t077-inbound-audio-stt` or `main` after T077 merges)
- Production needs `OPENAI_API_KEY` for voice notes (Secret Manager cutover follow-up).
- T079 optional polish still open.
