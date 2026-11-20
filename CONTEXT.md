# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T082** — Grok chat + vision client; wire `ia_service` text + image paths to xAI as primary (ADR 0007).

| Order | Task | Focus | Status |
|-------|------|--------|--------|
| 1 | **T081** | ADR 0007 | done on `main` (#76) |
| 2 | **T082** | Grok chat + vision → `ia_service` | **THIS RUN** |
| 3 | **T083** | Grok STT replaces Whisper | later |
| 4 | **T084** | Ops/docs / `XAI_API_KEY` Secret Manager | later (user already has key offline) |

Epic: [`docs/specs/sdd/T080-grok-ia-stack-sdd.md`](docs/specs/sdd/T080-grok-ia-stack-sdd.md)  
Slice: [`docs/specs/sdd/T082-grok-chat-vision-client-sdd.md`](docs/specs/sdd/T082-grok-chat-vision-client-sdd.md)  
ADR: [`docs/adrs/0007-xai-grok-ia-stack.md`](docs/adrs/0007-xai-grok-ia-stack.md)

Branch: `cursor/t082-grok-chat-vision-afd2` (from `main`).

## Priority / skip

| Item | Action |
|------|--------|
| **T040–T043** payments | **Parked**. Do not implement. |
| **T083** STT | **Out of scope** this run — keep Whisper. |
| **T084** full ops rewrite | Optional light docs (`XAI_API_KEY` in config.example / DEPLOYMENT one-liner OK); full Secret Manager table is T084. |
| **T079** | Do not block T082. |
| Live xAI calls in CI | **Forbidden** — mock HTTP only. |

## Decisions locked

| Topic | Decision |
|-------|----------|
| Provider | xAI Grok per ADR 0007 |
| Model | Pin `grok-4.7` (or env `XAI_API_MODEL` / `GROK_API_MODEL` with that default) |
| Auth | `XAI_API_KEY` from env; optional `config.json` fallback like other AI keys |
| HTTP | `requests` only — **no** new pip SDK |
| Surface | Mirror `ClaudeClient.generate(system_prompt, user_prompt, image_*=optional)` so `IAService` swaps cleanly |
| Vision | JPEG/PNG base64 (same as T078 inbound); Portuguese Gastón prompts unchanged |
| Budget | Existing Claude daily call budget helpers still wrap successful generations (rename optional; do not break T061) |
| Claude client | May remain in tree unused for rollback; primary path is Grok |
| Git | Never `main`; PR via ManagePullRequest (parent if subagent lacks tool); Conventional Commits EN; body lines ≤100 |

## Relevant files

- `infrastructure/external/claude_client.py` — pattern to mirror
- `domain/services/ia_service.py` — swap default generator to Grok
- `tests/unit/infrastructure/test_claude_client.py` — parallel Grok tests
- `tests/unit/domain/test_ia_service.py`
- `config.example.json` — add `XAI_API_KEY` / model
- Composition / handlers that construct `IAService`

## Acceptance criteria

- [x] `infrastructure/external/` Grok client: text + optional image; mocked unit tests
- [x] `ia_service` text + vision paths use Grok by default
- [x] Broadcast / suggestions still one-gen-per-slot semantics
- [x] Import style (`quality/check_import_style.py`); no `domain` → new SDK; prefer not adding domain→infra if already present — keep same DI style as today
- [x] Coverage / ruff / pytest green
- [x] ROADMAP-TASKS T082 checked; INDEX + T082 SDD updated
- [ ] PR to `main`; CI green

## Out of scope

- Replacing Whisper (T083)
- Asking user for API key value / logging secrets
- Removing `anthropic` from requirements
- Live A/B quality eval
