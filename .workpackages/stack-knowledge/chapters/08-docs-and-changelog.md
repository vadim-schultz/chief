---
name: Chapter C4 - Docs and changelog
overview: "Document the vscode target and the stack packs in the README and CHANGELOG, with a test that the README names every concrete target and never the term MCP."
id: C4
depends_on: ["C1", "C3"]
touches: ["README.md", "CHANGELOG.md", "docs/**", "tests/test_readme.py"]
execution: chapter-implementer
isProject: false
---

# C4 - Docs and changelog

**Depends on:** C1, C3 · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [../01-rollout.md](../01-rollout.md)

## Goal

After this chapter, the README lists the four install targets and what each one installs. The CHANGELOG records the `vscode` target and the stack packs. The README never uses the term MCP. The skills carry the MCP guidance.

## Read first

- [00-architecture.md](../00-architecture.md): invariant I2; section `vscode` target.
- [gaps-and-decisions.md](../gaps-and-decisions.md): decisions D1, D2 and D3, and the answer to O3 from C1's red commit body.
- [01-rollout.md](../01-rollout.md): section Per-chapter gate.

## Coordination scope

**Add:** None.

**Edit:**

- `README.md`: the Supported IDEs table, the install commands and the Commands table. Add the VS Code row. Add the `vscode` option wherever the README lists the targets.
- `CHANGELOG.md`: rename the heading `0.1.0 (not yet released)` to `0.2.0 (not yet released)`, and add the `vscode` target and the stack packs under it (D10).
- `README.md`, install command and release text: replace every `v0.1.0` with `v0.2.0` (D10). The install command reads `uv tool install git+https://github.com/vadim-schultz/chief@v0.2.0`.
- `docs/**`: only where a page repeats a target list. The docs pages include README sections, so most pages need no change.
- `tests/test_readme.py`: add the tests below.

**Do not edit:**

- Any file under `src/chief/`. Owned by C1 and C2a to C3.
- The release tag. Chapter C5 creates it (D10).

## Work items

1. **Red, happy path.** In `tests/test_readme.py`, add `test_readme_lists_every_concrete_target`. It reads the `CONCRETE_TARGETS` tuple and asserts that the README names each member, including `vscode`. Run it. It fails, because the README lists three targets.

2. **Red, negative path.** Add these tests:
   - `test_readme_has_no_v0_1_0_tag`: the README names no `v0.1.0`. It fails before the edit.
   - `test_readme_list_check_rejects_missing_target`: a planted README copy without `vscode` fails the helper that the first test uses.
   - `test_readme_has_no_mcp_term`: the existing `test_readme_has_no_mcp_or_package_index` covers it. Run it, and keep it green. Do not weaken it.
   - `test_changelog_names_vscode_target`: the CHANGELOG heading `0.2.0 (not yet released)` holds the `vscode` target. It fails before the edit.
   - `test_readme_names_release_tag_v0_2_0` (happy path, add with the first test): the README install command names `@v0.2.0`. It fails before the edit.

3. **Green.** Make the smallest change:
   - Add the VS Code row to the Supported IDEs table: target `vscode`, install folder `~/.copilot`, installs skills and agents. State in one sentence that rules are not installed, if O3 gave the default answer. If O3 confirmed a folder, the row names it.
   - Update the install command examples to say `vscode` where they list `cursor`, `claude` and `opencode`.
   - Add the CHANGELOG entry: the `vscode` target, and the five stack packs with their skills.
   - Write one short sentence that says the stack packs add skills for the services a project uses, and that a skill names the MCP server to use. Do not write the word MCP in the README. Write "server" or "documentation index" instead.

4. **Refactor (see Refactor report).**

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| Target list | `test_readme_lists_every_concrete_target` | `test_readme_list_check_rejects_missing_target` |
| MCP term | the existing `test_readme_has_no_mcp_or_package_index` | the same test fails on a planted README containing the term |
| CHANGELOG | `test_changelog_names_vscode_target` | the same test fails before the edit |
| Release tag | `test_readme_names_release_tag_v0_2_0` | `test_readme_has_no_v0_1_0_tag` |

## Review gate

- `grep -i mcp README.md` finds no line.
- Every target in `CONCRETE_TARGETS` appears in the README.
- The CHANGELOG entry says what the target installs, and where.
- `./ci.sh all` exits 0 on the chapter branch.

## Out of scope

- The skill text. Owned by C2a to C2e.
- The release note. Chapter C5 owns it.

## Verification

```bash
# Run from the repository root.
uv run --group test pytest tests/test_readme.py -q
grep -i -n "mcp" README.md || echo "no MCP term in README"
./ci.sh all
```

Expected: pytest exits 0, the grep prints `no MCP term in README`, and `./ci.sh all` exits 0.

## Refactor report

Smells found -> refactorings applied: none. The outcome is observed only (commit 5299cdd):
- Large module: `tests/test_readme.py` is 250 lines, up from 166, against the roughly 100-line guide. A split needs new files, which the touches list does not allow.
- Repeated literal: `"vscode"` appears in four tests, and the README is read in many tests. The literal names the target under test. The two reads of the Installation section are below the rule of three.
- Single source: the README target list appears in six places. The chapter asked to link the other places to one source. A link to `#supported-ides` would break in the docs site, because `docs/usage.md` includes the Commands table and not the Supported IDEs section. The single source in code is `CONCRETE_TARGETS`, which the tests read. The link rule was not applied. Decide whether the rule should change.

The narrow suite stayed green after the green step. The MCP grep on README.md prints nothing.

Audit scope, for the implementer: the README target list appears in more than one place. Keep one source of truth, and link to it from the other places.

## Git workflow

- Check out the loop branch with `git checkout feat/stack-knowledge`. C1 and C3 must already be merged into it.
- Create the chapter branch with `git checkout -b feat/stack-knowledge-c4-docs-and-changelog`.
- Commit the red tests first, then the green change.
- Run the local gate on the chapter branch. It passes when it exits 0.
- Do not push, and do not open a pull request. Remote CI runs once, on the release pull request.
- The chief merges the chapter branch into the loop branch locally, with `git merge --no-ff`.
