# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**Inbound WhatsApp Twilio media (T074–T079).** Customers can send photos and voice notes; today the webhook only reads `Body` and **silently ignores** media-only messages. Epic research: [`docs/specs/sdd/T074-inbound-whatsapp-media-sdd.md`](docs/specs/sdd/T074-inbound-whatsapp-media-sdd.md).

Execute **in order**. Do not skip ahead of a failing slice.

| Order | Task | Focus |
|-------|------|--------|
| 1 | **T075** | Parse `NumMedia` / `MediaUrl0` / `MediaContentType0`; route media-only into domain (no silent ignore) |
| 2 | **T076** | Download `MediaUrl0` with Twilio HTTP Basic Auth + size/MIME guards |
| 3 | **T077** | Audio → STT → existing text IA path (ADR if new dep) |
| 4 | **T078** | Image → multimodal Claude + caption; unsupported MIME Portuguese reply |
| 5 | **T079** | Ops docs + tests / LGPD ephemeral media notes; mark epic progress |

SDD contracts (normative Expected work before implement):

- [T075](docs/specs/sdd/T075-twilio-media-parser-sdd.md)
- [T076](docs/specs/sdd/T076-twilio-media-download-sdd.md)
- [T077](docs/specs/sdd/T077-inbound-audio-stt-sdd.md)
- [T078](docs/specs/sdd/T078-inbound-image-vision-sdd.md)
- [T079](docs/specs/sdd/T079-inbound-media-ops-tests-sdd.md)

For each slice: expand SDD with **Expected work EW-xx** → implement only those items → builder report → **reviewer (Composer 2.5)** as judge vs EW-xx + git diff (not only the diff).

## Priority / skip (parent, 2026-11-18)

| Item | Action |
|------|--------|
| **T040–T043** payments | **Parked.** User contacting Asaas separately. Do not implement payments. |
| Dependabot Actions PRs | Do not own. |
| **This run** | **T075 then T076** fully. Continue **T077–T079** if time/clarity allows; otherwise stop after T076 with open STT/vision decisions documented. |

## Decisions already made (parent defaults)

| Topic | Decision |
|-------|----------|
| Twilio fields | `NumMedia`, `MediaUrl0`, `MediaContentType0`; WhatsApp ≤1 attachment |
| Download auth | HTTP Basic Auth with existing `TWILIO_ACCOUNT_SID` + `TWILIO_AUTH_TOKEN`; follow 307 CDN redirect |
| Architecture | Clean Architecture: parser/handler HTTP; domain orchestration; infrastructure for Twilio fetch / STT / vision. Domain must not import infrastructure. |
| Existing gates | Keep Twilio signature, webhook rate limits, on-demand entitlements, Claude daily budget, T032 async outbound enqueue |
| Fail closed | Media present but unprocessable → Portuguese reply (no silent 200 with no product response) |
| Non-goals v1 | Outbound media; video/docs/stickers/contacts (unsupported copy); long-term Datastore blob storage |
| Quota | Successful media turn counts as one on-demand IA turn (same counter as text) unless SDD says otherwise |
| Git | English Conventional Commits; **never `main`**. Branch: `feat/<topic-kebab>` — **no `cursor/` prefix**. Use `ManagePullRequest` with `skip_branch_prefix_check: true`, `base_branch: main`. |
| SDD judge | Reviewer compares builder report + Expected work table + diff |

## Open decisions (orchestrator may propose defaults in SDD before implement)

| Topic | Notes |
|-------|--------|
| STT provider (T077) | Prefer no new vendor if Anthropic/Claude can transcribe; else ADR for new dep |
| Claude multimodal constraints (T078) | Size/MIME caps; document in SDD |
| Max download size (T076) | Propose sensible cap (e.g. images ≤5MB per Twilio guidance; audio within overview limits) |

## Out of scope

- Payments / Asaas integration
- Changing ENTRY/SUPERIOR product promises beyond counting media as one on-demand turn
- Outbound WhatsApp media sends

## Relevant files

| File | Role |
|------|------|
| `api/handlers/whatsapp_handler.py` | Webhook entry; today skips empty Body |
| `core/utils/twilio_webhook_parser.py` | Body-only extract today |
| `domain/services/messaging_service.py` | `process_incoming_message` |
| `domain/services/ia_service.py` | Text IA |
| `infrastructure/external/claude_client.py` | Claude text client |
| `infrastructure/external/twilio_whatsapp_client.py` | Outbound Twilio |
| `docs/specs/sdd/T074-*.md` … `T079-*.md` | Contracts |
| `docs/operations/WHATSAPP-COMPLIANCE.md` | Update in T079 |
| `docs/operations/PRODUCTION.md` | Update in T079 |
| `docs/operations/DATA-RETENTION.md` | Ephemeral media note (T079) |

## Acceptance criteria (run)

- [x] T075: media-only webhook payloads enter domain path; unit tests; SDD EW + builder report + reviewer pass
- [ ] T076: authenticated download + MIME/size guards; unit tests with fakes; SDD EW + builder report + reviewer pass
- [ ] PRs on `feat/...` branches (no `cursor/`); CI green; coverage ≥ 95% on domain/core; ruff + import style
- [ ] Text-only path unchanged
- [ ] CONTEXT.md kept current for handoff
- [ ] If T077–T079 not finished: document remaining open decisions and next slice in the parent summary

## Handoff notes

- Branch in progress: `feat/t075-twilio-media-parser`
- Next slice after T075 merge/review: **T076** (`docs/specs/sdd/T076-twilio-media-download-sdd.md`)
- Media-only currently returns Portuguese `MEDIA_UNAVAILABLE_MESSAGE` until download/STT/vision land

## Parent note

Roadmap docs for T074–T079 already merged on `main` (PR #58). Implement code next; do not re-litigate the epic research in T074 unless needed for EW expansion.
