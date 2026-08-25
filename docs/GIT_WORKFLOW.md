# Git Workflow

WineAI uses **Conventional Commits** for commit messages and **semantic PR titles**, aligned with common gateway-style repositories. This keeps history readable and supports automated changelog and release notes later.

---

## Branching

- **`main`** — integration branch; protected by CI (pytest, ruff, coverage, Docker build, conventional commits).
- **Feature branches** — open PRs against `main`; squash or merge per team preference.
- **Releases** — tag `main` with semver `v*.*.*` to trigger production deploy (see [DEPLOYMENT.md](./DEPLOYMENT.md)).

Do **not** rely on auto-deploy from `main` — production is tag- or manual-dispatch only.

---

## Commit message format

```
<type>(<optional scope>): <subject>

<optional body>
```

Examples:

```
feat(customers): add pre-sale registration endpoint
fix(whatsapp): honor daily message cap on recommendations
docs: add engineering manual index
ci: upload coverage artifact on PR builds
```

### Allowed types

| Type | Use |
|------|-----|
| `feat` | New user-facing or API behavior |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Code change without feature/fix |
| `perf` | Performance improvement |
| `test` | Tests only |
| `build` | Build system or dependencies |
| `ci` | CI/CD configuration |
| `chore` | Maintenance, tooling |
| `revert` | Revert a prior commit |

Scope is optional. Subject should be imperative, lowercase (after type), no trailing period.

---

## Enforcement

### Local — `.commitlintrc.yaml`

Extends `@commitlint/config-conventional` with:

- Non-empty type and subject
- Header max length 100 characters

Install commitlint locally if desired; CI is the source of truth on PRs.

### CI — `.github/workflows/conventional-commits.yml`

Two jobs:

1. **commitlint** — validates all commits in a PR (and on push to `main`) via `wagoid/commitlint-github-action@v6`, which reads `.commitlintrc.yaml`.
2. **semantic-pr** — validates PR title against the same type list via `amannn/action-semantic-pull-request@v5`.

PR titles should follow the same type prefix as commits, e.g. `feat: add recommendation content CRUD`.

---

## Pull request checklist

- [ ] Title passes semantic PR check
- [ ] Commits pass commitlint
- [ ] CI green (ruff, pytest, coverage)
- [ ] Docs/RFC/ADR/SPEC updated if behavior or dependencies changed (see [ROADMAP.md](./ROADMAP.md) Engineering Rule)

---

## Related docs

- [ENGINEERING_MANUAL.md](./ENGINEERING_MANUAL.md)
- [DEPLOYMENT.md](./DEPLOYMENT.md) — release tags and deploy workflow
