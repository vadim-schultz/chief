# Host workflow (GitHub)

Branch roles: [git-model.md]({{skill_dir:chief-of-staff}}/git-model.md) (`<releaseBranch>`, `<loopBranch>`, `<chapterBranch>`). The local gate and the local-first CI policy are defined there.

This workflow supports GitHub only. Detect the host once per repository, at preflight:

```bash
git remote get-url origin
```

A URL that contains `github.com` selects GitHub. Any other URL is a blocker: report it and stop.

## Credentials

`gh auth setup-git` makes `gh` the HTTPS credential helper. After it runs, `git pull` and `git push` authenticate through `gh`.

```bash
gh auth setup-git
```

## Preflight

Both commands must succeed before any chapter starts:

```bash
gh auth status
gh repo view --json nameWithOwner,url
```

If either fails, fix the login with `gh auth login -h github.com` and run both commands again.

## Pull request and check state

Use `gh` for pull request state, check state and merge state. Do not use `git fetch` or `git ls-remote` to learn whether a pull request merged or whether checks passed. Use `git` for local work only: checkout, commit, rebase, pull and push.

## Safe `--json` fields

When you use `--json` on a pull request command, request only these fields:

`state`, `mergedAt`, `mergeable`, `mergeStateStatus`, `url`, `headRefName`, `baseRefName`, `statusCheckRollup`, `title`, `number`

The classic Projects field never appears in `--json`. The classic field is deprecated. A deprecation notice from `gh` does not block a chapter.

## GitHub Projects

Board items use `gh project`. The token needs the `project` scope:

```bash
gh auth refresh -s project
gh project item-add <project-number> --owner <owner> --url <pull-request-url>
```

## Merge state over REST

Read merge state through the REST pulls endpoint when you need only that state:

```bash
gh api repos/{owner}/{repo}/pulls/{number} --jq '{state: .state, merged_at: .merged_at, base: .base.ref, head: .head.ref}'
```

In a repository checkout, `gh api` fills in `{owner}` and `{repo}`. Replace `{number}` with the pull request number.

## Chapter integration (local)

A chapter gets no pull request and no remote check. Integrate each chapter into the loop branch locally, as [git-model.md]({{skill_dir:chief-of-staff}}/git-model.md) describes under Per chapter. The commands for a chapter are `git` only: checkout, commit, merge with `--no-ff`, and branch deletion.

## Release pull request (chief of staff, end of loop)

Open a pull request from **`<loopBranch>` into `<releaseBranch>`** when all chapters are merged into the loop branch. See [git-model.md]({{skill_dir:chief-of-staff}}/git-model.md), section Release.

Push the loop branch first, then open the pull request, watch its checks and merge it:

```bash
git push -u origin <loopBranch>
gh pr create --base <releaseBranch> --head <loopBranch> --title "<subject>" --body "<body>"
gh pr checks --watch
gh pr merge --merge
git checkout <releaseBranch> && git pull
```

Merge with `--merge` and without `--delete-branch`. Use merge commits (`--merge`) unless the plan docs say otherwise. Merge only when the user or the plan asks. The default runbook may stop at opening the pull request.

Verify the merge at a chief of staff check-in:

```bash
gh pr view <number> --json state,mergedAt,baseRefName,headRefName,url
gh pr checks <number>
```

Expect `state` to be `MERGED`, `mergedAt` to be set and `baseRefName` to be `<releaseBranch>`.

Required checks: the workflow jobs that the release chapter names.

## Implementer return fields

The full return list is in the chapter-implementer agent. The host supplies these fields for a chapter:

- **local gate:** `<command> @ <sha>`, the local gate and the commit that it ran on.
- **remote ci:** not run (policy). Remote CI runs on the release pull request only.
- **merge:** not merged. The chief of staff merges the chapter branch into the loop branch with `git merge --no-ff`.
