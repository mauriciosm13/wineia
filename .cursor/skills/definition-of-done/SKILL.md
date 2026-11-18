---
name: definition-of-done
description: Reviewer checks CONTEXT.md acceptance criteria. CI owns tests, lint, types, and format.
---

The reviewer checks the work against the acceptance criteria in CONTEXT.md.

CI still owns tests, lint, types, and format.

When the change adds, removes, or alters HTTP routes or other production behavior, confirm `docs/operations/PRODUCTION.md` is updated in the same PR (see also `.github/PULL_REQUEST_TEMPLATE.md` and the Pull request checklist in `docs/GIT_WORKFLOW.md`).
