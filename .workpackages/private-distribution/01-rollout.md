---
name: Private distribution - rollout
overview: "Git invariants, dependency graph, scheduling matrix, batches, integration order and gates for the private-distribution work package."
isProject: false
---

# Private distribution - rollout

The chapters run in nine batches. Batch 3 holds three chapters with disjoint paths. Every other batch holds one chapter, because those chapters share files.

**Architecture:** [00-architecture.md](00-architecture.md) · **Decisions:** [gaps-and-decisions.md](gaps-and-decisions.md) · **Chapters:** [chapters/README.md](chapters/README.md) · **Ledger:** [run-ledger.md](run-ledger.md)

This file holds the scheduling contract. The matrix is the source of truth for `depends_on` and `touches`. Each chapter frontmatter must match its matrix row. If the two disagree, this file wins.

---

## Before C0

These steps happen before the chief of staff starts the first chapter.

1. The repository is private. Check with `gh repo view --json visibility` (D1).
2. This work package folder is on `main`, through a pull request. The folder holds no corporate content, so the pull request runs no remote CI.
3. The environment variable `CORPORATE_REPO` names the source repository. Do not write its path into any file.

## Git invariants

- **Release branch:** `main`. It holds this work package and nothing else until C10.
- **Loop branch:** `feat/private-distribution`. The chief creates it from `main`.
- **Chapter branch:** `feat/private-distribution-cNN-<slug>`. It starts from the loop branch.

- **R1.** A chapter starts only after every chapter in its `depends_on` merges into the loop branch.
- **R2.** Two chapters in one batch never share a `touches` path.
- **R3.** The chief merges chapters in the integration order, with `git merge --no-ff`, locally.
- **R4.** After each merge, the chief runs `./ci.sh all` and the leak gate on the loop branch. The ledger records the command and the commit.
- **R5.** Nothing is pushed before C10. Check with `git ls-remote origin` before each chapter.
- **R6.** Nothing commits to `main` directly. Commits follow Conventional Commits.
- **R7.** A blocked chapter blocks only its dependants. Unrelated chapters continue.

## Dependency graph

```text
C0 -> C1 -> C2
C2 -> C3
C2 -> C4
C2 -> C5
C3 -> C6
C4 -> C7
C6 -> C7
C3 -> C8
C4 -> C8
C6 -> C8
C7 -> C8
C8 -> C9 -> C10
```

## Scheduling matrix

| ID | Chapter | Depends on | Batch | Execution | Touches |
| --- | --- | --- | ---: | --- | --- |
| C0 | [seed](chapters/00-seed.md) | none | 0 | chief-of-staff | `**` |
| C1 | [rename](chapters/01-rename.md) | C0 | 1 | chapter-implementer | `src/**`; `tests/**`; `pyproject.toml`; `README.md`; `docs/**` |
| C2 | [guards](chapters/02-guards.md) | C1 | 2 | chapter-implementer | `ci.sh`; `tests/test_no_leaks.py`; `tests/test_bundle_contract.py`; `tests/test_install.py`; `tests/fixtures/install_snapshot.json`; `src/chief/bundle/sources.json` |
| C3 | [corporate-code](chapters/03-corporate-code.md) | C2 | 3 | chapter-implementer | `src/chief/mcp/**`; `src/chief/api.py`; `src/chief/cli/**`; `src/chief/bundle/packs/mcp/**`; `src/chief/bundle/packs/orchestration/skills/chief-of-staff/corporate-build-env.md`; `src/chief/bundle/packs/orchestration/skills/chief-of-staff/SKILL.md`; `src/chief/bundle/packs/orchestration/agents/chapter-implementer.md`; `tests/test_mcp_snippet.py`; `tests/test_cli.py`; `tests/test_api.py`; `tests/test_packs.py`; `tests/fixtures/install_snapshot.json` |
| C4 | [packaging](chapters/04-packaging.md) | C2 | 3 | chapter-implementer | `pyproject.toml`; `tox.ini`; `LICENSE`; `docs/conf.py`; `.gitignore` |
| C5 | [bundle-scrub](chapters/05-bundle-scrub.md) | C2 | 3 | chapter-implementer | `src/chief/bundle/packs/quality/**`; `src/chief/bundle/packs/style/**`; `src/chief/bundle/packs/data/**` |
| C6 | [github-host](chapters/06-github-host.md) | C3 | 4 | chapter-implementer | `src/chief/bundle/packs/orchestration/skills/chief-of-staff/host-workflow.md`; `src/chief/bundle/packs/orchestration/skills/chief-of-staff/git-model.md`; `src/chief/bundle/packs/orchestration/skills/chief-of-staff/SKILL.md`; `src/chief/bundle/packs/orchestration/skills/chief-of-staff/work-package-layout.md`; `src/chief/bundle/packs/orchestration/agents/chapter-implementer.md`; `src/chief/bundle/packs/git/**`; `src/chief/bundle/packs/work-package/skills/work-package-create/templates/chapter.md`; `src/chief/bundle/packs/work-package/skills/work-package-create/templates/rollout.md`; `src/chief/bundle/packs/work-package/skills/work-package-create/templates/run-ledger.md`; `tests/fixtures/hello-levels/gaps-and-decisions.md`; `tests/test_bundle_contract.py`; `tests/test_dispatch_contract.py` |
| C7 | [ci-policy](chapters/07-ci-policy.md) | C4, C6 | 5 | chapter-implementer | `.github/**`; `.githooks/**`; `.gitlab-ci.yml`; `ci.sh`; `tests/test_ci_scope.py`; `src/chief/bundle/packs/orchestration/skills/chief-of-staff/git-model.md`; `src/chief/bundle/packs/orchestration/skills/chief-of-staff/host-workflow.md`; `src/chief/bundle/packs/orchestration/skills/chief-of-staff/SKILL.md`; `src/chief/bundle/packs/orchestration/agents/chapter-implementer.md`; `src/chief/bundle/packs/work-package/skills/work-package-create/SKILL.md`; `src/chief/bundle/packs/work-package/skills/work-package-create/templates/**`; `tests/test_work_package_templates.py`; `tests/test_dispatch_contract.py`; `tests/fixtures/install_snapshot.json` |
| C8 | [docs](chapters/08-docs.md) | C3, C4, C6, C7 | 6 | chapter-implementer | `README.md`; `docs/*.md`; `CHANGELOG.md`; `tests/test_readme.py` |
| C9 | [final-sweep](chapters/09-final-sweep.md) | C8 | 7 | chapter-implementer | `tests/test_ci_skill_doc.py`; `tests/test_packs.py`; `tests/test_install.py`; `tests/test_no_leaks.py` |
| C10 | [release-pr](chapters/10-release-pr.md) | C9 | 8 | chief-of-staff | none |

