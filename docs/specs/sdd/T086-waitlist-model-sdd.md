# SDD — Waitlist model + Datastore (T086)

**Status:** draft  
**Task:** [T086](../../ROADMAP-TASKS.md) · parent [T085](./T085-launch-waitlist-sdd.md)

## Goals

- Domain model for waitlist lead: phone, name, email, birth_date, created_at, updated_at.
- Age validation helper (default min age 18; env e.g. `WAITLIST_MIN_AGE`).
- Datastore kind (e.g. `WaitlistLead`) + repository interface; unique constraint strategy (phone and/or email).
- Unit tests for validation and upsert semantics.

## Acceptance criteria

- [ ] Pure domain tests for under-age / missing fields
- [ ] Repository fake in unit tests; no emulator required

## Related

- [T085](./T085-launch-waitlist-sdd.md)

## Revision history

| Date | Change |
|------|--------|
| 2026-11-20 | Initial draft |
