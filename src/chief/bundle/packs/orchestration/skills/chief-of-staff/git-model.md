# Git model (work package loop)

## Branch roles

| Role | Default name | Purpose |
| --- | --- | --- |
| **Release branch** (`<releaseBranch>`) | `main` | Plan docs must exist here. Final pull request **target** after the whole loop. |
| **Loop branch** (`<loopBranch>`) | user / rollout / `feat/plans-<suite>` | One long-lived branch for **all** chapters in the suite. Chapters integrate into it locally. |
| **Chapter branch** (`<chapterBranch>`) | from chapter doc | Short-lived and local. The chief of staff merges it into the loop branch with `git merge --no-ff`. |

Do **not** push a chapter branch and do **not** open a chapter pull request. Do **not** merge chapters to `<releaseBranch>` until the suite is complete.

## Precedence

Launching the chief of staff requests one pull request: the release pull request, which the release chapter opens after the user confirms. It does not request a chapter pull request or any other pull request.

## Local-first CI

- Every chapter passes the **local gate** on its chapter branch. The chief of staff runs the local gate again on the loop branch after each merge.
- Remote CI runs on the pull request from `<loopBranch>` into `<releaseBranch>`, and on tags. Remote CI does not run per chapter, and no chapter depends on it.

### Local gate

The local gate is one command, run from the repository root. It is `./ci.sh all` unless the chapter or the rollout names another command. The gate passes when the command exits 0. Report it as `local gate: <command> @ <sha>`, where `<sha>` is the commit that the gate ran on. When no command is named, discover one in this order: `scripts/ci.sh`, `./ci.sh`, `make ci`, and the project's documented entry point.

This section is the only definition of the local gate. Other texts link here.

## Loop bootstrap

Before the first chapter, the chief of staff creates the loop branch from the release branch. An implementer does this only when the branch is missing:

```bash
git checkout <releaseBranch> && git pull
git checkout -b <loopBranch>    # skip if the branch already exists locally
```

The loop branch stays local. It is pushed only for the release pull request (see Release).

## Per chapter

```bash
git checkout <loopBranch>
git pull                        # only when <loopBranch> tracks an upstream
git checkout -b <chapterBranch>
# commit the red tests, commit the green change, run the local gate
```

Do **not** push the chapter branch. When the local gate passes, the chief of staff integrates the chapter locally:

```bash
git checkout <loopBranch>
git merge --no-ff <chapterBranch>
./ci.sh all                     # local gate on the loop branch: record the command and the commit
git branch -d <chapterBranch>
```

If the loop branch moved while the chapter ran, merge the loop branch into the chapter branch and run the local gate again before the merge.

## Release (after all chapters)

When every chapter is merged into the loop branch and the local gate passes on the loop branch head, the chief of staff runs the release chapter once:

1. Push the loop branch: `git push -u origin <loopBranch>`.
2. Open one pull request from `<loopBranch>` into `<releaseBranch>` with the combined suite. The `gh` commands are in [host-workflow.md]({{skill_dir:chief-of-staff}}/host-workflow.md).
3. Watch the remote checks with `gh pr checks --watch`, then merge into `<releaseBranch>`.
4. Tag the release. The tag starts the release workflow and no other workflow.

Record the release pull request URL in the run ledger (see the chief-of-staff skill). The chief of staff opens the release pull request. The chapter-implementer does **not** open it. If remote CI fails, follow the remote-failure steps in the release chapter.
