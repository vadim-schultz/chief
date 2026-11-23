---
name: Chapter C3 - Remove corporate code
overview: "Remove the MCP server setup, the MCP snippet command and the corporate build environment. The installer keeps refusing MCP configuration paths."
id: C3
depends_on: ["C2"]
touches: ["src/chief/mcp/**", "src/chief/api.py", "src/chief/cli/**", "src/chief/bundle/packs/mcp/**", "src/chief/bundle/packs/orchestration/skills/chief-of-staff/corporate-build-env.md", "src/chief/bundle/packs/orchestration/skills/chief-of-staff/SKILL.md", "src/chief/bundle/packs/orchestration/agents/chapter-implementer.md", "tests/test_mcp_snippet.py", "tests/test_cli.py", "tests/test_api.py", "tests/test_packs.py", "tests/fixtures/install_snapshot.json"]
execution: chapter-implementer
isProject: false
---

# C3 - Remove corporate code

**Depends on:** C2 · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [../01-rollout.md](../01-rollout.md)

## Goal

After this chapter, the package holds no MCP server setup, no MCP snippet command and no corporate build environment. The installer still refuses MCP configuration paths.

## Read first

- [00-architecture.md](../00-architecture.md): read invariant I3 and the separation hazards. If this chapter and the architecture disagree, the architecture wins.
- [../gaps-and-decisions.md](../gaps-and-decisions.md): read D7 and D12.
- [../01-rollout.md](../01-rollout.md): read "Per-chapter gate".
- The `SKILL.md` and `chapter-implementer.md` files of the orchestration pack: read every line that links the corporate build environment file.

## Coordination scope

**Add:**

- None.

**Edit:**

- `src/chief/api.py`: remove the `mcp_snippet` method and its imports.
- `src/chief/cli/app.py`: remove the registration of the `mcp-snippet` command.
- `src/chief/cli/commands.py`: remove the MCP snippet command and its helpers.
- `src/chief/bundle/packs/orchestration/skills/chief-of-staff/SKILL.md`: remove the links and mentions of the corporate build environment.
- `src/chief/bundle/packs/orchestration/agents/chapter-implementer.md`: remove the corporate build environment section.
- `tests/test_cli.py`, `tests/test_api.py`, `tests/test_packs.py`: remove the tests of the removed parts.
- `tests/fixtures/install_snapshot.json`: regenerate it with paths only.

**Delete:**

- `src/chief/mcp/`.
- `src/chief/bundle/packs/mcp/`.
- `src/chief/bundle/packs/orchestration/skills/chief-of-staff/corporate-build-env.md`.
- `tests/test_mcp_snippet.py`.

**Do not edit:**

- `src/chief/installation/planner.py`. Its refusal rule for MCP configuration files stays. It is a safety rule with its own tests.
- Any other pack. C5 and C6 own those.

## Work items

1. **Red for the command removal.**
   - Add `test_cli_has_no_mcp_snippet_command`. It checks that the command list holds only `list`, `install`, `uninstall`, `doctor` and `export`. It fails now. Commit it with the type `test`.

2. **Green.**
   - Delete the paths listed above. Remove the command and the API method. Edit `SKILL.md` and the agent text. Remove the removed packs from the pack list in `tests/test_packs.py`. Regenerate the snapshot.
   - Run `./ci.sh unit`. Expected: every test passes.

3. **Refactor.**
   - Find the imports of the deleted modules and remove them.
   - Check that each helper that remains in `src/chief/cli/commands.py` has at least one caller.
   - Record the smells found and the refactorings applied.

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| Corporate removal | `test_all_remaining_packs_resolve` | `test_install_still_refuses_mcp_config_paths` |
| Command surface | `test_cli_has_no_mcp_snippet_command` | `test_api_has_no_mcp_snippet_method` |

## Review gate

- Run `git grep -n -i "mcp" -- src tests`. Expected: only `src/chief/installation/planner.py` and the planner's refusal tests appear.
- Check that every pack named in `ALL_PACKS` exists in the bundle.
- Check that `SKILL.md` and the agent contain no link to a deleted file.

## Out of scope

- Packaging metadata. C4 owns it.
- Host handling and the pull request text. C6 owns them.
- Documentation. C8 owns it.

## Verification

```bash
# Run from the repository root.
./ci.sh unit
git grep -n -i "mcp" -- src tests
```

Expected: `./ci.sh unit` exits 0. The grep lists only the planner and its refusal tests.

## Refactor report

Smells found: none applied. Observed, not touched: `list_command` and `install_command` iterate a comprehension in the `for` header, which reads clearly. `targets()` and `_names(Target.ALL)` both compute `targets_for(Target.ALL)`, with different return types. `packs()` and `has_pack()` both read the bundle catalogue, and a fix belongs in `BundleTree`, outside this entity. `app.py` is 104 lines, over the ~100-line guideline; splitting it is beyond a removal chapter.

Each helper left in `commands.py` has a caller. The imports of the deleted modules went into the removal commit, because the package does not import without them.

Data-design gate: not applicable. The diff removes code and regenerates a path-only install snapshot, with no schema change.

Deleted, per D7: the MCP pack, the MCP package, and the corporate build-environment file with its references in the orchestration skill and the implementer agent. The planner's refusal rule for MCP configuration paths stays (I3). `README.md` and `CHANGELOG.md` still describe the removed command; C8 owns them.

## Git workflow

- Check out the loop branch: `git checkout feat/private-distribution`.
- Create the chapter branch: `git checkout -b feat/private-distribution-c03-corporate-code`.
- Commit the red test first, with the type `test`.
- Commit the removal with the type `refactor`. Use the subject `refactor: remove the MCP pack and the corporate build environment`.
- Run `./ci.sh all` before the hand-off.
- Do not push. The chief merges the chapter branch into the loop branch with `git merge --no-ff`.
