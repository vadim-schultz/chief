---
name: Chapter C7 - Local-first CI policy
overview: "Run local gates for every chapter. Run remote GitHub CI once, on the pull request into main. Make the workflows, the templates and the texts follow that rule."
id: C7
depends_on: ["C4", "C6"]
touches: [".github/**", ".githooks/**", ".gitlab-ci.yml", "ci.sh", "tests/test_ci_scope.py", "src/chief/bundle/packs/orchestration/skills/chief-of-staff/git-model.md", "src/chief/bundle/packs/orchestration/skills/chief-of-staff/host-workflow.md", "src/chief/bundle/packs/orchestration/skills/chief-of-staff/SKILL.md", "src/chief/bundle/packs/orchestration/agents/chapter-implementer.md", "src/chief/bundle/packs/work-package/skills/work-package-create/SKILL.md", "src/chief/bundle/packs/work-package/skills/work-package-create/templates/**", "tests/test_work_package_templates.py", "tests/test_dispatch_contract.py", "tests/fixtures/install_snapshot.json"]
execution: chapter-implementer
isProject: false
---

# C7 - Local-first CI policy

**Depends on:** C4, C6 · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [../01-rollout.md](../01-rollout.md)

## Goal

After this chapter, the repository runs one remote workflow. It runs on the pull request into `main` and on tags. Each distributed text states that chapters pass their local gate and that remote CI waits for the release pull request.

This chapter changes the distributed texts. It does not change how this work package integrates its own chapters. Rule R3 applies to this work package.

## Read first

- [00-architecture.md](../00-architecture.md): read invariants I4 and I5.
- [../gaps-and-decisions.md](../gaps-and-decisions.md): read D8 and D12, and open item O4.
- [../01-rollout.md](../01-rollout.md): read "Per-chapter gate" and "Final gate".
- `ci.sh`: read the stage names. The workflow calls these stages and adds no new tool install.
- `tests/test_ci_scope.py`: read how the existing test parses the pipeline. The new test follows the same approach.

## Coordination scope

**Add:**

- `.github/workflows/ci.yml`.
- `.github/workflows/release.yml`.
- `.githooks/pre-push`. It runs the leak gate only.
- `src/chief/bundle/packs/work-package/skills/work-package-create/templates/release-chapter.md`.

**Edit:**

- `ci.sh`: only if a workflow needs a stage name that does not yet exist.
- `tests/test_ci_scope.py`: rewrite it for the new workflow.
- `git-model.md`, `host-workflow.md`, `SKILL.md` and `chapter-implementer.md` of the orchestration pack: the local-first wording and the return fields.
- `work-package-create/SKILL.md`: list the release chapter template.
- Templates `rollout.md` and `run-ledger.md`, and `required-sections.json`: the per-chapter gate, the final gate, the `Local gate` and `Remote CI` columns, and the release chapter entry.
- `tests/test_work_package_templates.py`, `tests/test_dispatch_contract.py`, `tests/fixtures/install_snapshot.json`.

**Delete:**

- `.gitlab-ci.yml`.

**Do not edit:**

- `tests/ci/**`.
- The stage behavior of `ci.sh`.

## Work items

1. **Red.**
   - Add the workflow tests to `tests/test_ci_scope.py`:
     - `test_workflow_triggers_only_on_main_and_tags`: the `pull_request` trigger names `branches: [main]`. The `push` trigger names only tags. `workflow_dispatch` is allowed.
     - `test_workflow_has_no_branch_wildcard_trigger`: no branch list with a wildcard and no push trigger on all branches.
     - `test_workflow_token_is_read_only`: the top-level `permissions` is `contents: read`. `ci.yml` has no `contents: write`.
     - `test_ci_pins_actions_to_sha`: each `uses:` line carries a 40-character commit SHA.
     - `test_remote_jobs_are_subset_of_local_gate`: each job runs a `./ci.sh` mode whose stages `./ci.sh all` covers.
   - Add the template tests to `tests/test_work_package_templates.py`:
     - `test_release_chapter_template_has_required_sections`: the template holds the ten chapter sections in order.
     - `test_release_chapter_template_forbids_chapter_branch`: the template names no chapter branch.
   - Commit the red tests with the type `test`.

