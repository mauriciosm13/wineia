# SDD — Launch compliance documentation (T073)

**Status:** implemented  
**Task:** [T073](../../ROADMAP-TASKS.md)  
**Comparison contract:** this Expected work list is what the reviewer checks against [T073-builder-report.md](./T073-builder-report.md).

## Problem

Commercial launch still blocks on documentation for WhatsApp/Twilio messaging policy (CL #16) and LGPD data retention (CL #61). Operators also need an explicit production recommendation for `CLAUDE_DAILY_CALL_BUDGET` (`0`/unset remains unlimited in code).

## Goals

- Add `docs/operations/WHATSAPP-COMPLIANCE.md` covering templates vs free-form, opt-in, cancelar, 24h window notes, Twilio/Meta policy links, and WineAI send paths.
- Add `docs/operations/DATA-RETENTION.md` covering PII inventory, retention intent, export/erase (T050/T051), no payment data yet, and Claude/Twilio subprocessors.
- Document a suggested production starting value for `CLAUDE_DAILY_CALL_BUDGET` (**500**, ops-tunable) in DEPLOYMENT and LAUNCH-CHECKLIST, while restating that **`0`/unset = unlimited**.
- Cross-link from COMMERCIAL-LAUNCH (#16/#61), ENGINEERING_MANUAL, and LAUNCH-CHECKLIST; add Related links from PRODUCTION.
- Add and complete micro-task **T073**; flip only CL #16 and #61.

## Non-goals

- T040–T043 payments implementation or provider choice.
- T004 GitHub admin; Dependabot; operator auth.
- Runtime `api/` / `domain/` / `infrastructure/` / `tests/` changes.
- Changing the code default for `CLAUDE_DAILY_CALL_BUDGET` (stays `0`).
- Registering WhatsApp templates in Twilio/Meta consoles (document only).
- Flipping any CL item other than #16 and #61, or any micro-task other than T073.

## Behavior

### WhatsApp compliance doc

`docs/operations/WHATSAPP-COMPLIANCE.md` must explain, in English:

1. **Templates vs free-form** — Meta/WhatsApp business messaging: approved templates for business-initiated outbound outside the customer-care session; free-form session replies inside the window.
2. **Opt-in** — customers enter via pre-sale / activation with privacy/terms notice (T050); education requires `weekly_education_opt_in`.
3. **Cancelar** — inbound keyword updates Datastore only; no outbound WhatsApp text on cancel.
4. **24h window** — note that business-initiated messages outside the customer-care window typically need approved templates; WineAI scheduled/education sends are business-initiated and must stay aligned with Twilio/Meta policy.
5. **Policy links** — official Twilio and Meta WhatsApp messaging policy / template docs (external URLs).
6. **WineAI send paths today** — webhook IA reply (+ limit warning) via Cloud Tasks `send_message`; scheduled recommendations job; weekly education job; `/ia/suggestions` can send synchronously (must not be public).

### Data retention doc

`docs/operations/DATA-RETENTION.md` must explain:

1. **PII stored** — Customer and PreSaleCustomer fields (phone, name, email/whatsapp on pre-sale, preferences, consent metadata, plan/tier, counters).
2. **Retention intent** — keep active customer records while the relationship is live; erase/anonymize on operator request (T051); recommendation history not hard-deleted without a stronger policy.
3. **Export / erase** — point at T050 (consent at opt-in) and T051 / `LGPD-EXPORT-DELETE.md`.
4. **Payments** — no payment/card data in product yet; payment subprocessor deferred to CL #63.
5. **Subprocessors** — Twilio (WhatsApp delivery) and Anthropic/Claude (generation); GCP Datastore/Cloud Run as primary processor infrastructure.

### Claude daily call budget ops note

In `docs/DEPLOYMENT.md` (global Claude budget section) and `docs/LAUNCH-CHECKLIST.md` (secrets/env and/or entitlements section):

- Restate **`0` or unset = unlimited**.
- Recommend production set a positive ceiling; suggested starting value **`500`** calls per UTC day, clearly labeled as an **ops-tunable guess** (not a hard product constant).

## Expected work

The builder implements only these items. The reviewer marks each **match**, **gap**, or **extra**.

| ID | Must be true when the work is done | Where |
|----|-------------------------------------|--------|
| EW-01 | `docs/operations/WHATSAPP-COMPLIANCE.md` exists and covers: templates vs free-form session messaging; opt-in; cancelar (no outbound on cancel); 24h customer-care window notes; links to Twilio and Meta WhatsApp policy/template docs; WineAI send paths (webhook reply via queue, scheduled recommendations, weekly education, and note on `/ia/suggestions`). | `docs/operations/WHATSAPP-COMPLIANCE.md` |
| EW-02 | `docs/operations/DATA-RETENTION.md` exists and covers: PII inventory for Customer / PreSaleCustomer; retention intent; export/erase via T050/T051 (link `LGPD-EXPORT-DELETE.md`); no payment data yet; Twilio and Anthropic/Claude as subprocessors. | `docs/operations/DATA-RETENTION.md` |
| EW-03 | `docs/DEPLOYMENT.md` and `docs/LAUNCH-CHECKLIST.md` document that `CLAUDE_DAILY_CALL_BUDGET` **`0`/unset = unlimited**, and recommend a production starting value of **`500`** labeled as an ops-tunable guess. | those files |
| EW-04 | `docs/COMMERCIAL-LAUNCH.md` item **16** is checked and links to `operations/WHATSAPP-COMPLIANCE.md`; item **61** is checked and links to `operations/DATA-RETENTION.md`. No other CL checkbox flips. | `docs/COMMERCIAL-LAUNCH.md` |
| EW-05 | `docs/ENGINEERING_MANUAL.md` lists both new ops docs; `docs/LAUNCH-CHECKLIST.md` links both; `docs/operations/PRODUCTION.md` Related section links both. | those files |
| EW-06 | Only after EW-01–EW-05 and EW-07 hold: `ROADMAP-TASKS.md` adds and checks **only** T073; this SDD status is `implemented`; `INDEX.md` has a T073 `implemented` row. Do not flip T004 or T040–T043. | those files |
| EW-07 | Diff is docs-only for T073 deliverables (plus `CONTEXT.md` handoff). No runtime `api/`, `domain/`, `infrastructure/`, or `tests/` product code. No payments implementation. | whole diff |

## Builder report

After implementation, write `docs/specs/sdd/T073-builder-report.md`:

| ID | Result (`done` or `skipped`) | Files | What changed |
|----|-------------------------------|-------|----------------|

Add a **Files touched** list of every path in the diff and the exact verification commands with results. The reviewer treats any path not justified by an ID as **extra**.

## Reviewer comparison

Read this file, the builder report, and the diff. Return only:

- One line per ID: `EW-xx match|gap — evidence`
- Extras: paths or behavior not in the table
- Bugs that break an ID or would mislead an operator at go-live
- Verdict: accept or reject

Do not implement.

## Related

- [CONTEXT.md](../../../CONTEXT.md)
- [COMMERCIAL-LAUNCH.md](../../COMMERCIAL-LAUNCH.md) — #16, #61
- [LAUNCH-CHECKLIST.md](../../LAUNCH-CHECKLIST.md)
- [ENGINEERING_MANUAL.md](../../ENGINEERING_MANUAL.md)
- [DEPLOYMENT.md](../../DEPLOYMENT.md)
- [operations/PRODUCTION.md](../../operations/PRODUCTION.md)
- [operations/LGPD-EXPORT-DELETE.md](../../operations/LGPD-EXPORT-DELETE.md)
- [T061 SDD](./T061-global-claude-budget-stop-sdd.md)
- [INDEX.md](./INDEX.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-18 | Initial SDD with Expected work EW-01–EW-07 from parent T073 decisions |
| 2026-11-18 | Status `implemented` after EW-01–EW-07 hold |
