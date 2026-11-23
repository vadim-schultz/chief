---
name: Chapter C6 - GitHub host handling
overview: "Make the bundle handle GitHub only. Implementers and the chief use gh for pull requests, checks and merge state. No GitLab handling remains."
id: C6
depends_on: ["C3"]
touches: ["src/chief/bundle/packs/orchestration/skills/chief-of-staff/host-workflow.md", "src/chief/bundle/packs/orchestration/skills/chief-of-staff/git-model.md", "src/chief/bundle/packs/orchestration/skills/chief-of-staff/SKILL.md", "src/chief/bundle/packs/orchestration/skills/chief-of-staff/work-package-layout.md", "src/chief/bundle/packs/orchestration/agents/chapter-implementer.md", "src/chief/bundle/packs/git/**", "src/chief/bundle/packs/work-package/skills/work-package-create/templates/chapter.md", "src/chief/bundle/packs/work-package/skills/work-package-create/templates/rollout.md", "src/chief/bundle/packs/work-package/skills/work-package-create/templates/run-ledger.md", "tests/fixtures/hello-levels/gaps-and-decisions.md", "tests/test_bundle_contract.py", "tests/test_dispatch_contract.py"]
execution: chapter-implementer
isProject: false
---

# C6 - GitHub host handling

**Depends on:** C3 · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [../01-rollout.md](../01-rollout.md)

## Goal

After this chapter, the bundle handles GitHub only. Implementers and the chief use `gh` for pull requests, checks and merge state. No GitLab handling remains in the bundle.

## Read first

- [00-architecture.md](../00-architecture.md): read decision A1.
- [../gaps-and-decisions.md](../gaps-and-decisions.md): read D6, D8 and D12.
- [../01-rollout.md](../01-rollout.md): read "Per-chapter gate".
- The hand-installed skill on the workstation, at `~/.claude/skills/chief-of-staff/references/`. Read `host-workflow.md` and `git-model.md`. Port only the GitHub handling that the bundle lacks.
- The hand-installed agent at `~/.claude/agents/chapter-implementer.md`. Read its GitHub block.
- The rules `github-remotes.mdc` and `git-workflow.mdc` in `~/.cursor/rules/`. Port the GitHub remotes section.

Use `{{skill_dir:chief-of-staff}}` tokens for links between bundle files. Do not write absolute paths.

## Coordination scope

**Add:**

- None.

**Edit:**

- `host-workflow.md`: rewrite it for GitHub only. Work item 2 lists the content.
- `git-model.md`: remove the GitLab sections and the push options. Replace "merge request" with "pull request". Link to `host-workflow.md` for the commands.
- `SKILL.md` of the orchestration pack: the description and the host sentence. Replace "release MR" with "release pull request". Remove the internal product name from the description, as listed in the denylist. Pass the loop and release branch names to each implementer.
- `agents/chapter-implementer.md`: the description, the GitHub pull request block and the return fields.
- `work-package-layout.md`: replace "release MR" with "release pull request".
- `git/rules/git-workflow.md`: the scope line, the pull request wording and the issue reference. Add the GitHub remotes section.
- `git/pack.toml`: the description.
- Templates `chapter.md`, `rollout.md` and `run-ledger.md`: replace "merge request" with "pull request".
- `tests/fixtures/hello-levels/gaps-and-decisions.md`: the sentence about the toy repository.
- `tests/test_bundle_contract.py`: change the GitHub text rule into a GitLab text rule.
- `tests/test_dispatch_contract.py`: change the exact scope line that the test asserts.

**Do not edit:**

- The CI policy text and the release template. C7 owns them.
- The README. C8 owns it.

## Work items

1. **Red.**
   - Add `test_host_workflow_names_each_gh_command`. It checks that `host-workflow.md` names `gh pr create`, `gh pr checks`, `gh pr merge`, `gh pr view` and `gh api`.
   - Add `test_host_workflow_never_requests_projectcards`. It checks that no `--json` line names `projectCards`.
   - Add `test_bundle_has_no_gitlab_text`. It scans the bundle for `gitlab`, `glab` and `merge request` and expects no hit.
   - Flip the existing rule test into `test_planted_gitlab_text_is_found`. It plants one term in a temporary copy and expects a finding.
   - Commit the red tests with the type `test`.

