---
name: Stack knowledge and VS Code target - rollout
overview: "Git invariants, scheduling matrix, parallel batches, integration order, critical path and the per-chapter gate for the stack knowledge work package."
isProject: false
---

# Stack knowledge and VS Code target - rollout

Chapters run in five batches. Batch 1 holds two chapters with disjoint paths. Batch 2 holds four chapters, one for each stack pack. Batches 3 to 5 each hold one chapter, because they wait on earlier output.

**Architecture:** [00-architecture.md](00-architecture.md) · **Decisions:** [gaps-and-decisions.md](gaps-and-decisions.md) · **Chapters:** [chapters/README.md](chapters/README.md) · **Ledger:** [run-ledger.md](run-ledger.md)

This file holds the scheduling contract. The matrix is the source of truth for `depends_on` and `touches`. Each chapter frontmatter must match its matrix row. If the two disagree, this file wins.

---

## Git invariants

- **Release branch:** `main`. The release chapter opens the only pull request.
- **Loop branch:** `feat/stack-knowledge`. The chief of staff creates it from `main` before the first chapter.
- **Chapter branch:** `feat/stack-knowledge-<chapter id>-<slug>`, for example `feat/stack-knowledge-c1-vscode-target`. It starts from the loop branch.
- Chapter branches and the loop branch stay local until the release chapter runs.
- Chapters do not push. No chapter opens a pull request.
- The chief of staff merges each chapter branch into the loop branch with `git merge --no-ff`.

## Scheduling matrix

| ID | Chapter | Depends on | Batch | Touches |
| --- | --- | --- | ---: | --- |
| C0 | [name-scrub](chapters/00-name-scrub.md) | none | 1 | `src/chief/bundle/packs/orchestration/skills/chief-of-staff/SKILL.md`; `tests/test_sibling_name.py` |
| C1 | [vscode-target](chapters/01-vscode-target.md) | none | 1 | `src/chief/targets/names.py`; `src/chief/targets/registry.py`; `src/chief/targets/locations.py`; `src/chief/catalogue/bundle_tree.py`; `src/chief/installation/planner.py`; `src/chief/installation/installer.py`; `src/chief/cli/commands.py`; `tests/test_render.py`; `tests/test_locations.py`; `tests/test_api.py`; `tests/test_cli.py`; `tests/test_export.py`; `tests/test_install.py`; `tests/fixtures/install_snapshot.json` |
| C2a | [stack-docs-pack](chapters/02-stack-docs.md) | none | 1 | `src/chief/bundle/packs/stack-docs/**`; `tests/test_stack_knowledge.py`; `tests/test_packs.py`; `tests/fixtures/install_snapshot.json` |
| C2b | [stack-cloud-pack](chapters/03-stack-cloud.md) | C2a | 2 | `src/chief/bundle/packs/stack-cloud/**`; `tests/test_stack_cloud_pack.py`; `tests/fixtures/install_snapshot.json` |
| C2c | [stack-data-services-pack](chapters/04-stack-data-services.md) | C2a | 2 | `src/chief/bundle/packs/stack-data-services/**`; `tests/test_stack_data_services_pack.py`; `tests/fixtures/install_snapshot.json` |
| C2d | [stack-python-pack](chapters/05-stack-python.md) | C2a | 2 | `src/chief/bundle/packs/stack-python/**`; `tests/test_stack_python_pack.py`; `tests/fixtures/install_snapshot.json` |
| C2e | [stack-web-pack](chapters/06-stack-web.md) | C2a | 2 | `src/chief/bundle/packs/stack-web/**`; `tests/test_stack_web_pack.py`; `tests/fixtures/install_snapshot.json` |
| C3 | [bundle-complete-gate](chapters/07-bundle-complete-gate.md) | C2b, C2c, C2d, C2e | 3 | `tests/stack_contract.py`; `tests/test_stack_knowledge.py`; `tests/test_stack_cloud_pack.py`; `tests/test_stack_data_services_pack.py`; `tests/test_stack_python_pack.py`; `tests/test_stack_web_pack.py`; `tests/test_packs.py`; `tests/fixtures/install_snapshot.json` |
| C4 | [docs-and-changelog](chapters/08-docs-and-changelog.md) | C1, C3 | 4 | `README.md`; `CHANGELOG.md`; `docs/**`; `tests/test_readme.py` |
| C5 | [release](chapters/09-release.md) | C1, C3, C4 | 5 | none. The chief of staff runs it. |

## Parallel batches

- **Batch 1: C0, C1, C2a.** C0 touches one line of the chief-of-staff skill and one new test file. C1 and C2a both touch the install snapshot. C1 integrated first, and C2a regenerates the snapshot after it merges the loop branch (D13). The target code and the pack folder do not overlap.
- **Batch 2: C2b, C2c, C2d, C2e.** Each chapter owns one new pack folder, and all four touch the install snapshot. They implement in parallel and integrate one at a time, in the listed order (D13).
- **Batch 3: C3.** C3 owns the install snapshot update for the stack packs and the final pack assertions. Batch 2 must be integrated first.
- **Batch 4: C4.** C4 documents the targets from C1 and the packs from C3.
- **Batch 5: C5.** Chief of staff only.

Every chapter that adds installed paths regenerates `tests/fixtures/install_snapshot.json` after it merges the loop branch (D13). Those chapters integrate one at a time, so the file has one merge at a time. C3 regenerates it only when the final install set differs.

## Integration order

1. C0 - name-scrub
2. C1 - vscode-target
3. C2a - stack-docs-pack
4. C2b - stack-cloud-pack
5. C2c - stack-data-services-pack
6. C2d - stack-python-pack
7. C2e - stack-web-pack
8. C3 - bundle-complete-gate
9. C4 - docs-and-changelog
10. C5 - release

Batch 2 chapters integrate in the listed order, one at a time (D13).

## Critical path

C2a -> C2b -> C3 -> C4 -> C5

C1 runs in parallel with C2a. C1 must integrate before C4, because C4 documents the target list.

## Per-chapter gate

A chapter passes the gate when all of the following are true:

1. The red tests are committed and fail for the right reason: missing behaviour, not a typo or an import error.
2. The chapter's narrow verification commands pass on the chapter branch.
3. `./ci.sh all` exits 0 on the chapter branch, after the loop branch is merged into it.
4. The refactor report in the chapter file is filled in. It names the containing method or class that the pass audited.
5. The chief of staff merges the chapter branch into the loop branch with `--no-ff`, runs `./ci.sh all` on the loop branch, and records the command and the commit in the run ledger.

Chapters do not push and get no remote CI. The release chapter, C5, runs remote CI once, on the pull request into `main`.

## Final gate

Before the release pull request opens, the loop branch must show:

- Every chapter row in the run ledger reads `done`.
- `./ci.sh all` exits 0 on the loop branch head.
- The leak gate passes in strict mode on the loop branch head: `CHIEF_LEAK_STRICT=1 ./ci.sh all`. The gate reads its denylist from the file that `CHIEF_LEAK_DENYLIST` names.
- The live checks in C5 pass. They are a dry run and a real install into a temporary `HOME` for every target, followed by `chief doctor` and `chief export`.
- The user has confirmed the release.

The release tag is `v0.2.0` (D10). The release chapter creates it on the merged commit.

The release chapter, C5, runs this gate once. The chief of staff executes it. No implementer runs it.
