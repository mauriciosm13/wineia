# CONTEXT — WineAI (wineia) — T079 run

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (this run)

**T079** — inbound media ops docs + unit tests per [`docs/specs/sdd/T079-inbound-media-ops-tests-sdd.md`](docs/specs/sdd/T079-inbound-media-ops-tests-sdd.md).

Rebased onto `main` after **T082/T083** (Grok chat/vision + Grok STT).

| Item | Status |
|------|--------|
| Ops docs | PRODUCTION / WHATSAPP-COMPLIANCE / DATA-RETENTION + threat-model |
| Unit tests | media-only routing, download/unsupported MIME failure copy |
| Roadmap | T079 (+ T074 epic) marked implemented |
| Providers on `main` | **Grok** text/vision + **Grok** STT (`XAI_API_KEY`; ADR 0007) |

Branch: `cursor/t079-inbound-media-ops-afd2` · PR: https://github.com/mauriciosm13/wineia/pull/79

## Priority / skip

| Item | Action |
|------|--------|
| **T040–T043** payments | Parked |
| **T084** Secret Manager XAI table | Later |

## Acceptance criteria

- [x] Ops docs: ephemeral media, entitlements/budget, Grok providers
- [x] Unit tests for media ops paths
- [x] ROADMAP / INDEX / T079 SDD updated
- [x] Rebased onto post-T083 `main`
- [ ] PR #79 CI green + merge
