---
name: Chapter C1 - Rename the package
overview: "Rename the package, the command and every runtime marker to chief. The source package name appears in no file under the source tree."
id: C1
depends_on: ["C0"]
touches: ["src/**", "tests/**", "pyproject.toml", "README.md", "docs/**"]
execution: chapter-implementer
isProject: false
---

# C1 - Rename the package

**Depends on:** C0 · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [../01-rollout.md](../01-rollout.md)

## Goal

After this chapter, the package, the import name, the command and the runtime markers use the name `chief`. The old package name appears in no file under `src/` or `tests/`.

## Read first

- [00-architecture.md](../00-architecture.md): read the target layout and decision A4. If this chapter and the architecture disagree, the architecture wins.
- [../01-rollout.md](../01-rollout.md): read "Per-chapter gate".
- [../gaps-and-decisions.md](../gaps-and-decisions.md): read D4.
- The source `pyproject.toml` in the seed: read it once to learn the old package name. Export it as `OLD_PACKAGE_NAME` in your shell. Do not write the name into any file.

## Coordination scope

**Add:**

- None.

**Edit:**

- The package directory under `src/`. Rename it to `src/chief/`.
- Every import of the old name in `src/` and `tests/`.
- `pyproject.toml`: the project name, the script entry, the package data, the coverage source and the version file path.
- `src/chief/targets/locations.py`: the state directory name becomes `chief`.
- `src/chief/rendering/managed_block.py`: the begin and end markers become `<!-- chief:begin -->` and `<!-- chief:end -->`.
- `src/chief/cli/entry.py` and `src/chief/cli/app.py`: the program name and the logger name.
- `src/chief/__main__.py`: the module docstring.
- `README.md` and `docs/**`: the command and package names.
- Test literals in `tests/test_install.py`, `tests/test_render.py`, `tests/test_locations.py`, `tests/test_main.py` and `tests/test_readme.py`.
- `tests/fixtures/install_snapshot.json`: regenerate it when the marker text changes the installed bytes.

**Do not edit:**

- The skill and agent names `chief-of-staff` and `chapter-implementer`. Decision D4 keeps them.
- `.workpackages/`.

## Work items

1. **Rename the package directory.**
   - **Red:** Add `test_src_holds_only_chief_package`. It checks that `src/` holds one package directory, `chief`. Add `test_state_dir_is_chief`. It checks that the state directory name is `chief`. Both fail on the old names. Commit the red tests with the type `test`.
   - **Green:** Run `git mv` on the package directory to `src/chief`. Rewrite the imports and the names listed above. Run `./ci.sh unit`. Expected: both red tests pass.
   - **Refactor:** Run `ruff check --select I` and fix the import order. Look for a module docstring that still names the old package. Run the narrow suite after each step.

2. **Rename the markers.**
   - **Red:** Add `test_managed_block_markers_use_chief`. It checks the begin marker `<!-- chief:begin -->` and the end marker `<!-- chief:end -->`. It fails on the old markers.
   - **Green:** Change the two constants in `managed_block.py`. Update the tests that assert the old markers. If the install snapshot test fails, regenerate `tests/fixtures/install_snapshot.json`. Record the change in the refactor report.
   - **Refactor:** Check that each marker appears in one constant only.

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| Package name | `test_src_holds_only_chief_package` | `test_no_source_package_name_in_tree` reads the denylist and fails on any hit under `src/` or `tests/` |
| Runtime names | `test_state_dir_is_chief` | `test_managed_block_markers_use_chief` fails on the old markers |

## Review gate

- Run `git grep -n -F "$OLD_PACKAGE_NAME" -- src tests`. Expected: no output.
- Check that `pyproject.toml` declares the script `chief` and no other command.
- Check that no skill or agent directory name changed.

## Out of scope

- Removing corporate content. C3 and C5 own it.
- The corporate names in the bundled skill text. C5 owns those.
- The hermetic environment. C2 owns it.

## Verification

```bash
# Run from the repository root.
./ci.sh unit
git grep -n -F "$OLD_PACKAGE_NAME" -- src tests || echo "no old package name in src or tests"
```

Expected: `./ci.sh unit` exits 0. The last line prints `no old package name in src or tests`.

## Refactor report

_To be filled by the implementer before the chapter commit. State what the refactor pass changed, or "no refactor needed" with the reason._

## Git workflow

- Check out the loop branch: `git checkout feat/private-distribution`. There is no remote copy to pull.
- Create the chapter branch: `git checkout -b feat/private-distribution-c01-rename`.
- Commit the red tests first, with the type `test`.
- Commit the green change and the refactor with the type `refactor`. Use the subject `refactor: rename the package to chief`.
- Run `./ci.sh all` before the hand-off.
- Do not push. The chief merges the chapter branch into the loop branch with `git merge --no-ff`.
