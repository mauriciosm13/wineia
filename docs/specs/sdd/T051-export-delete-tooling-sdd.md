# SDD — Export/delete tooling (T051)

**Status:** implemented  
**Task:** [T051](../../ROADMAP-TASKS.md)  
**Comparison contract:** this Expected work list is what the reviewer checks against [T051-builder-report.md](./T051-builder-report.md).

## Problem

LGPD / commercial launch item #62 requires an export and delete path for a customer by phone. Operators today can CRUD customers over `/customers`, but there is no documented export dump or anonymize/erase flow. Recommendation history and future financial records must not be hard-deleted without an explicit retention policy.

## Goals

- Operator-facing HTTP under the existing customer API (same auth model as `/customers`: **no app auth** — internal/operator only) to export customer PII as JSON and to anonymize (erase) a customer by phone.
- Domain owns export payload shape and erase rules; handlers stay thin; Datastore via existing repository patterns.
- Ops runbook for how to run export/erase and what is / is not deleted; PRODUCTION documents the new routes and the unauthenticated risk.

## Non-goals

- T040–T043 payments; T004.
- T070 ownership (PRODUCTION route updates for these paths are in scope and help T070).
- App auth, OIDC, or `X-Job-Internal-Secret` on these paths (prefer customer paths for operator ergonomics).
- Hard-delete of recommendation history or financial records.
- Export of pre-sale-only leads with no Customer row.
- New pip dependencies.

## Behavior

### Routes

| Method | Path | Result |
|--------|------|--------|
| `GET` | `/customers/{phone}/export` | `200` JSON export; `404` if no Customer for `phone` |
| `POST` | `/customers/{phone}/erase` | `200` JSON with anonymized customer (+ erase metadata); `404` if no Customer |

Same unauthenticated surface as other `/customers*` routes. Document as internal/operator only.

### Export payload

Top-level object (no secrets, no Twilio/Claude keys):

| Field | Source |
|-------|--------|
| `phone`, `name`, `status`, `plan`, `plan_tier`, `weekly_education_opt_in`, `preferences` | Customer |
| `privacy_terms_version`, `privacy_terms_accepted_at` | Customer consent |
| `created_at`, `last_message_at`, `last_recommendation_at`, `recommendation_window_started_at`, `recommendation_send_count_7d`, `messages_sent_today`, `daily_reset` | Customer counters / timestamps |
| `pre_sale` | Optional object when a PreSaleCustomer exists with `whatsapp == phone`: `name`, `email`, `whatsapp`, `preferences`, consent fields, `created_at`. `null` if none. |

### Erase (anonymize)

When Customer exists:

1. Set `name` = `"REDACTED"`, `preferences` = `[]`, `status` = `canceled`, `weekly_education_opt_in` = `false`, `privacy_terms_version` = `None`, `privacy_terms_accepted_at` = `None`. Keep `phone` as Datastore key. Retain `plan` / `plan_tier` and operational counters (not PII display fields).
2. If a PreSaleCustomer is found with `whatsapp == phone`, **delete** that pre-sale entity (email is the Datastore key; leaving a REDACTED row would retain the email key).
3. Do **not** hard-delete recommendation history or financial records (none implemented for payments yet). Document this in the runbook.
4. Response: anonymized customer dict plus `erased: true` and `pre_sale_deleted: bool`.

### Repositories

- `PreSaleCustomerRepository.get_by_whatsapp(whatsapp)` → lead or `None`.
- `PreSaleCustomerRepository.delete(email_or_lead)` → removes the pre-sale entity (Datastore: delete by email key).
- Fake and Datastore implementations updated. Customer repository `update` reused for anonymized customer writes.

### Domain

`CustomerPrivacyService(customer_repository, pre_sale_repository)`:

- `export_customer(phone)` → export dict or `None`
- `erase_customer(phone)` → result dict or `None`

Handlers call the service only; no anonymize rules in the API layer.

### Ops