The `touches` sets of each batch are disjoint:

- Batch 0 holds C0 alone.
- Batch 3 holds C3, C4 and C5. C3 owns the orchestration and MCP paths and the install snapshot. C4 owns the packaging files. C5 owns the reference packs. None of the three touches a path in another.
- Batches 1, 2 and 4 to 8 hold one chapter each.

## Parallel batches

- Batch 0: C0.
- Batch 1: C1.
- Batch 2: C2.
- Batch 3: C3, C4 and C5. Their paths are disjoint.
- Batch 4: C6.
- Batch 5: C7.
- Batch 6: C8.
- Batch 7: C9.
- Batch 8: C10.

## Integration order

1. C0 - seed
2. C1 - rename
3. C2 - guards
4. C3 - corporate-code
5. C4 - packaging
6. C5 - bundle-scrub
7. C6 - github-host
8. C7 - ci-policy
9. C8 - docs
10. C9 - final-sweep
11. C10 - release-pr, the final gate

Each chapter in this order has every `depends_on` chapter earlier in the list.

## Critical path

C0 -> C1 -> C2 -> C3 -> C6 -> C7 -> C8 -> C9 -> C10. A delay on this path delays the release. A delay elsewhere delays only the work that waits for it. C4 and C5 run in the shadow of the path.

## Per-chapter gate

A chapter passes the gate when all of the following are true:

1. The red tests are committed, and they failed for the right reason before the green change. An import error or an attribute error does not count as the right reason.
2. The chapter's verification commands pass on the chapter branch.
3. `./ci.sh all` passes on the chapter branch, after the loop branch is merged into it.
4. The leak gate reports no file that is worse than the local baseline.
5. The refactor report is filled in. It states what changed, or it states "no refactor needed" with a reason.
6. The chief merges the chapter branch into the loop branch locally. The chief then runs `./ci.sh all` on the loop branch and records the command and the commit in the ledger.
7. The ledger row for the chapter shows `done`, with the local commit.

A chapter that fails any item stays `blocked` in the ledger. R7 applies.

## Final gate

Chapter C10 is the final gate. The chief of staff runs it. No implementer runs it.

Before C10 starts, the loop branch must show:

- Every chapter row in the ledger shows `done`.
- `./ci.sh all` passes on the loop branch.
- The strict leak gate reports zero hits.
- `git log main..HEAD` shows no corporate author or committer address.
- Open item O1 is answered in writing.

C10 then opens one pull request into `main`. Remote CI runs on that pull request, and on no other pull request in this run.
