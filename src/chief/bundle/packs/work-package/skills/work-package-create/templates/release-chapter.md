---
name: Chapter <CHAPTER ID> - <RELEASE TITLE>
overview: "<ONE SENTENCE: THE RELEASE CHAPTER OPENS THE ONE PULL REQUEST INTO THE RELEASE BRANCH AND TAGS THE RELEASE>"
id: <CHAPTER ID>
depends_on: [<DEPENDENCY CHAPTER IDS>]
touches: []
execution: chief-of-staff
isProject: false
---

# <CHAPTER ID> - <RELEASE TITLE>

**Depends on:** <DEPENDENCY CHAPTER IDS> · **Architecture:** <ARCHITECTURE FILE> · **Rollout:** <ROLLOUT FILE>

## Goal

The release branch holds the whole suite after this chapter. One pull request from the loop branch into the release branch runs remote CI, and a tag on the merged commit starts the release workflow.

## Read first

- <ROLLOUT FILE>: the per-chapter gate and the final gate.
- The chief-of-staff git model, sections Local gate and Release. The local gate is defined there and only there.
- The chief-of-staff host workflow, section Release pull request.

## Coordination scope

**Add:**

- None.

**Edit:**

- None. The chief of staff records the result in the run ledger.

**Do not edit:**

- Every chapter file and every chapter branch. Each chapter is integrated before this chapter runs.

## Work items

The chief of staff runs every step, from the repository root. No implementer runs this chapter.

1. Confirm that every chapter row in the run ledger shows `done`, and that the final gate in the rollout holds.
2. Check out the loop branch with `git checkout <LOOP BRANCH>` and confirm that its working tree is clean.
3. Run the local gate on the loop branch head with `./ci.sh all`. Record `local gate: ./ci.sh all @ <sha>` in the run ledger. Stop when it fails.
4. Push the loop branch with `git push -u origin <LOOP BRANCH>`. This is the first push of the suite.
5. Open the pull request into the release branch with `gh pr create --base main --head <LOOP BRANCH> --title "<subject>" --body "<body>"`. The base is `main`.
6. Watch the remote checks with `gh pr checks --watch`. This is the remote run.
7. Merge the pull request with `gh pr merge --merge`, without `--delete-branch`. Then run `git checkout main && git pull`.
8. Tag the release with `git tag -a v<VERSION> -m "v<VERSION>"` and push it with `git push origin v<VERSION>`. The tag starts the release workflow.

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
| Remote CI | `gh pr checks --watch` reports every check as passed before the merge | A check fails: follow the remote-failure steps in Work items. |

## Review gate

- Every chapter row in the run ledger shows `done`, and the local gate is recorded on the loop branch head.
- The pull request base is the release branch, and its head is the loop branch.
- The count of remote runs is recorded. A third remote run has the user's answer.

## Out of scope

- Chapter implementation. The chapters own it.
- Repository settings and rulesets. The repository owner sets them.

## Verification

```bash
# Run from the repository root.
./ci.sh all
gh pr view <NUMBER> --json state,mergedAt,baseRefName,headRefName,url
git tag --list 'v*'
```

Expected: `./ci.sh all` exits 0. The pull request has `state` `MERGED` and `baseRefName` `main`. The new tag appears in the list.

## Refactor report

_<WHAT THE REFACTOR PASS CHANGED, OR "no refactor needed" WITH THE REASON>_

## Git workflow

- Check out the loop branch with `git checkout <LOOP BRANCH>`.
- Create no chapter branch. The release runs from the loop branch head.
- Commit nothing on the release branch. The pull request is the only change to it.
- Do not force-push and do not skip hooks.
