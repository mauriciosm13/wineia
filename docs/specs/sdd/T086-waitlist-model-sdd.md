# SDD — Waitlist model + Datastore (T086)

**Status:** implemented  
**Task:** [T086](../../ROADMAP-TASKS.md) · parent [T085](./T085-launch-waitlist-sdd.md)

## Goals

- Domain model for waitlist lead: phone, name, email, birth_date, created_at, updated_at.
- Age validation helper (default min age 18; env e.g. `WAITLIST_MIN_AGE`).
- Datastore kind (e.g. `WaitlistLead`) + repository interface; unique constraint strategy (phone and/or email).
- Unit tests for validation and upsert semantics.

## Unique key

**Phone** (E.164) is the Datastore entity id / upsert key. Email is stored lower-case and updated on upsert; it is not a second unique key in this slice.

## Acceptance criteria

- [x] Pure domain tests for under-age / missing fields
- [x] Repository fake in unit tests; no emulator required

## Related

- [T085](./T085-launch-waitlist-sdd.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-20 | Initial draft |
| 2026-11-20 | Implemented: `WaitlistLead`, phone upsert, `WAITLIST_MIN_AGE` |
