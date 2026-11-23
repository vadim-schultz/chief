---
name: Chapter C9 - Final sweep
overview: "Run the leak gate in strict mode over the tree, the history and the built artifacts. Fix every remaining hit at its source."
id: C9
depends_on: ["C8"]
touches: ["tests/test_ci_skill_doc.py", "tests/test_packs.py", "tests/test_install.py", "tests/test_no_leaks.py"]
execution: chapter-implementer
isProject: false
---

# C9 - Final sweep

**Depends on:** C8 · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [../01-rollout.md](../01-rollout.md)

## Goal

After this chapter, the strict leak gate finds no hit in the tree, the history or the built artifacts. The remaining tests pass.

## Read first

- [00-architecture.md](../00-architecture.md): read invariants I1, I6 and I7.
- [../gaps-and-decisions.md](../gaps-and-decisions.md): read D10 and D14.
- `tests/test_no_leaks.py`: read the scanner that chapter C2 wrote.

## Coordination scope

**Add:**

- None.

**Edit:**

- `tests/test_no_leaks.py`: add the artifact scan. Make strict mode the default for the release run.
- `tests/test_ci_skill_doc.py`: remove the corporate token from the list of outside text. Read the list from the denylist instead.
- `tests/test_packs.py`: check the pack list.
- `tests/test_install.py`: use `tmp_path` instead of a fixed temporary path.

**Do not edit:**

- Source files, except where the strict run finds a hit that an earlier chapter missed. Record each such fix in the refactor report. Do not add any exemption except `.workpackages/private-distribution/`.

## Work items

1. **Strict run on the tree and the history.**
   - **Red:** Add `test_leak_gate_is_strict_after_sweep`. It runs the scanner with `CHIEF_LEAK_STRICT=1` over the tree and the history, and expects no hit. It fails on the remaining hits. Commit it with the type `test`.
   - **Green:** Fix each hit at its source. Do not add exemptions.

2. **Artifact scan.**
   - **Red:** Add `test_built_artifacts_are_clean`. It builds the source distribution and the wheel, extracts each into its own empty directory, and expects no hit. Add `test_artifact_scan_flags_planted_hit`. It plants one hit in a temporary archive and expects a finding.
   - **Green:** Add the artifact scan to `tests/test_no_leaks.py`. Use the same patterns as the tree scan.
   - **Refactor:** Keep one scan function for the tree, the history and the artifacts.

3. **Test lists.**
   - **Green:** Remove the corporate names from `tests/test_ci_skill_doc.py` and `tests/test_packs.py`. Move the temporary home in `tests/test_install.py` to `tmp_path`.
   - **Refactor:** Remove helper code that repeats across these modules.

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| Strict tree and history | `test_leak_gate_is_strict_after_sweep` | `test_leak_gate_flags_planted_token`, run in strict mode |
| Artifacts | `test_built_artifacts_are_clean` | `test_artifact_scan_flags_planted_hit` |

## Review gate

- Run the strict gate over the tree, the history and the artifacts. Expected: no hit outside `.workpackages/private-distribution/`.
- Check that no test file contains a corporate token.
- Record the list of fixes made in the refactor report.

## Out of scope

- Repository settings. C10 owns them.
- New features.

## Verification

```bash
# Run from the repository root.
CHIEF_LEAK_STRICT=1 tox -e test-pytest -- tests/test_no_leaks.py
./ci.sh all
git log --format='%an <%ae>%n%cn <%ce>%n%B' feat/private-distribution
```

Expected: the strict leak test passes. `./ci.sh all` exits 0. The history lists only the personal identity.

## Refactor report

_To be filled by the implementer before the chapter commit. List each fix made outside the test files._

## Git workflow

- Check out the loop branch: `git checkout feat/private-distribution`.
- Create the chapter branch: `git checkout -b feat/private-distribution-c09-final-sweep`.
- Commit the red tests first, with the type `test`.
- Commit the fixes with the type `fix` or `refactor`, as each change requires.
- Run `./ci.sh all` and the strict leak gate before the hand-off.
- Do not push. The chief merges the chapter branch into the loop branch with `git merge --no-ff`.
