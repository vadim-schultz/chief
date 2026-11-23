---
name: Chapter C4 - Packaging metadata
overview: "Set the packaging files to the MIT license, the GitHub project and the private classifier. Remove every corporate index, mirror and brick tool from the configuration."
id: C4
depends_on: ["C2"]
touches: ["pyproject.toml", "tox.ini", "LICENSE", "docs/conf.py", ".gitignore"]
execution: chapter-implementer
isProject: false
---

# C4 - Packaging metadata

**Depends on:** C2 · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [../01-rollout.md](../01-rollout.md)

## Goal

After this chapter, the packaging files name the MIT license, the GitHub project and the private classifier. They name no corporate index, mirror or brick tool. The tox environments use the hermetic settings.

## Read first

- [00-architecture.md](../00-architecture.md): read invariant I1 and the target layout.
- [../gaps-and-decisions.md](../gaps-and-decisions.md): read D4, D5, D11 and D13.
- [../01-rollout.md](../01-rollout.md): read "Per-chapter gate".
- The source `pyproject.toml`: read the brick tables and the index tables. Do not copy their values.

## Coordination scope

**Add:**

- None.

**Edit:**

- `pyproject.toml`: the license and license files, the authors and maintainers, the project URLs, the classifier `Private :: Do Not Upload`, and the script name. Remove the `[tool.uv]` mirror, the `[[tool.uv.index]]` table and every `[tool.brickmaker*]` table.
- `tox.ini`: remove the corporate default index from `install_command`. Remove the corporate prefixes from `passenv`. Remove the `changelog`, `upload`, `release`, `release-local` and `release-ci` environments. Rename the SBOM output. Add the hermetic `setenv` settings.
- `LICENSE`: the MIT text, with the copyright holder and year.
- `docs/conf.py`: the copyright line and the author.
- `.gitignore`: keep `uv.lock` ignored. Change nothing else unless a check fails.

**Do not edit:**

- `ci.sh`. C2 owns it.
- The workflow files. C7 owns them.
- The README. C8 owns it.

## Work items

1. **Red.**
   - Add `test_pyproject_metadata_is_private_and_mit`. It checks the MIT license, the private classifier and the GitHub project URLs.
   - Add `test_no_corporate_index_in_config`. It checks that `pyproject.toml` has no `[[tool.uv.index]]` table and no `brickmaker` table, and that `tox.ini` sets no default index.
   - Both fail now. Commit them with the type `test`.

2. **Green.**
   - Edit the files listed above.
   - Run `./ci.sh build`. Expected: exit 0, and one source distribution and one wheel in `dist/`.
   - Run `./ci.sh lint`. Expected: exit 0.

3. **Refactor.**
   - Remove the tox environments that only the deleted tooling used.
   - Check that every `{[testenv:...]}` reference still resolves to an existing environment.
   - Record the smells found and the refactorings applied.

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| Metadata | `test_pyproject_metadata_is_private_and_mit` | `test_no_corporate_index_in_config` |
| Tox environments | `test_tox_sets_hermetic_env` | `test_tox_has_no_release_environment` |

## Review gate

- Check that every project URL starts with `https://github.com/vadim-schultz/chief`.
- Check that `LICENSE` contains the MIT text, with only the holder and year changed.
- Check that `dist/` holds the license metadata of the built wheel.

## Out of scope

- The hermetic `ci.sh` exports. C2 owns them.
- Workflow files and the release tooling. C7 owns them.
- The README. C8 owns it.

## Verification

```bash
# Run from the repository root.
./ci.sh build
./ci.sh lint
```

Expected: both commands exit 0.

## Refactor report

Smells found: a long test function with two concerns, the packaging table and the LICENSE text. Refactoring: Extract Function for the missing license markers. Dead code: a build environment dependency with no importer. Refactoring: removed it from the build environment. Observed, not touched: the test module is 119 lines with one concern, so it stays one module. Deprecated alias environments for codestyle, docstyle, errors and security are not tied to the deleted tooling. A placeholder comment remains in the setuptools package-data table. README still names the deleted tooling; C8 owns it.

Data-design gate: not applicable. The diff edits packaging metadata, tox configuration, the license text and the Sphinx copyright line.

Deviations: `./ci.sh build` is not a mode in ci.sh, so the build was checked with `tox -e build`. The red tests are in a new `tests/test_packaging.py`. The test environment's setenv starts with the base block, because tox 4.67 replaces an environment's setenv rather than merging it. The SBOM output is renamed. The copyright line is 2026, Vadim Schultz.

## Git workflow

- Check out the loop branch: `git checkout feat/private-distribution`.
- Create the chapter branch: `git checkout -b feat/private-distribution-c04-packaging`.
- Commit the red tests first, with the type `test`.
- Commit the green change with the type `build`. Use the subject `build: set MIT metadata and remove corporate indexes`.
- Run `./ci.sh all` before the hand-off.
- Do not push. The chief merges the chapter branch into the loop branch with `git merge --no-ff`.
