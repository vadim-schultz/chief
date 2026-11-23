---
name: git-workflow
description: Git workflow — feature branches, CI before push, conventional commits
---

# Git Workflow

Scope: GitHub only. Conventional Commits apply in every language.

## Feature branches

Before making code changes, confirm you are **not** on `main` or `master`.

```bash
git branch --show-current
```

### Always branch from an up-to-date default branch

Starting a new changeset means **sync the default branch first, then branch from its latest commit**. Never branch off whatever happens to be checked out — a stale base produces avoidable merge conflicts and CI failures from changes you never saw.

```bash
git checkout main && git pull   # or master
git checkout -b feat/short-description   # or fix/, chore/, docs/, refactor/, test/
```

- ❌ `git checkout -b feat/new-thing` from a stale `main` or a leftover feature branch
- ✅ `git checkout main && git pull` **then** `git checkout -b feat/new-thing`

If uncommitted work blocks the checkout, stash or commit it before switching — do not silently carry it onto the new branch.

Do not commit directly to `main`/`master`. Only open a pull request from a feature branch.

## CI before push

Before `git push`, run the project's CI pipeline locally and fix failures before pushing.

**Discover the entry point** (check in this order):

1. `scripts/ci.sh` — run `./scripts/ci.sh` (or `./scripts/ci.sh lint` for a faster pre-push check)
2. `tox` — run `tox` (or the project's documented tox env, e.g. `tox -e py312`)
3. `Makefile` — run `make ci`, `make test`, or `make lint` if defined
4. `package.json` — run `npm test`, `npm run lint`, or the project's `ci` script
5. **Fallback** for Python projects: `ruff check`, `ruff format --check`, `mypy`, `pytest`

Do not push while CI is failing. Re-run checks after fixes until green.

In a work package, every chapter passes the local gate on its own branch. Chapter branches stay local. Remote CI runs once, on the pull request into the release branch, and on tags. The chief-of-staff git model defines the local gate.

## GitHub remotes

`gh` is authenticated for GitHub. `gh auth setup-git` makes `gh` the HTTPS credential helper, so `git pull` and `git push` authenticate through it. Pull requests, checks and other GitHub API calls are `gh` subcommands. Commits stay `git commit`.

Detect the host once per repository:

```bash
git remote get-url origin
```

A URL that contains `github.com` is GitHub. Use the same sequence as above: sync the default branch, branch from it, commit with Conventional Commits, run local CI, then push with `git push -u origin HEAD`. In a work package, the chapter branches stay local, and the release is the only push.

Open a pull request only when the user asks. Launching the chief of staff is that request for the release pull request only. Chapters get no pull request. They integrate into the loop branch locally.

### Do not

- Do not force-push.
- Do not skip hooks.
- Do not amend a pushed commit.
- Do not run `gh repo sync --force`.
- Do not retry a failed `gh` or git authentication with another token.

## Conventional commits

Use [Conventional Commits](https://www.conventionalcommits.org/) for every commit. Format:

```
<type>[optional scope]: <short imperative summary>

[optional body]

[optional footer]
```

### Types

| Type | When to use |
|------|-------------|
| `feat` | New user-facing capability |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or correcting tests |
| `chore` | Tooling, deps, CI config — no production code change |
| `perf` | Performance improvement |
| `ci` | CI/CD pipeline changes |

### Rules

- **Subject**: imperative mood, lowercase, no trailing period, ~72 chars max
  - ✅ `fix(parser): handle empty syslog lines`
  - ❌ `Fixed the parser bug.`
- **Scope** (optional): module or area affected, e.g. `cli`, `ingestion`, `ci`
- **Breaking changes**: add `!` after type/scope or a `BREAKING CHANGE:` footer
- **Issue refs**: include the GitHub issue in body or footer, e.g. `Closes #42` or `Refs #42`

### Examples

```
feat(cli): add --format json output flag

fix(ingestion): reject malformed timestamps before parse

docs: document local CI workflow in CONTRIBUTING

chore(deps): bump ruff to 0.9.0

refactor(parsers)!: rename SyslogAdapter to SyslogParser

BREAKING CHANGE: syslog adapter module moved to parsers.syslog_adapters
```