2. **Workflow.**
   - **Green:** Write `.github/workflows/ci.yml`.
     - Triggers: as in the red tests.
     - Top-level `permissions: contents: read`.
     - A `concurrency` group with cancel-in-progress for pull requests.
     - Job `gate` runs `./ci.sh all`.
     - Job `unit` runs `./ci.sh unit` with `CI_HARNESS_NESTED=1` on Python 3.10 and 3.14. Apply open item O4. The default excludes `tests/ci` from this matrix.
     - Pin each action to a full commit SHA. Put the version in a comment.
     - No secrets. No `pull_request_target`.
   - Write `.github/workflows/release.yml`. On a tag that matches `v*`, it builds the source distribution and the wheel. It attaches them to a GitHub release. Only this workflow gets `contents: write`.
   - Add `.githooks/pre-push`. It runs the leak gate and nothing else.
   - Delete `.gitlab-ci.yml`.
   - **Refactor:** The workflow jobs call the same stages as `ci.sh`. Remove any tool install that repeats a stage.

3. **Texts and templates.**
   - **Red:** Add `test_chapter_return_names_local_gate` to `tests/test_dispatch_contract.py`. It checks that the return fields hold `local gate: <command> @ <sha>` and `remote ci: not run (policy)`. Add `test_no_text_waits_for_remote_ci_per_chapter`. It finds `checks --watch` only in the release section. Both fail now.
   - **Green:**
     - State in `git-model.md` that chapter integration is local, and that remote CI waits for the release pull request.
     - Keep one definition of the local gate in `git-model.md`. The other texts link to it.
     - Update the return fields in the agent text.
     - In `rollout.md`, name the release chapter in the per-chapter gate and in the final gate.
     - In `run-ledger.md`, add the `Local gate` and `Remote CI` columns.
     - Write `release-chapter.md`. Its front matter sets `execution: chief-of-staff`. It holds these steps: run the local gate on the loop branch head, open the pull request into `main` with `gh pr create --base main`, watch the checks with `gh pr checks --watch`, merge, and tag.
     - In `release-chapter.md`, add this remote-failure rule: reproduce the failure locally, fix it on the loop branch, rerun the local gate, then push. Ask the user before a third remote run.
     - Add the `release-chapter.md` entry to `required-sections.json`.
   - **Refactor:** Remove any remaining statement that a chapter waits for remote CI.

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| Workflow triggers | `test_workflow_triggers_only_on_main_and_tags` | `test_workflow_has_no_branch_wildcard_trigger` |
| Workflow safety | `test_workflow_token_is_read_only` | `test_ci_pins_actions_to_sha` |
| Local gate subset | `test_remote_jobs_are_subset_of_local_gate` | `test_release_chapter_template_forbids_chapter_branch` |
| Texts | `test_chapter_return_names_local_gate` | `test_no_text_waits_for_remote_ci_per_chapter` |

## Review gate

- Run `actionlint` on the two workflows if it is installed. Record the result.
- Check that the release template holds every section of the chapter template.
- Check that `.githooks/pre-push` runs only the leak gate.

## Out of scope

- Repository settings and the ruleset. C10 owns them.
- Changes to `tests/ci/**`.

## Verification

```bash
# Run from the repository root.
./ci.sh all
tox -e test-pytest -- tests/test_ci_scope.py tests/test_work_package_templates.py tests/test_dispatch_contract.py
git ls-files .gitlab-ci.yml
```

Expected: `./ci.sh all` exits 0. The pytest run passes. The last command prints nothing after the chapter commit.

## Refactor report

_To be filled by the implementer before the chapter commit._

## Git workflow

- Check out the loop branch: `git checkout feat/private-distribution`.
- Create the chapter branch: `git checkout -b feat/private-distribution-c07-ci-policy`.
- Commit the red tests first, with the type `test`.
- Commit the workflow with the type `ci`. Commit the texts with the type `docs`.
- Run `./ci.sh all` before the hand-off.
- Do not push. The chief merges the chapter branch into the loop branch with `git merge --no-ff`.
