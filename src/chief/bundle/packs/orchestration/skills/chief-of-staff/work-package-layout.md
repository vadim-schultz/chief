# Work package layout

One folder per body of work.

## Suite-level files

| Path | Role |
| --- | --- |
| `00-architecture.md` | Stack, scope, structure, invariants the chapters must respect |
| `01-rollout.md` | Chapter list, dependency graph, git/CI invariants, **execution order** for chief of staff |
| `gaps-and-decisions.md` | Settled decisions and deferred items — do not re-litigate during implementation |
| `run-ledger.md` | Merge ledger (chapters → loop branch; release pull request to main) |
| `chapters/` | One executable markdown plan per chapter |

`run-ledger.md` may be absent until the first chapter merges; architecture, rollout, gaps, and `chapters/` are expected for executable suites.

## Chapter files

Each file under `chapters/` is a self-contained slice (often `NN-<slug>.md`). YAML frontmatter typically includes `name`, `overview`, optional `todos`, and `isProject`. Chapters link tests, refactor gate, branch name, and commits.

`chapters/README.md` is optional index copy.

## What chief of staff reads

| When | Files |
| --- | --- |
| Preflight + invariants | `01-rollout.md`, `00-architecture.md`, `gaps-and-decisions.md`, `run-ledger.md` (if exists) |
| Per chapter | One `chapters/*.md` path from rollout execution order |
| Order source | `01-rollout.md` → **Execution order (chief of staff)**, else **Chapters** table |

Orchestration is **user-level**: the chief-of-staff skill and the chapter-implementer agent are installed once per user, not per plan folder. A plan folder supplies architecture, rollout, gaps, chapters, and run-ledger only.
