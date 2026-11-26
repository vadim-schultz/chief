---
name: Chapter C1 - VS Code target
overview: "Add vscode as a concrete install target that writes skills and agents under ~/.copilot, with rules unsupported unless the official docs confirm a personal instructions folder."
id: C1
depends_on: []
touches: ["src/chief/targets/names.py", "src/chief/targets/registry.py", "src/chief/targets/locations.py", "src/chief/catalogue/bundle_tree.py", "src/chief/installation/planner.py", "src/chief/cli/commands.py", "tests/test_render.py", "tests/test_locations.py", "tests/test_api.py", "tests/test_cli.py", "tests/test_export.py", "tests/test_install.py", "tests/fixtures/install_snapshot.json"]
execution: chapter-implementer
isProject: false
---

# C1 - VS Code target

**Depends on:** none · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [../01-rollout.md](../01-rollout.md)

## Goal

After this chapter, `chief install --target vscode` writes the skills and agents of every pack under `~/.copilot`. `chief install --target all` installs into four targets. The `claude` target is unchanged.

## Read first

- [00-architecture.md](../00-architecture.md): sections Design, `vscode` target; invariants I1, I6 and I7.
- [gaps-and-decisions.md](../gaps-and-decisions.md): decisions D2 and D3, and open question O3.
- [01-rollout.md](../01-rollout.md): section Per-chapter gate.

## Coordination scope

**Add:**

- None. Every change lands in an existing file.

**Edit:**

- `src/chief/targets/names.py`: add the `vscode` member and extend `CONCRETE_TARGETS`.
- `src/chief/targets/registry.py`: add the `vscode` spec, and a per-kind placement policy (see Work items).
- `src/chief/targets/locations.py`: only if the config root needs a new base. It should not.
- `src/chief/catalogue/bundle_tree.py`: replace the `_in_block` special case with the placement policy.
- `src/chief/installation/planner.py`: add `mcp-config.json` to the refused names.
- `src/chief/cli/commands.py`: derive the target help text from `Target`, and print one line for each skipped rule.
- The tests and the snapshot listed in `touches`.

**Do not edit:**

- Every file under `src/chief/bundle/packs/` belongs to C2a to C2e.
- `README.md`, `CHANGELOG.md` and `docs/**` belong to C4.

## Work items

1. **Verify first.** Read these pages with a fetch tool:
   - https://code.visualstudio.com/docs/agent-customization/agent-skills
   - https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference

   Record in the red commit body: the personal skill folder, the personal agent folder, and whether a personal instructions folder exists. Answer O3 from this evidence. If no personal instructions folder is confirmed, rules are unsupported for `vscode`.

2. **Red, happy path.** Add these tests and confirm each fails for the missing behaviour:
   - `tests/test_render.py::test_vscode_paths_and_frontmatter`: the skill renders to `skills/tdd/SKILL.md` and the agent renders to `agents/chapter-implementer.agent.md`, both under the given root.
   - `tests/test_install.py::test_install_vscode_writes_tree_under_copilot_root`: an install into an isolated `HOME` writes only under `~/.copilot`.
   - `tests/test_locations.py::test_vscode_config_root_is_copilot_under_home`: the root is `<home>/.copilot`.
   - `tests/test_cli.py::test_cli_install_vscode_dry_run_exits_0`: the dry run exits 0 and writes nothing.
   - `tests/test_api.py`: the concrete target set equals `{cursor, claude, opencode, vscode}`.
   - `tests/test_export.py`: exporting `vscode` writes its skill and agent files.

3. **Red, negative path.** Add these tests:
   - `tests/test_render.py::test_unknown_target_is_rejected`: change the name from the placeholder `vscode` to `no-such-target`. It still raises `UnknownTargetError`.
   - `tests/test_cli.py::test_cli_install_misspelled_vscode_exits_2`: `--target vscod` exits 2 and writes no file under the isolated `HOME`.
   - `tests/test_install.py::test_planner_refuses_copilot_mcp_config`: a planned `~/.copilot/mcp-config.json` gets the `refuse` action.
   - `tests/test_install.py::test_vscode_rules_are_skipped_when_unsupported`: no file appears under `~/.copilot/instructions`. The `Tree` reports the skipped rule names. Skip this test if O3 confirms a personal folder, and write the matching rule test instead.

4. **Green.** Make the smallest change for each red test:
   - Add `Target.VSCODE = "vscode"` and append it to `CONCRETE_TARGETS`.
   - Add the `vscode` entry to `TARGETS`: base `home`, directory `.copilot`, skill path `skills/{name}/SKILL.md`, agent path `agents/{name}.agent.md`.
   - Give each target a placement for each kind: `FILE`, `BLOCK` or `SKIP`. Today `opencode` puts rules in a block, `cursor` and `claude` write files, and `vscode` skips rules when O3 is unanswered.
   - Make `BundleTree` read the placement and stop comparing target names.
   - Print one line for each skipped rule from the install command.
   - Regenerate `tests/fixtures/install_snapshot.json` only after the install test is green, and only with the four-target install.

5. **Refactor (see Refactor report).**

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| Target paths | `test_vscode_paths_and_frontmatter` | `test_unknown_target_is_rejected` |
| Install location | `test_install_vscode_writes_tree_under_copilot_root` | `test_vscode_rules_are_skipped_when_unsupported` |
| CLI argument | `test_cli_install_vscode_dry_run_exits_0` | `test_cli_install_misspelled_vscode_exits_2` |
| Config root | `test_vscode_config_root_is_copilot_under_home` | `test_vscode_root_ignores_xdg_config_home` (add with the happy test) |
| MCP refusal | the existing `test_mcp_config_files_are_never_touched` still passes | `test_planner_refuses_copilot_mcp_config` |
| Snapshot | `test_install_all_matches_recorded_snapshot` after regeneration | `test_snapshot_lists_paths_only` still passes |

## Review gate

- Every red test failed before the green change, and the failure names the missing behaviour.
- The refusal for `mcp-config.json` is tested, and no test was weakened to pass.
- `./ci.sh all` exits 0 on the chapter branch.
- The commit body of the red commit records the verified facts and the answer to O3.

## Out of scope

- Skill and agent contents. Owned by C2a to C2e.
- README and CHANGELOG text for the target. Owned by C4.
- Writing MCP configuration. Refused by design (I1, D1).

## Verification

```bash
# Run from the repository root.
uv run pytest tests/test_render.py tests/test_locations.py tests/test_install.py tests/test_cli.py tests/test_api.py tests/test_export.py -q
./ci.sh all
```

Expected: the narrow run exits 0 with the new tests passing. `./ci.sh all` exits 0.

## Refactor report

_Pending. The implementer fills this in during the refactor pass. Name the containing entity, the arms of each decision, and the outcome._

Audit scope, for the implementer:

- `TARGETS` and `TargetSpec` in `src/chief/targets/registry.py`.
- `BundleTree` in `src/chief/catalogue/bundle_tree.py`. Count the placement arms, including the existing `opencode` block case.
- The install command in `src/chief/cli/commands.py`, including the five help strings.

## Git workflow

- Check out the loop branch with `git checkout feat/stack-knowledge`.
- Create the chapter branch with `git checkout -b feat/stack-knowledge-c1-vscode-target`.
- Commit the red tests first, then the green change.
- Run the local gate on the chapter branch. It passes when it exits 0.
- Do not push, and do not open a pull request. Remote CI runs once, on the release pull request.
- The chief merges the chapter branch into the loop branch locally, with `git merge --no-ff`.
