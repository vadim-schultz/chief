---
name: Chapter C2 - Guards
overview: "Add a hermetic tool environment, a local leak gate with a ratchet, and a bundle contract that holds paths instead of source hashes."
id: C2
depends_on: ["C1"]
touches: ["ci.sh", "tests/test_no_leaks.py", "tests/test_bundle_contract.py", "tests/test_install.py", "tests/fixtures/install_snapshot.json", "src/chief/bundle/sources.json"]
execution: chapter-implementer
isProject: false
---

# C2 - Guards

**Depends on:** C1 · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [../01-rollout.md](../01-rollout.md)

## Goal

After this chapter, `ci.sh` sets a hermetic tool environment. A local leak gate runs in ratchet mode. The bundle contract no longer depends on source hashes, and the install snapshot records paths only.

## Read first

- [00-architecture.md](../00-architecture.md): read invariants I1 and I7. If this chapter and the architecture disagree, the architecture wins.
- [../gaps-and-decisions.md](../gaps-and-decisions.md): read D10, D11, D12 and D14, and open item O3.
- [../01-rollout.md](../01-rollout.md): read "Per-chapter gate".
- `tests/test_bundle_contract.py`: read the rule functions that scan for text, and the planted-text tests that prove each rule fires.

## Coordination scope

**Add:**

- `tests/test_no_leaks.py`.

**Edit:**

- `ci.sh`: add the hermetic exports after `set -euo pipefail`.
- `tests/test_bundle_contract.py`: remove the hash, manifest and completeness tests and the copy list. Move the list of foreign repository names into the local denylist.
- `tests/test_install.py`: compare the snapshot by path only.
- `tests/fixtures/install_snapshot.json`: regenerate it with paths only.

**Delete:**

- `src/chief/bundle/sources.json`.

**Do not edit:**

- `src/chief/bundle/packs/**`. Chapters C3 to C6 own those files.
- `.workpackages/private-distribution/`. The leak gate exempts this folder.

## Work items

1. **Hermetic tool environment.**
   - **Red:** Add `test_ci_exports_hermetic_env`. It checks that `ci.sh` exports `UV_NO_CONFIG`, `PIP_CONFIG_FILE` and `NPM_CONFIG_USERCONFIG`. It fails now.
   - **Green:** Add the three exports after `set -euo pipefail`. If open item O3 needs it, also set the public index in `UV_DEFAULT_INDEX`. Record the answer to O3 in the refactor report.
   - **Refactor:** Keep the exports in one block.

2. **Leak gate.**
   - **Red:** Add `tests/test_no_leaks.py` with two tests. `test_leak_gate_ignores_clean_tree` builds a temporary clean tree and expects no finding. `test_leak_gate_flags_planted_token` builds a temporary tree with one planted generic token and expects one finding. Both fail, because the scanner does not exist yet.
   - **Green:** Implement the scanner. It scans tracked file contents and names, the messages of the `git log` output, the author and committer addresses, and the registry hosts of a tracked `uv.lock`. It reads two layers. The repository layer holds generic names such as `gitlab`, `glab`, `jira`, `confluence`, `atlassian`, `artifactory`, `sonarqube`, `dependency-track`, `brickmaker`, `cookiecutter` and `merge request`. The local layer reads the file named by `CHIEF_LEAK_DENYLIST`.
   - **Ratchet:** Create a baseline once, from the current tree. Store it outside the repository, at the path named by `CHIEF_LEAK_BASELINE`. A run fails when a file has more hits than the baseline. `CHIEF_LEAK_STRICT=1` fails on any hit. The scanner exempts only `.workpackages/private-distribution/`.
   - **Refactor:** Keep one scan function and one list of pattern groups.

3. **Bundle contract and snapshot.**
   - **Red:** Add `test_snapshot_lists_paths_only`. It checks that each snapshot entry is a path. Add `test_snapshot_detects_missing_file`. It removes one file from a temporary install and expects the comparison to fail. Both fail on the current snapshot.
   - **Green:** Delete `src/chief/bundle/sources.json`. Remove its hash, manifest and completeness tests and the copy list from `tests/test_bundle_contract.py`. Replace the list of foreign repository names with a read from the local denylist. Regenerate `install_snapshot.json` with paths only.
   - **Refactor:** Remove helper functions that only the deleted tests used.

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| Hermetic environment | `test_ci_exports_hermetic_env` | `test_uv_ignores_corporate_config` runs `uv pip compile` with a planted configuration file and expects the public index in the output |
| Leak gate | `test_leak_gate_ignores_clean_tree` | `test_leak_gate_flags_planted_token` |
| Snapshot | `test_snapshot_lists_paths_only` | `test_snapshot_detects_missing_file` |

## Review gate

- Run `CHIEF_LEAK_STRICT=0 tox -e test-pytest -- tests/test_no_leaks.py`. Expected: no hit beyond the baseline.
- Check that `tests/test_no_leaks.py` contains no corporate token.
- Check that the gate exempts only `.workpackages/private-distribution/`.
- Record the answer to open item O3 in the refactor report.

## Out of scope

- Removing the corporate content that the gate reports. C3 to C8 own that content.
- Changing bundled text. C5 and C6 own that.

## Verification

```bash
# Run from the repository root.
./ci.sh unit
CHIEF_LEAK_STRICT=0 tox -e test-pytest -- tests/test_no_leaks.py
```

Expected: `./ci.sh unit` exits 0. The leak test passes against the baseline and reports no new hit.

## Refactor report

Refactor gate, tests/test_no_leaks.py: a guard clause for the history surface, an `_is_scanned` predicate for file selection, one path resolver for the denylist and baseline paths, strict and ratchet failures behind one selector, a command table for the CLI, and separate write and commit helpers for the tree builder. Other containing entities: no change needed. Observed, not touched: the module is 424 lines, against the ~100-line guideline. It stays one module because the chapter fixes its path and it has one concern.

Open item O3: `UV_NO_CONFIG=1` stops uv from discovering configuration files. uv never reads pip.conf. Explicit sources still apply, so `ci.sh` also exports `UV_DEFAULT_INDEX=https://pypi.org/simple`, because tox.ini passes a corporate default index explicitly. The uv test needs network access to the public index.

Data-design gate (applicable: new persisted baseline schema, changed snapshot schema). Applied: DD30, strict runs refuse without the local denylist. Observed: DD28, strict mode and the path variables do not reach the tox tests, so tox.ini needs passenv in C4 or C9. DD10, the baseline does not record its inputs. DD21, hosted CI has no denylist, so the local layer passes unchecked there; C7 and C10 must handle it. Accepted risk: DD5, the baseline write re-accepts hits without a record; DD8, the snapshot has no schema_version; DD26, the uv call has no timeout.

## Git workflow

- Check out the loop branch: `git checkout feat/private-distribution`.
- Create the chapter branch: `git checkout -b feat/private-distribution-c02-guards`.
- Commit the red tests first, with the type `test`.
- Commit the green change with the type `chore`. Commit the refactor with the type `refactor`.
- Run `./ci.sh all` and the leak gate before the hand-off.
- Do not push. The chief merges the chapter branch into the loop branch with `git merge --no-ff`.
