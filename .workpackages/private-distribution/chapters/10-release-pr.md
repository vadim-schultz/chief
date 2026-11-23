---
name: Chapter C10 - Release pull request
overview: "Squash the loop branch into one commit, open one pull request into main, run remote CI once on it, merge, and tag v0.1.0. The chief of staff runs this chapter with the user's confirmation at each outward step."
id: C10
depends_on: ["C9"]
touches: []
execution: chief-of-staff
isProject: false
---

# C10 - Release pull request

**Depends on:** C9 · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [../01-rollout.md](../01-rollout.md)

## Goal

After this chapter, `main` holds one squashed commit of the distribution, merged through one pull request. Remote CI runs once on that pull request. The tag `v0.1.0` marks the release.

## Read first

- [00-architecture.md](../00-architecture.md): read invariants I2 and I4.
- [../gaps-and-decisions.md](../gaps-and-decisions.md): read D1, D3, D8 and D9, and open items O1 and O2.
- [../01-rollout.md](../01-rollout.md): read "Before C0" and "Final gate".
- The release chapter template in the work package pack. Its steps are the basis of this chapter.

## Coordination scope

**Add:**

- The tag `v0.1.0`.

**Edit:**

- The loop branch, by squashing it. No file content changes in this chapter.

**Do not edit:**

- Any chapter content. A content fix goes back to the chapter that owns the file. The fix runs on the loop branch, and the gate runs again.

## Work items

The chief of staff runs these steps. Ask the user for confirmation before each outward step: each push, each pull request action, each tag and each repository setting.

1. **Confirm the gate.**
   - Check that open item O1 is answered in writing. If not, stop and report.
   - Check that every chapter row in the ledger shows `done`.
   - Set the ledger's Final gate row to `running`.

2. **Check the visibility.**
   - Run `gh repo view vadim-schultz/chief --json visibility`. Expected: `PRIVATE`.
   - If the output shows `PUBLIC`, stop. The visibility change happens before the work package is pushed (see "Before C0").

3. **Squash the loop branch.**
   - Check the identities: `git log --format='%an <%ae> %cn <%ce>' main..feat/private-distribution`. Expected: only the personal identity.
   - Run `git reset --soft main`, then commit with the subject `feat: import the private chief-of-staff distribution`.

4. **Run the local gate and the leak sweep.**
   - Run `./ci.sh all`. Expected: exit 0.
   - Run `CHIEF_LEAK_STRICT=1 tox -e test-pytest -- tests/test_no_leaks.py`. Expected: exit 0.
   - Record both commands and the commit SHA in the ledger.

5. **Open the pull request and run remote CI once.**
   - Push: `git push -u origin feat/private-distribution`.
   - Open: `gh pr create --base main --head feat/private-distribution --title "feat: import the private chief-of-staff distribution"`. Give a body with the summary and the local gate result.
   - Watch: `gh pr checks --watch`. This is the only remote CI run for this release.
   - Merge: `gh pr merge --merge`.
   - Remote-failure rule: if a check fails, reproduce it locally. Fix it on the loop branch, rerun step 4, then push. Ask the user before a third remote run.

6. **Ruleset (open item O2).**
   - If the plan allows rulesets on private repositories, add a ruleset on `main`. It requires a pull request and blocks force-push and deletion.
   - If not, record "skipped: plan" in the ledger.

7. **Tag the release.**
   - Run `git checkout main && git pull`.
   - Run `git tag -a v0.1.0 -m "v0.1.0"`, then `git push origin v0.1.0`.
   - The tag starts the release workflow only. It runs no CI gate.

8. **Install smoke test.**
   - In a throwaway home directory, with `UV_NO_CONFIG=1` set, run `uv tool install git+https://github.com/vadim-schultz/chief@v0.1.0`.
   - Run `chief doctor`. Expected: exit 0.

9. **Close out.**
   - Delete the local chapter branches and any worktrees.
   - Fill in the Final gate row of the ledger with the pull request URL, the merge result and the tag.
   - Write the footer line `**Last orchestration:** <date> — completed`.

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| Visibility | `gh repo view --json visibility` prints `PRIVATE` | Output `PUBLIC`: stop and report |
| Remote runs | `gh pr checks` shows one green run for the pull request into `main` | A run for a pull request into a loop branch: stop and report |
| Install | `chief doctor` exits 0 in the throwaway home | Any error: stop and do not tag |

## Review gate

- The user reviews the pull request diff before the merge.
- The squashed commit message reads as a single change.
- The strict leak gate reports zero hits.

## Out of scope

- Any content change. Chapters C1 to C9 own content.
- New features.

## Verification

```bash
gh repo view vadim-schultz/chief --json visibility
git log --oneline main..feat/private-distribution
gh pr view --json state,mergedAt,baseRefName,url
gh run list --limit 5
```

Expected: visibility is `PRIVATE` before the push. The range `main..feat/private-distribution` holds one commit before the merge. The pull request state is `MERGED` into `main`. `gh run list` shows one run for the pull request, plus the release run after the tag.

## Refactor report

_No refactor. This chapter changes no content._

## Git workflow

- Work on the loop branch. Do not create a chapter branch.
- The only pull request in this run targets `main`.
- Do not push before step 5. The user confirms the push.
- Use `--merge` for the merge. Do not force-push.
