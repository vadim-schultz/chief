---
name: Chapter C0 - Seed the tree
overview: "Seed the loop branch with the source tree, without its history, lock file, build output or corporate work packages."
id: C0
depends_on: []
touches: ["**"]
execution: chief-of-staff
isProject: false
---

# C0 - Seed the tree

**Depends on:** none · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [01-rollout.md](../01-rollout.md)

## Goal

After this chapter, the loop branch holds the source tree. It has no corporate history, lock file, build output or corporate work package. `./ci.sh all` runs on it.

## Read first

- [00-architecture.md](../00-architecture.md): read invariants I1, I2 and I7, and separation hazards 1 to 3. If this chapter and the architecture disagree, the architecture wins.
- [01-rollout.md](../01-rollout.md): read "Before C0", "Git invariants" and "Per-chapter gate".
- [gaps-and-decisions.md](../gaps-and-decisions.md): read D2, D3, D5, D10, D11, D13 and D14.

## Coordination scope

**Add:**

- Every tracked file of the source tree. Take them from one archive of the source default branch.
- The file named by `CHIEF_LEAK_DENYLIST`. It holds the corporate tokens from the local notes. It stays outside the repository.

**Edit:**

- `.gitignore`: take the union of the source file and the current file.
- `README.md`: replace the stub with a short placeholder. C8 writes the full README.

**Do not edit:**

- `.workpackages/private-distribution/`. Seeding does not touch this folder.
- Git configuration, except the repository-local identity in work item 2.

## Work items

1. **Export the source tree.**
   - Export tracked files only. Write them to an empty directory outside the repository, for example `git -C "$CORPORATE_REPO" archive HEAD | tar -x -C "$SEED_DIR"`.
   - Copy the exported files into the repository. Do not copy `.git`.
   - Remove `.cookiecutter.json`.
   - Remove every corporate work package folder under `.workpackages/`. Keep `.workpackages/private-distribution/`.
   - Record the source commit in the local notes. Do not write it into the repository.

2. **Set the repository identity.**
   - Run `git config --local user.name "Vadim Schultz"`.
   - Run `git config --local user.email vadim.schultz@me.com`.

3. **Create the local denylist.**
   - Copy the corporate token list from the local notes into the file named by `CHIEF_LEAK_DENYLIST`.
   - Keep the file outside the repository.

4. **Confirm that the seed builds.**
   - Run `./ci.sh all` from the repository root.
   - Expected: exit code 0, the same result as in the source repository on this machine.
   - A different result blocks C0. The chief reports the failure. Do not fix the content here.

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| Seed gate | `./ci.sh all` exits 0 on the loop branch | `git ls-files --cached --others --exclude-standard` lists none of `uv.lock`, `dist/`, `.cookiecutter.json` or a corporate work package folder |
| Identity | `git config --local user.email` prints the personal address | No commit on the loop branch has a corporate author address |
| Denylist location | `CHIEF_LEAK_DENYLIST` points to a path outside the repository | `git status --short` does not list the denylist file |

## Review gate

- Check that `git status --short` lists only the seed files, the placeholder README and the `.gitignore` change.
- Check that every commit author on the loop branch uses the personal identity.
- Check that no tracked file matches the denylist. Run `git grep -i -f "$CHIEF_LEAK_DENYLIST" -- . ':!.workpackages/private-distribution'`. Expected: no output.

## Out of scope

- Renaming the package. C1 owns it.
- Adding the leak gate or the hermetic environment. C2 owns them.
- Removing corporate code from the packages. C3 owns it.
- Pushing anything. Rule R5 applies.

## Verification

```bash
# Run from the repository root.
./ci.sh all
git status --short
git ls-files --cached --others --exclude-standard | grep -E '^(uv\.lock|dist/|\.cookiecutter\.json)' || echo "no excluded files"
```

Expected: `./ci.sh all` exits 0. `git status --short` lists the seed files. The last line prints `no excluded files`.

## Refactor report

_Filled in by the chief of staff. This chapter copies files and changes no code. The expected entry is "no refactor needed: seed only"._

## Git workflow

- There is no remote copy of the loop branch before C10. Do not pull.
- Create the loop branch from `main`: `git checkout main`, then `git checkout -b feat/private-distribution`.
- Create the chapter branch: `git checkout -b feat/private-distribution-c00-seed`.
- Commit the seed with the type `chore`. Use the subject `chore: seed the private distribution from the source tree`.
- Merge into the loop branch locally: `git checkout feat/private-distribution`, then `git merge --no-ff feat/private-distribution-c00-seed`.
- Delete the chapter branch: `git branch -d feat/private-distribution-c00-seed`.
- Do not push.
