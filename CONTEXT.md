# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T080–T084** — migrate IA stack to **xAI Grok** (text + vision + STT) for test/launch cost (single vendor vs Claude Sonnet + OpenAI Whisper).

| Order | Task | Focus | Status |
|-------|------|--------|--------|
| 0 | **T080** | Epic + cost assumptions | draft SDD |
| 1 | **T081** | ADR 0007; supersede ADR 0006 | draft |
| 2 | **T082** | Grok chat + vision client → `ia_service` | draft |
| 3 | **T083** | Grok STT replaces Whisper | draft |
| 4 | **T084** | Ops/docs / `XAI_API_KEY` / budget | draft |

Epic: [`docs/specs/sdd/T080-grok-ia-stack-sdd.md`](docs/specs/sdd/T080-grok-ia-stack-sdd.md).  
Branch (roadmap docs): `cursor/t080-grok-model-migration-afd2`.

## Priority / skip (parent, 2026-11-19)

| Item | Action |
|------|--------|
| **T040–T043** payments | **Parked** (Asaas contact in progress). Do not implement. |
| **T079** media ops/docs | Still open; can land before or with T084. |
| **T075–T078** | Done on `main` — media path exists; Grok slices depend on it. |

## Decisions locked

| Topic | Decision |
|-------|----------|
| IA vendor (test/launch) | **xAI Grok** for chat + vision + STT (T080–T084). |
| Why not stay on Claude+Whisper | Two vendors; Sonnet+Whisper higher unit cost; Grok unifies keys/billing. |
| Why not Haiku-only | Cheaper tokens possible, but still needs separate STT vendor. |
| STT today (until T083) | ADR 0006 OpenAI Whisper — to be superseded by ADR 0007. |
| Vision today (until T082) | Claude multimodal — replaced by Grok image input. |
| Architecture | Domain injectable callables; prefer `requests`, no new SDK unless ADR says so. |
| Git | Never commit to `main`; PR from feature branch. |

## Acceptance criteria (roadmap docs run)

- [x] T080–T084 listed in ROADMAP-TASKS + SDD INDEX
- [x] ROADMAP M3 + COMMERCIAL-LAUNCH #29 point at T080
- [x] Epic + slice SDDs drafted
- [ ] Implementation slices (T081–T084) — separate runs

## Out of scope this docs PR

- Code changes to Claude/Whisper clients
- Live xAI integration or quality A/B