New `docs/operations/LGPD-EXPORT-DELETE.md`: curl examples, auth risk, anonymize vs retain (recommendation history / financial not hard-deleted). Link from PRODUCTION Related + routes table. CL #62 checked when EW hold.

## Expected work

The builder implements only these items. The reviewer marks each **match**, **gap**, or **extra**.

| ID | Must be true when the work is done | Where |
|----|-------------------------------------|--------|
| EW-01 | `PreSaleCustomerRepository` gains abstract `get_by_whatsapp` and `delete`. Datastore impl queries `whatsapp ==` and deletes by email key. `FakePreSaleCustomerRepository` supports both (index by whatsapp for lookup). Unit tests cover fake behavior used by the privacy service. | `domain/repositories/pre_sale_customer_repository.py`, `infrastructure/repositories/datastore_pre_sale_customer_repository.py`, `tests/fakes/repositories.py` |
| EW-02 | `CustomerPrivacyService.export_customer(phone)` returns the export shape in Behavior (customer fields + optional `pre_sale`); `None` when customer missing. No secrets in the payload. Unit tests: export with and without pre-sale; missing customer. | `domain/services/customer_privacy_service.py`, `tests/unit/domain/test_customer_privacy_service.py` |
| EW-03 | `CustomerPrivacyService.erase_customer(phone)` anonymizes as in Behavior (REDACTED / canceled / consent cleared / opt-in false), persists via customer `update`, deletes linked pre-sale when present, returns result with `erased: true` and `pre_sale_deleted`. `None` when customer missing. Does not call any recommendation-history delete. Unit tests: erase with and without pre-sale; missing customer; assert REDACTED fields. | same |
| EW-04 | Customer handler routes `GET .../export` and `POST .../erase` (phone may be URL-encoded); thin handlers call the privacy service; 200 JSON or 404. Existing `/customers`, `/customers/{phone}`, pre-sale paths unchanged in behavior. Route unit tests cover dispatch for export and erase. | `api/handlers/customer_handler.py`, `tests/unit/api/test_customer_routes.py` |
| EW-05 | Ops: `docs/operations/LGPD-EXPORT-DELETE.md` documents export/erase curl examples, unauthenticated operator-only risk, anonymize vs retain (recommendation history / financial not hard-deleted). `PRODUCTION.md` lists the two new paths in the HTTP routes table and links the runbook under Related. | those files |
| EW-06 | Only after EW-01–EW-05 and EW-07 hold: `ROADMAP-TASKS.md` checks **only** the T051 line; `COMMERCIAL-LAUNCH.md` checks **only** item 62; this SDD status is `implemented`; `INDEX.md` T051 row is `implemented`. | those files (T051 / #62 only) |
| EW-07 | Diff does not implement payments T040–T043, T004, or own T070 deliverables beyond PRODUCTION route accuracy for these paths. Domain/core coverage stays ≥ 95%. Ruff + import style pass. | whole diff |

## Builder report

After implementation, write `docs/specs/sdd/T051-builder-report.md`:

| ID | Result (`done` or `skipped`) | Files | What changed |
|----|-------------------------------|-------|----------------|

Add a **Files touched** list of every path in the diff and the exact test commands with results. The reviewer treats any path not justified by an ID as **extra**.

## Reviewer comparison

Read this file, the builder report, and the diff. Return only:

- One line per ID: `EW-xx match|gap — evidence`
- Extras: paths or behavior not in the table
- Bugs that break an ID
- Verdict: accept or reject

Do not implement.

## Related

- [CONTEXT.md](../../../CONTEXT.md)
- [COMMERCIAL-LAUNCH.md](../../COMMERCIAL-LAUNCH.md) item 62
- [PRODUCTION.md](../../operations/PRODUCTION.md)
- [LGPD-EXPORT-DELETE.md](../../operations/LGPD-EXPORT-DELETE.md) (added by this task)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-10 | Initial SDD stub |
| 2026-11-18 | Expanded to T031-style Expected work EW-01–EW-07 (export/erase under `/customers`, anonymize, runbook) |