2. **Host workflow.**
   - **Green:** Write `host-workflow.md` with these sections:
     - Host detection with `git remote get-url origin`. A URL that contains `github.com` selects GitHub.
     - Use `gh` for pull request and check state. Do not use `git fetch` or `git ls-remote` for that state.
     - `gh auth setup-git` as the credential helper.
     - The preflight: `gh auth status` and `gh repo view --json nameWithOwner,url`.
     - The safe `--json` fields: `state`, `mergedAt`, `mergeable`, `mergeStateStatus`, `url`, `headRefName`, `baseRefName`, `statusCheckRollup`, `title` and `number`.
     - The classic Projects field never appears in `--json`. Use `gh project` for board items. It needs `gh auth refresh -s project`.
     - The REST merge check: `gh api repos/{owner}/{repo}/pulls/{number}`.
     - The chapter pull request commands and the release pull request commands.
     - The implementer return fields.
   - **Refactor:** Keep each `gh` command block in `host-workflow.md` only. `git-model.md` links to it.

3. **Git model, agent and rules.**
   - **Green:** Rewrite the branch roles, the bootstrap and the per-chapter flow in `git-model.md`. Update the agent text. Update the git rule with the GitHub remotes section. Its "do not" list covers these items:
     - No force-push.
     - No skipped hooks.
     - No amend of a pushed commit.
     - No `gh repo sync --force`.
     - No retry with another token.
   - Add the precedence note. Launching the chief is the request to open the chapter pull requests and the release pull request.
   - **Refactor:** Keep one copy of the branch-role table. Remove duplicates from `SKILL.md`.

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| Host commands | `test_host_workflow_names_each_gh_command` | `test_host_workflow_never_requests_projectcards` |
| Bundle host text | `test_planted_gitlab_text_is_found` | `test_bundle_has_no_gitlab_text` |
| Git rule scope | `test_dispatch_contract_names_github_scope` | `test_git_rule_has_no_gitlab_scope` |

## Review gate

- Run `git grep -n -i -E "gitlab|glab|merge request" -- src/chief/bundle`. Expected: no output.
- Check that each `gh` command named in `host-workflow.md` exists. Run `gh pr create --help`, `gh pr checks --help` and `gh pr merge --help`.
- Check that `SKILL.md`, `git-model.md` and the agent name the same branch roles.

## Out of scope

- The CI policy and the release template. C7 owns them.
- The README and the changelog. C8 owns them.

## Verification

```bash
# Run from the repository root.
./ci.sh unit
git grep -n -i -E "gitlab|glab|merge request" -- src/chief/bundle || echo "no gitlab text in bundle"
gh pr create --help | head -3
```

Expected: `./ci.sh unit` exits 0. The grep prints `no gitlab text in bundle`. The help text prints the usage of `gh pr create`.

## Refactor report

Refactor gate: three smells applied. Duplicated code: the release block in `host-workflow.md` repeated the chapter `gh` block, so the release section now reuses the chapter block with its parameters. Duplicated code: the GitHub scope literal appeared twice in `tests/test_dispatch_contract.py`, so it is one constant. Mysterious name: an inline negative literal was spelled in pieces, so it is now a named constant with a comment. `_scan` in `tests/test_bundle_contract.py` needed no change. Observed, not touched: the forge term list also sits in `tests/test_no_leaks.py`, which is outside this chapter's scope.

Data-design gate: not applicable. The change is text and host handling only.

Deviations: three test names are reworded so they do not carry the forge term, because the leak baseline is frozen at zero for those files. `_scan` now fails on an unknown rule name. The agent file has no `gh` block, and links to `host-workflow.md` instead. The per-chapter pull-request wording conflicts with D3 and D8 in several files. C7 corrects it, and C6 reports the list.

## Git workflow

- Check out the loop branch: `git checkout feat/private-distribution`.
- Create the chapter branch: `git checkout -b feat/private-distribution-c06-github-host`.
- Commit the red tests first, with the type `test`.
- Commit the host handling with the type `feat`. Use the subject `feat(bundle): handle pull requests on GitHub only`.
- Run `./ci.sh all` before the hand-off.
- Do not push. The chief merges the chapter branch into the loop branch with `git merge --no-ff`.
