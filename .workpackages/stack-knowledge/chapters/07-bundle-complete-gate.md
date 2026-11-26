---
name: Chapter C3 - Bundle complete gate
overview: "Assert that the bundle holds exactly the five stack packs, that every stack skill passes the contract across packs, and regenerate the install snapshot for all four targets."
id: C3
depends_on: ["C2b", "C2c", "C2d", "C2e"]
touches: ["tests/test_stack_knowledge.py", "tests/test_packs.py", "tests/fixtures/install_snapshot.json"]
execution: chapter-implementer
isProject: false
---

# C3 - Bundle complete gate

**Depends on:** C2b, C2c, C2d, C2e · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [../01-rollout.md](../01-rollout.md)

## Goal

After this chapter, the bundle is complete, and its tests say so. The five stack packs exist. Every stack skill passes the contract. The install snapshot lists the stack paths for all four targets. Nothing else changes.

## Read first

- [00-architecture.md](../00-architecture.md): section Pack layout; invariants I1 to I5.
- [01-rollout.md](../01-rollout.md): section Scheduling matrix, row C3; section Per-chapter gate.
- [02-stack-docs.md](02-stack-docs.md): the checker that C3 runs across all packs.

## Coordination scope

**Add:** None.

**Edit:**

- `tests/test_stack_knowledge.py`: add the cross-pack tests. Do not change the checker. The checker belongs to C2a.
- `tests/test_packs.py`: replace the open-ended `stack-*` discovery with the exact set of five stack packs.
- `tests/fixtures/install_snapshot.json`: regenerate it for the four targets.

**Do not edit:**

- Any file under `src/chief/bundle/packs/`. A content defect goes back to the chapter that owns the pack, through the chief of staff.
- The `vscode` target code. Owned by C1.

## Work items

1. **Red, happy path.** Add `test_real_bundle_holds_every_planned_stack_pack` to `tests/test_packs.py`. It asserts that the stack packs on disk equal `{stack-docs, stack-cloud, stack-data-services, stack-python, stack-web}`. Run it on the chapter branch before the snapshot change. It must pass, because C2b to C2e are integrated. Then run it with one pack folder temporarily renamed, and confirm that it fails. Restore the name before you commit.

2. **Red, cross-pack tests.** Add to `tests/test_stack_knowledge.py`:
   - `test_every_stack_skill_passes_contract`: the checker runs over every stack skill outside `stack-docs`.
   - `test_stack_packs_name_no_project_identifier`: the identifier scan runs over every file of every stack pack. The scan includes the sibling project's name (decision D9).
   - `test_every_stack_description_is_within_limit`: each description is 300 characters or fewer.

   Each must pass. If one fails, the failure names the skill, and the chapter goes back to its owner.

3. **Red, snapshot.** The existing `test_install_all_matches_recorded_snapshot` fails, because the snapshot has no stack paths. Confirm that it fails for that reason and no other.

4. **Negative path.** Add `test_snapshot_refuses_mcp_config_paths`: no path in the snapshot is an MCP configuration file, such as `mcp.json`, `.mcp.json`, `opencode.json` or `mcp-config.json`. Confirm it passes.

5. **Green.** Regenerate `tests/fixtures/install_snapshot.json`:
   - Install all four targets into an isolated `HOME`.
   - Write the sorted list of relative paths, as the existing file does. Keep the format that `test_snapshot_lists_paths_only` expects.
   - Record the command in the commit body. Do not add a script for it.

6. **Refactor (see Refactor report).**

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| Pack set | `test_real_bundle_holds_every_planned_stack_pack` | a planted extra pack fails the strict set check (add it to the test) |
| Contract across packs | `test_every_stack_skill_passes_contract` | the checker rejects a planted skill (C2a test) |
| Identifier scan across packs | `test_stack_packs_name_no_project_identifier` | a planted hostname or a planted sibling-project name fails |
| Description length | `test_every_stack_description_is_within_limit` | a planted 301-character description fails |
| Snapshot | `test_install_all_matches_recorded_snapshot` | `test_snapshot_refuses_mcp_config_paths` |

## Review gate

- The snapshot diff adds stack paths for all four targets, and it removes nothing that the `vscode` work in C1 did not already add.
- No MCP configuration file appears in the snapshot.
- `./ci.sh all` exits 0 on the chapter branch.

## Out of scope

- Editing any pack. Owned by C2b to C2e.
- README and CHANGELOG text. Owned by C4.

## Verification

```bash
# Run from the repository root.
uv run pytest tests/test_stack_knowledge.py tests/test_packs.py tests/test_install.py -q
./ci.sh all
```

Expected: both commands exit 0.

## Refactor report

_Pending. The implementer fills this in during the refactor pass. Name the containing entity, the arms of each decision, and the outcome._

Audit scope, for the implementer: the set assertions in `tests/test_packs.py`. If the same set appears in two tests, extract one constant.

## Git workflow

- Check out the loop branch with `git checkout feat/stack-knowledge`. C2b to C2e must already be merged into it.
- Create the chapter branch with `git checkout -b feat/stack-knowledge-c3-bundle-complete-gate`.
- Commit the red tests first, then the green change.
- Run the local gate on the chapter branch. It passes when it exits 0.
- Do not push, and do not open a pull request. Remote CI runs once, on the release pull request.
- The chief merges the chapter branch into the loop branch locally, with `git merge --no-ff`.
