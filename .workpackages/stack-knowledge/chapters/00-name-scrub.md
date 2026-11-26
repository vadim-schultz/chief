---
name: Chapter C0 - Name scrub
overview: "Remove the sibling project's name from the shipped package, and add a test that fails when any file under the package names it again."
id: C0
depends_on: []
touches: ["src/chief/bundle/packs/orchestration/skills/chief-of-staff/SKILL.md", "tests/test_sibling_name.py"]
execution: chapter-implementer
isProject: false
---

# C0 - Name scrub

**Depends on:** none · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [../01-rollout.md](../01-rollout.md)

## Goal

After this chapter, no file under `src/chief/` names the sibling project. The description of the chief-of-staff skill says "work package", not the project's name. A test keeps the name out of the package from now on.

## Read first

- [00-architecture.md](../00-architecture.md): invariant I9.
- [gaps-and-decisions.md](../gaps-and-decisions.md): decision D9.
- [01-rollout.md](../01-rollout.md): section Per-chapter gate.

## Coordination scope

**Add:**

- `tests/test_sibling_name.py`

**Edit:**

- `src/chief/bundle/packs/orchestration/skills/chief-of-staff/SKILL.md`: line 3, the `description` field. Remove the project name. The text otherwise stays the same.

**Do not edit:**

- Any other file under `src/chief/`. A hit in another file is a finding. Report it to the chief of staff before you change it.
- `.workpackages/private-distribution/**`. It is exempt from the leak gate and it is a historical record.

## Work items

1. **Red, happy path.** Add `tests/test_sibling_name.py` with `test_shipped_package_names_no_sibling_project`. It scans every text file under `src/chief/` and asserts that no line matches the name. The pattern must match the name in any case, with an optional hyphen or underscore between the two words. Build the pattern from parts, so that the test file does not contain the name in one piece. Run it. It fails, and the hit is `src/chief/bundle/packs/orchestration/skills/chief-of-staff/SKILL.md`, line 3.

2. **Red, negative path.** Add `test_planted_name_is_reported`. It writes a planted file with one line that names the project into a temporary folder, runs the same scanner over that folder, and asserts that the scanner reports the file and the line number. It passes when the scanner works. It fails before the scanner exists, if you write the test first.

3. **Green.** Edit the `description` line of `chief-of-staff/SKILL.md`. Remove the project name, and change nothing else. The line becomes: `description: Orchestrate a work package from its plan folder by scheduling independent chapter-implementer agents in parallel whenever dependencies and file ownership permit, then integrating their reviewable changes into the loop branch.` Run both tests. Both pass.

4. **Refactor (see Refactor report).**

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| Shipped package | `test_shipped_package_names_no_sibling_project` | `test_planted_name_is_reported` |

## Review gate

- `grep -rn -i -E "red[-_]?tape" src/` finds no line. Run it on the chapter branch, and record the empty result in the commit body.
- No other test that pins the description text fails. Run `uv run pytest tests/test_skill_contracts.py tests/test_bundle_contract.py -q`.
- `./ci.sh all` exits 0 on the chapter branch.

## Out of scope

- The installed copy of the skill in a user's home folder. It changes only when the user runs `chief install` again.
- The `private-distribution` run ledger, which records an earlier decision about this name. See the note in the release summary.
- The stack packs. Owned by C2a to C2e. They must never contain the name (I9).

## Verification

```bash
# Run from the repository root.
uv run pytest tests/test_sibling_name.py tests/test_skill_contracts.py tests/test_bundle_contract.py -q
grep -rn -i -E "red[-_]?tape" src/ || echo "no sibling-project name in src/"
./ci.sh all
```

Expected: pytest exits 0. The grep prints `no sibling-project name in src/`. `./ci.sh all` exits 0.

## Refactor report

Smells found -> refactorings applied (chapter branch commit 16591b9):
- Long Function and Loops: `_name_hits` held the file walk, the read and the match in one nested comprehension. Applied: Extract Function `_files_under` and `_file_hits`.
- Mysterious Name: the loop variable `line` held text, while `Hit.line` holds a line number. Applied: Rename Variable `line` to `text`.

The narrow suite stayed green after each step. Comments and module constants were left alone.

Observed, not changed (follow-ups):
- The walk and match code is duplicated in `tests/test_bundle_contract.py` and `tests/test_bundle_scrub.py`. Sharing it needs edits to those files.
- The scan reads every file under `src/chief/`, so a local `__pycache__` would be scanned too. Excluding it needs a test that the chapter does not name.
- The gate prints a pre-existing ruff warning about rule COM812. The gate passed.

Audit scope, for the implementer: the new scanner and the existing scanners in `tests/test_bundle_contract.py` and `tests/test_bundle_scrub.py` both walk the bundle and match patterns. If they share the walk, extract one helper. Do not change the behaviour of the existing tests.

## Git workflow

- Check out the loop branch with `git checkout feat/stack-knowledge`.
- Create the chapter branch with `git checkout -b feat/stack-knowledge-c0-name-scrub`.
- Commit the red test first, then the green change.
- Run the local gate on the chapter branch. It passes when it exits 0.
- Do not push, and do not open a pull request. Remote CI runs once, on the release pull request.
- The chief merges the chapter branch into the loop branch locally, with `git merge --no-ff`.
