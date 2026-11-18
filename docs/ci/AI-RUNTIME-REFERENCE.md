# CI reference — AI-Runtime vs WineAI

WineAI **already implements** the patterns described for [AI-Runtime](https://github.com/mauriciosm13/AI-Runtime):

| Pattern | WineAI |
|---------|--------|
| `ci.yml` quality gate | pytest + coverage + ruff + import style |
| `docker.yml` | build without push |
| `conventional-commits.yml` | commitlint + semantic PR |
| Deploy separated from merge | tag / `workflow_dispatch` only ([DEPLOYMENT.md](../DEPLOYMENT.md)) |
| OIDC to cloud | GCP WIF ([adrs/0001-github-oidc-gcp.md](../adrs/0001-github-oidc-gcp.md)) |

**WineAI extras vs AI-Runtime:** coverage artifact, custom import style check, no Postgres service (pure mocks).

**COMMERCIAL-LAUNCH #6:** Dependabot covers supply-chain PRs via [`.github/dependabot.yml`](../../.github/dependabot.yml) (weekly `pip` + `github-actions`). Optional further borrow from AI-Runtime: add a `pip-audit` step in CI (not required when Dependabot is enabled).

Full AI-Runtime workflow notes were used when bootstrapping the sibling `wine-concierge` repo; this repo is the **canonical** backend.
