---
name: Chapter C2e - Stack web pack
overview: "Create the stack-web pack with the chakra-ui and vite-react skills. Chakra UI has an official MCP package and llms.txt files. The Vite and React facts are recorded with their verification status."
id: C2e
depends_on: ["C2a"]
touches: ["src/chief/bundle/packs/stack-web/**", "tests/test_stack_web_pack.py", "tests/fixtures/install_snapshot.json"]
execution: chapter-implementer
isProject: false
---

# C2e - Stack web pack

**Depends on:** C2a · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [../01-rollout.md](../01-rollout.md)

## Goal

After this chapter, the `stack-web` pack exists with two service skills for the React and Vite frontend. Chakra UI gets its verified MCP package and llms files. Vite and the React libraries get working rules and the docs index that was verified, with the rest marked as unverified.

## Read first

- [00-architecture.md](../00-architecture.md): section Skill contract; invariants I3 to I5.
- [gaps-and-decisions.md](../gaps-and-decisions.md): decisions D6, D7 and D8.
- [02-stack-docs.md](02-stack-docs.md): the contract checker and the identifier scan. Reuse them.

## Coordination scope

**Add:**

- `tests/test_stack_web_pack.py`
- `src/chief/bundle/packs/stack-web/pack.toml`
- `src/chief/bundle/packs/stack-web/skills/chakra-ui/SKILL.md`
- `src/chief/bundle/packs/stack-web/skills/vite-react/SKILL.md`

**Edit:**

- `tests/fixtures/install_snapshot.json`: regenerate it after the loop merge, as decision D13 says. Do not edit it by hand.

**Do not edit:**

- `tests/test_stack_knowledge.py`, owned by C2a.
- Every other pack under `src/chief/bundle/packs/`.

## Work items

1. **Red, happy path.** In `tests/test_stack_web_pack.py`, add `test_stack_web_pack_declares_expected_skills`: both skill names exist, and `pack.toml` requires `stack-docs`. Confirm it fails because the pack is missing.

2. **Red, negative path.** In the same file, add:
   - `test_stack_web_pack_names_no_project_identifier`: the identifier scan finds no hit.
   - `test_stack_web_skills_pass_contract`: the C2a checker finds no violation.
   - `test_vite_rules_warn_about_public_env_vars`: the `vite-react` skill states that a `VITE_` variable is public in the browser bundle, and that a secret never takes that prefix.

   Confirm each fails before the pack exists.

3. **Green.** Write the pack. Facts for each skill:

   - **chakra-ui.**
     - `MCP: official`. The official package is `@chakra-ui/react-mcp`. Start it with `npx -y @chakra-ui/react-mcp`. Source of truth: https://chakra-ui.com/docs/get-started/ai/mcp-server
     - Pro component templates need an API key. The tools `list_component_templates` and `get_component_templates` need it. Record that the key is the user's, and that no key goes into the skill.
     - Docs index: `https://www.chakra-ui.com/llms.txt`, the full v3 file at `llms-full.txt`, and a separate v2-to-v3 migration file. The exact migration file name differs between sources. Confirm it on the AI docs page, and record the name you confirmed in the commit body, before you cite it.
     - Working rules: Chakra UI v3 APIs differ from v2. Most models were trained on v2 code, so check the migration file before you write component code. Use the theme tokens, not hard-coded colours.

   - **vite-react.**
     - MCP: `none verified` for Vite, React, React Router, TanStack Query and supabase-js.
     - Docs index: `https://vite.dev/llms.txt` is reported by the Vite maintainers. Confirm it before you cite it, and mark it `verified` only after you read it. React's documentation index is not confirmed. Mark it `none verified`.
     - Context7 is an optional docs source for the libraries without an index (D8).
     - Working rules:
       - A `VITE_` variable is public. The browser bundle contains it. Never put a secret under that prefix.
       - Configure Vite in `vite.config.ts`. Keep test configuration with Vitest, using the jsdom environment.
       - Use the ESLint flat configuration and TypeScript strict mode.
       - Check the current React 19 and React Router 7 API before you change a route.
       - Keep server state in TanStack Query, with query keys in one module.

4. **Refactor (see Refactor report).**

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| Pack declares its skills | `test_stack_web_pack_declares_expected_skills` | the same test fails on a planted copy with one skill removed |
| Identifier scan | `test_stack_web_skills_pass_contract` | `test_stack_web_pack_names_no_project_identifier` |
| Public env var warning | `test_stack_web_skills_pass_contract` | `test_vite_rules_warn_about_public_env_vars` |

## Review gate

- The Chakra UI MCP package name matches the vendor page.
- The llms URLs are the ones the vendor page shows, each with a `Verified:` date.
- The `vite-react` skill states `none verified` for every library without a confirmed index.
- The identifier scan finds no hit in the pack.
- `./ci.sh all` exits 0 on the chapter branch.

## Out of scope

- The project's own frontend architecture and its size limits. Those stay in the project.
- Python libraries. Owned by C2d.

## Verification

```bash
# Run from the repository root.
uv run pytest tests/test_stack_web_pack.py tests/test_stack_knowledge.py -q
./ci.sh all
```

Expected: both commands exit 0.

## Refactor report

Smells found -> refactorings applied (chapter branch, commit 4fd4f62):
- Duplicated code: the pack-folder guard was repeated in three tests. Applied: the `stack_web` fixture.
- Speculative generality: `_skill_text` took a pack-folder parameter that was always `STACK_WEB`. Applied: the parameter was removed.
- Lint only: the `tomllib` import is version-guarded for Python 3.10.

The narrow suite stayed green after each step. The shared-wording refactor is dropped under D14.

Observed, not changed: `_skill_text` repeats the private helper in `tests/test_stack_knowledge.py`, which C2a owns. Trigger: a third pack-level caller.

Audit scope, for the implementer: the docs-lookup pointer and the secrets rule appear once each. The two skills link to them.

## Git workflow

- Check out the loop branch with `git checkout feat/stack-knowledge`. C2a must already be merged into it.
- Create the chapter branch with `git checkout -b feat/stack-knowledge-c2e-stack-web-pack`.
- Commit the red tests first, then the green change.
- Run the local gate on the chapter branch. It passes when it exits 0.
- Do not push, and do not open a pull request. Remote CI runs once, on the release pull request.
- The chief merges the chapter branch into the loop branch locally, with `git merge --no-ff`.
