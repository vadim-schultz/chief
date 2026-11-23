---
name: Private distribution - architecture
overview: "Target layout, invariants and decisions for the private-distribution work package. It turns the corporate chief-of-staff distribution into a GitHub-only distribution with no corporate content."
isProject: false
---

# Private distribution - architecture

This work package turns the corporate chief-of-staff distribution into the private, GitHub-only distribution `chief`.

**Rollout:** [01-rollout.md](01-rollout.md) · **Decisions:** [gaps-and-decisions.md](gaps-and-decisions.md) · **Chapters:** [chapters/README.md](chapters/README.md) · **Ledger:** [run-ledger.md](run-ledger.md)

**Status:** planned. This folder holds documentation only. The chief of staff runs the chapters in a later session.

---

## Purpose

The corporate distribution installs the chief-of-staff skill, the chapter-implementer agent and the work package packs. It depends on corporate GitLab, corporate package mirrors and corporate MCP setup guides. None of those parts can ship to GitHub.

This work package builds a distribution with no corporate content. It keeps the generic packs. It adds GitHub handling for pull requests and checks. It runs remote CI once per release, not once per chapter.

Out of scope:

- Rewriting skill prose beyond the scrub in C5 and the host text in C6.
- Installing the corporate and private distributions side by side.
- Publishing to PyPI.
- Changing the corporate repository. This work package only reads it.

## Invariants

| ID | Invariant | Gate |
| --- | --- | --- |
| I1 | The tree names no corporate host, login, product or address. | Leak gate in ratchet mode from C2. Strict mode from C9. |
| I2 | Before C10, only `main` reaches GitHub. | Rule R5 in [01-rollout.md](01-rollout.md). The chief checks `git ls-remote origin` before each chapter. |
| I3 | The installer never writes MCP configuration files. | Planner refusal test, kept green in C3. |
| I4 | Remote CI runs only on pull requests into `main` and on tags. | Workflow trigger test in C7. |
| I5 | Every chapter ends with `./ci.sh all` green on its chapter branch and on the loop branch. | Per-chapter gate in [01-rollout.md](01-rollout.md). |
| I6 | Every new unit has one happy-path test and one negative-path test. | Review gate of each chapter. |
| I7 | The local leak denylist stays outside the repository. | Test in C2. |
| I8 | Bundled skill and rule text keeps its meaning. Only the scrub in C5 and the host text in C6 change it. | Review gates of C5 and C6. |

## Target layout

```text
chief/
  .github/workflows/     ci.yml (gate on the pull request into main),
                         release.yml (tags only)
  .githooks/pre-push     leak gate before every push
  ci.sh                  stages: format, lint, types, unit, build
  tox.ini                tox environments with hermetic tool settings
  pyproject.toml         package metadata, MIT license, GitHub URLs
  src/chief/             Python package, renamed from the source package
    bundle/packs/        orchestration, git, quality, style, data, work-package
  tests/                 unit tests, leak gate, install snapshot
  docs/                  thin includes of the README sections
  .workpackages/private-distribution/    this work package
```

## Decided

| ID | Choice | Reason |
| --- | --- | --- |
| A1 | GitHub handling only. | The distribution targets GitHub. GitLab handling has no use there. |
| A2 | Local gates for each chapter. One remote run, on the pull request into `main`. | Keeps hosted CI minutes low on a private repository. The workflow trigger enforces the rule. |
| A3 | Chapter branches and the loop branch stay local until C10. | One squashed commit reaches GitHub. No intermediate corporate history leaks. |
| A4 | The package, the import name and the command are all `chief`. | The name is short and matches the repository. PyPI is not used. |
| A5 | Fresh history. | No corporate author, address or merge-request link reaches the new repository. |

Full decisions and reasons: [gaps-and-decisions.md](gaps-and-decisions.md), D1 to D14.

## Separation hazards

1. The corporate `LICENSE` file claims employer copyright. Confirm the rights before the release push (O1).
2. The global Git identity and the global uv, pip and npm settings point at corporate services. A repository-local identity and a hermetic `ci.sh` override them (D5, D11).
3. Corporate tokens live only in a local file outside the repository (D10).
4. The reference front matter names a corporate login in 13 files. C5 replaces it.
5. The name `chief` belongs to another project on PyPI. Never publish the package (D4).
6. The installer refuses to overwrite files it does not track. On the other machine, move the old hand-installed skill aside before `chief install`.
7. After release, two forks exist. Decide the upstream later (O7).

## Open

The Open table in [gaps-and-decisions.md](gaps-and-decisions.md) holds O1 to O8. Each open item has a default that applies when nobody answers.
