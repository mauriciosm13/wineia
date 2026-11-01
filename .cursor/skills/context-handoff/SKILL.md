---
name: context-handoff
description: Orchestrator writes CONTEXT.md once. Other agents read it first and do not ask again.
---

The orchestrator writes CONTEXT.md once, at the project root or at `.agents/context.md`. Include the goal, requirements, decisions already made, relevant files, and acceptance criteria.

Other agents read that file before starting. Do not ask again for anything already written there.
