# CONTEXT — WineAI (wineia)

> Read first. Product milestones: [`docs/ROADMAP.md`](docs/ROADMAP.md). Commercial launch checklist: [`docs/COMMERCIAL-LAUNCH.md`](docs/COMMERCIAL-LAUNCH.md). Micro-tasks: [`docs/ROADMAP-TASKS.md`](docs/ROADMAP-TASKS.md).

## Primary objective (current)

**T050** — Privacy/terms links at opt-in (COMMERCIAL-LAUNCH #60). At pre-sale create and/or first WhatsApp activation, surface a Portuguese notice with links to privacy policy and terms of service; persist consent metadata when the user opts in.

The comparison contract is [`docs/specs/sdd/T050-privacy-terms-opt-in-sdd.md`](docs/specs/sdd/T050-privacy-terms-opt-in-sdd.md). Its **Expected work** list (EW-01…) is what the reviewer checks against the builder report. Do not add behavior that list does not name. On conflict, the SDD Expected work table wins over PLAN.md / SPEC.md.

**Parallel note:** Another agent may run **T071** in parallel. Do **not** implement T051/T070/T071. Do **not** edit `docs/COMMERCIAL-LAUNCH.md` item 68 / T071 files. You may check CL #60 only. If touching `docs/ROADMAP-TASKS.md` or `docs/specs/sdd/INDEX.md`, change **only the T050 line/row**.

## Priority / skip (parent, 2026-11-18)

| Item | Action |
|------|--------|
| **T040–T043** (payments) | **Parked.** Do not work. |
| **T004** | Skip (GitHub admin). |
| **T051 / T070 / T071** | Do **not** implement (T071 may run in parallel). |
| **This run** | **T050** only. |

## Decisions already made (parent defaults, 2026-11-18)

| Topic | Decision |
|-------|----------|
| Surfaces | At **pre-sale create** and/or first WhatsApp activation path, Portuguese notice with links to privacy policy + terms. |
| URLs | Env `PRIVACY_POLICY_URL`, `TERMS_OF_SERVICE_URL` via `core/config`. If unset, documented placeholders `https://example.com/privacy` / `https://example.com/terms` in copy/docs only — do **not** block registration in MVP when unset. |
| Consent fields | Persist on customer/pre-sale: `privacy_terms_version` (string, e.g. `2026-11-18`) and `privacy_terms_accepted_at` (UTC ISO). Version constant in domain or config. |
| Copy | Prefer WhatsApp/pre-sale message text including the two links; keep handlers thin; domain owns rules. |
| Out of repo | No full legal PDF in repo; no payment fields; no export/delete (T051). |
| Ops | Update PRODUCTION/DEPLOYMENT lightly if env vars added; mark T050 + CL #60 when EW hold. |
| Git | English Conventional Commits; never `main`. Branch: `feat/t050-privacy-terms-opt-in` (**no** `cursor/` prefix). Parent opens PR. |

## Decisions made by the orchestrator

| Topic | Decision |
|-------|----------|
| Version constant | Domain constant `PRIVACY_TERMS_VERSION = "2026-11-18"` in `domain/privacy_terms.py`. |
| URL defaults | Config returns placeholder URLs when env unset so message builders always have link text; registration never fails solely because URLs are unset. |
| Persist when | Set `privacy_terms_version` + `privacy_terms_accepted_at` when pre-sale is created; copy/stamp on activation. |
| Message | Portuguese notice includes both links; domain helper builds notice text; create/activate responses include `privacy_terms_notice`. |
| Models | Add optional fields to customer and pre-sale models/serialization; migration-on-read leaves missing as `None` until accepted. |
| Handlers | Thin: parse HTTP, call domain; no business rules in API layer. |
| CL #60 | Check complete when EW hold; do not touch CL #68 / T071. |

## Out of scope

- T040–T043 payments / provider choice.
- T004 GitHub admin.
- T051 LGPD export/delete.
- T070 / T071 (parallel agent may own T071).
- Full legal PDF / markdown legal text in repo.
- Blocking registration when privacy/terms URLs are unset.
- New pip dependencies; payment fields.

## Relevant files

| File | Role |
|------|------|
| `docs/specs/sdd/T050-privacy-terms-opt-in-sdd.md` | Stub → expand to T031-style with Expected work EW-xx |
| `docs/specs/sdd/T031-scheduler-deploy-cd-sdd.md` | Template for SDD + EW style |
| `docs/specs/sdd/T031-builder-report.md` | Template for builder report |
| `core/config.py` | Add `PRIVACY_POLICY_URL`, `TERMS_OF_SERVICE_URL` |
| `domain/privacy_terms.py` | Version, notice, consent metadata |
| `domain/models/customer.py` | Consent fields |
| `domain/models/pre_sale_customer.py` | Consent fields |
| `domain/services/pre_sale_customer_service.py` | Opt-in surface + persist |
| `docs/COMMERCIAL-LAUNCH.md` | Item #60 only |
| `docs/operations/PRODUCTION.md`, `docs/DEPLOYMENT.md` | Ops env documentation |
| `docs/ROADMAP-TASKS.md`, `docs/specs/sdd/INDEX.md` | T050 status only |
| `PLAN.md`, `SPEC.md` | Plan/spec updates for T050 |
| `docs/specs/sdd/T050-builder-report.md` | Builder report for reviewer judge |

## Acceptance criteria

See EW-01… in the SDD. In short:

- [ ] Portuguese privacy/terms notice with links at pre-sale create and/or first WhatsApp activation.
- [ ] `PRIVACY_POLICY_URL` / `TERMS_OF_SERVICE_URL` via `core/config`; placeholders when unset; do not block registration.
- [ ] Persist `privacy_terms_version` + `privacy_terms_accepted_at` on opt-in; version constant.
- [ ] Domain owns rules; handlers thin; unit tests; coverage ≥ 95% if code changes; ruff + import style.
- [ ] No T051/T070/T071/payments work; no legal PDF; no CL #68 edits.
- [ ] PRODUCTION / DEPLOYMENT / CL #60 / ROADMAP-TASKS T050 / INDEX T050 updated when EW hold.
- [ ] Builder report + reviewer judge accept (each EW vs change list AND diff → match|gap|extra).

## Git policy (fixed)

Branch: `feat/t050-privacy-terms-opt-in` from `origin/main` (no `cursor/` prefix — see [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md)). **Never push to `main`.** Conventional Commits, English, lowercase subject. Parent creates the GitHub PR; leave PR URL unset if ManagePullRequest is parent-owned. Commit bodies wrap at 72 characters (commitlint `body-max-line-length` is 100).

## Agent handoff

On-call: [`.cursor/agents/on-call.md`](.cursor/agents/on-call.md).

Builder report path: `docs/specs/sdd/T050-builder-report.md` (one row per Expected work ID, files, done or skipped, plus Files touched). The reviewer reads that file, the SDD, and the diff, and is the judge. The reviewer does not edit any file.
