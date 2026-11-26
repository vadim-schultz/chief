---
name: Chapter C5 - Release
overview: "The release chapter runs the live checks, opens one pull request from the loop branch into main after the user confirms, and tags the merged commit v0.2.0."
id: C5
depends_on: ["C1", "C3", "C4"]
touches: []
execution: chief-of-staff
isProject: false
---

# C5 - Release

**Depends on:** C1, C3, C4 · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [../01-rollout.md](../01-rollout.md)

## Goal

The release branch holds the whole work package after this chapter. One pull request from the loop branch into `main` runs remote CI. The tag `v0.2.0` is created on the merged commit (D10). The tag starts the release workflow in `.github/workflows/release.yml`.

## Read first

- [01-rollout.md](../01-rollout.md): section Final gate and section Per-chapter gate.
- The chief-of-staff git model, sections Local gate and Release. The local gate is defined there and only there.
- The chief-of-staff host workflow, section Release pull request.

## Coordination scope

**Add:** None.

**Edit:** None. The chief of staff records the result in the run ledger.

**Do not edit:**

- Every chapter file and every chapter branch. Each chapter is integrated before this chapter runs.
- The release branch. The pull request is the only change to it.

## Work items

The chief of staff runs every step, from the repository root. No implementer runs this chapter.

1. Confirm that every chapter row in the run ledger reads `done`, and that the final gate in the rollout holds.
2. Run the live checks. Record each result in the run ledger.
   - `./ci.sh all` on the loop branch head. Record `local gate: ./ci.sh all @ <sha>`.
   - The leak gate in strict mode: `CHIEF_LEAK_STRICT=1 ./ci.sh all`. The denylist comes from the file that `CHIEF_LEAK_DENYLIST` names. Stop when it fails.
   - A dry run: `chief install --target vscode --dry-run`.
   - A real install into a temporary `HOME` and `XDG_CONFIG_HOME` and `XDG_STATE_HOME`, for each of the four targets: `chief install --target all`.
   - `chief doctor` against the temporary `HOME`. It reports no drift.
   - `chief export --target all --output <an empty temporary folder>`.
   - Stop when any check fails. Report the output to the user.
3. Ask the user to confirm the release. Do not push until the user answers.
4. After the confirmation, check out the loop branch with `git checkout feat/stack-knowledge` and confirm that its working tree is clean.
5. Push the loop branch with `git push -u origin feat/stack-knowledge`. This is the first push of the work package.
6. Open the pull request into `main` with `gh pr create --base main --head feat/stack-knowledge --title "<subject>" --body "<body>"`. The body names the chapters and the local gate line.
7. Watch the remote checks with `gh pr checks --watch`. This is the remote run.
8. Merge the pull request with `gh pr merge --merge`, without `--delete-branch`. Then run `git checkout main && git pull`.
9. Tag the merged commit: `git tag -a v0.2.0 -m "v0.2.0"`, then `git push origin v0.2.0`. The tag starts `release.yml`.

If remote CI fails:

1. Reproduce the failure locally with the command that the failed check ran.
2. Fix it on the loop branch.
3. Rerun the local gate and record the new `local gate` line.
4. Push the loop branch. This is the second remote run.
5. Ask the user before a third remote run. Push nothing until the user answers.

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| Local gate | `./ci.sh all` exits 0 on the loop branch head | The gate fails: stop before the push. Nothing is pushed or tagged. |
| Leak gate, strict | `CHIEF_LEAK_STRICT=1 ./ci.sh all` exits 0 | A hit: stop, and report the file and the line. Do not print the denylist term. |
| Live install | `chief install --target all` into a temporary `HOME` exits 0, and `chief doctor` reports no drift | Any refusal: stop before the push. |
| Remote CI | `gh pr checks --watch` reports every check as passed before the merge | A check fails: follow the remote-failure steps in Work items. |

## Review gate

- Every chapter row in the run ledger shows `done`, and the local gate is recorded on the loop branch head.
- The leak gate passed in strict mode, and the result is recorded.
- The pull request base is `main`, and its head is `feat/stack-knowledge`.
- The count of remote runs is recorded. A third remote run has the user's answer.

## Out of scope

- Chapter implementation. The chapters own it.
- Repository settings and rulesets. The repository owner sets them.

## Verification

```bash
# Run from the repository root.
CHIEF_LEAK_STRICT=1 ./ci.sh all
gh pr view <NUMBER> --json state,mergedAt,baseRefName,headRefName,url
git tag --list 'v*'
```

Expected: the strict gate exits 0. The pull request has `state` `MERGED` and `baseRefName` `main`. The tag `v0.2.0` appears in the list.

## Refactor report

_No refactor needed. This chapter runs commands and writes no code._

## Git workflow

- Check out the loop branch with `git checkout feat/stack-knowledge`.
- Create no chapter branch. The release runs from the loop branch head.
- Commit nothing on the release branch. The pull request is the only change to it.
- Do not force-push and do not skip hooks.
