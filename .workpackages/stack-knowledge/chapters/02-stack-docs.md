---
name: Chapter C2a - Stack docs pack
overview: "Create the stack-docs pack with the mcp-setup and docs-lookup skills, add the skill contract checker and the identifier scan, and let the pack tests find every stack-* pack on disk."
id: C2a
depends_on: []
touches: ["src/chief/bundle/packs/stack-docs/**", "tests/test_stack_knowledge.py", "tests/test_packs.py", "tests/fixtures/install_snapshot.json"]
execution: chapter-implementer
isProject: false
---

# C2a - Stack docs pack

**Depends on:** none · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [../01-rollout.md](../01-rollout.md)

## Goal

After this chapter, the `stack-docs` pack exists. Its two skills tell the agent where each tool keeps MCP configuration and how to look up current documentation. A test module holds the skill contract checker, the identifier scan and the pack tests. The later stack chapters use that checker unchanged.

## Read first

- [00-architecture.md](../00-architecture.md): sections Skill contract, MCP guidance, and Leak and identifier rules; invariants I1 to I5.
- [gaps-and-decisions.md](../gaps-and-decisions.md): decisions D1, D6, D7 and D8; open question O7.
- [01-rollout.md](../01-rollout.md): section Per-chapter gate.

## Coordination scope

**Add:**

- `src/chief/bundle/packs/stack-docs/pack.toml`
- `src/chief/bundle/packs/stack-docs/skills/mcp-setup/SKILL.md`
- `src/chief/bundle/packs/stack-docs/skills/mcp-setup/reference/config-layouts.md`
- `src/chief/bundle/packs/stack-docs/skills/docs-lookup/SKILL.md`
- `tests/test_stack_knowledge.py`

**Edit:**

- `tests/fixtures/install_snapshot.json`: regenerate it after the loop merge, as decision D13 says. Do not edit it by hand.
- `tests/test_packs.py`: replace the fixed `ALL_PACKS` set with `CORE_PACKS` plus every `stack-*` pack found on disk.

**Do not edit:**

- Every other pack under `src/chief/bundle/packs/`.
- `src/chief/targets/**` and the install code. Owned by C1.
- Hand edits to `tests/fixtures/install_snapshot.json`. Regenerate it instead (D13).

## Work items

1. **Red, happy path.** Write `tests/test_stack_knowledge.py` with the contract checker as small named predicates, one per contract line in the architecture. Add these tests:
   - `test_stack_skill_declares_agent_tooling`: a conforming sample passes the checker.
   - `test_stack_docs_pack_loads_and_renders_for_every_target`: `BundleTree` renders `skills/mcp-setup/SKILL.md` and `skills/docs-lookup/SKILL.md` for `cursor`, `claude`, `opencode` and `vscode`. Use an isolated root.

   Run the file. Confirm the failures show the missing pack, not an import error. The checker module exists, so the import works. Only the pack is missing.

2. **Red, negative path.** Add these tests, each with a planted sample:
   - `test_checker_rejects_skill_without_verified_line`
   - `test_checker_rejects_http_endpoint`: a plain `http://` URL fails.
   - `test_checker_rejects_literal_secret_in_snippet`: a token-shaped value fails the identifier scan. Reuse `TOKEN_PREFIXES` from `tests/test_bundle_contract.py`. Build the value from pieces so that this file does not match itself.
   - `test_checker_rejects_description_over_300_chars`
   - `test_checker_rejects_skill_over_100_lines`
   - `test_identifier_scan_rejects_supabase_project_host`: a `<ref>.supabase.co` host fails.
   - `test_identifier_scan_accepts_placeholders`: `<account_id>` and `${ENV_VAR}` pass.
   - `test_identifier_scan_rejects_sibling_project_name`: a line that names the sibling project fails. The name matches in any case, with an optional hyphen or underscore. Build the pattern from parts, as in chapter C0 (decision D9).

3. **Red, pack tests.** Change `tests/test_packs.py` so that `CORE_PACKS` holds the six existing packs. Add a test that every `stack-*` pack on disk resolves inside the bundle. Confirm the test fails before `pack.toml` exists, or before the `stack-*` discovery works.

4. **Green.** Make the smallest change that passes each red test:
   - Write `pack.toml`: `name = "stack-docs"`, a one-line description, `requires = []`.
   - Write `mcp-setup/SKILL.md` (under 100 lines). It covers when to use it, the layout table in `reference/config-layouts.md`, how to add a server (the user does it), how to check that a server connects (list its tools), and the trust rules: review third-party servers, prefer OAuth, read-only scope first, one project at a time.
   - Write `reference/config-layouts.md`. One section for each target: Cursor, Claude Code, OpenCode, VS Code. Each section names the file, the key and the environment syntax. Cite the vendor page for each row. If a row rests on a blog only, write `none verified` for that row. See O5 for Supabase and the rule that unverified URLs are not written.
   - Write `docs-lookup/SKILL.md` (under 100 lines). Source order: vendor index (`llms.txt`), vendor docs, vendor MCP server, a third-party docs server (Context7 is the example, and it is optional, D8), then a web search. Each fact cites its URL and its date. Queries to a third party carry no secrets and no customer data.
   - Write the `description` of each skill as 300 characters or fewer. The `mcp-setup` description names the trigger: a missing server, or a request to connect one.

5. **Refactor (see Refactor report).**

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| Agent tooling contract | `test_stack_skill_declares_agent_tooling` | `test_checker_rejects_skill_without_verified_line` |
| Endpoint rule | `test_stack_skill_declares_agent_tooling` | `test_checker_rejects_http_endpoint` |
| Secret rule | `test_identifier_scan_accepts_placeholders` | `test_checker_rejects_literal_secret_in_snippet` |
| Description length | `test_stack_skill_declares_agent_tooling` | `test_checker_rejects_description_over_300_chars` |
| Skill length | `test_stack_skill_declares_agent_tooling` | `test_checker_rejects_skill_over_100_lines` |
| Project identifiers | `test_identifier_scan_accepts_placeholders` | `test_identifier_scan_rejects_supabase_project_host`; `test_identifier_scan_rejects_sibling_project_name` |
| Pack renders | `test_stack_docs_pack_loads_and_renders_for_every_target` | `test_packs.py`: a missing `requires` target still raises (existing test) |

## Review gate

- The checker holds one predicate per contract line, and each predicate has a test that plants a failing sample.
- `mcp-setup` and `docs-lookup` do not carry an `Agent tooling` section. They are guidance skills. The contract applies to the service skills of the other packs.
- Every fact in `config-layouts.md` has a vendor URL, or is marked `none verified`.
- The identifier scan runs over the whole `stack-docs` folder.
- `./ci.sh all` exits 0 on the chapter branch.

## Out of scope

- Service skills for any product. Owned by C2b to C2e.
- The `vscode` target itself. Owned by C1. This chapter documents the `vscode` configuration layout only.
- The README. Owned by C4.

## Verification

```bash
# Run from the repository root.
uv run pytest tests/test_stack_knowledge.py tests/test_packs.py -q
./ci.sh all
```

Expected: both commands exit 0. The new tests are listed as passed.

## Refactor report

Smells found -> refactorings applied (chapter branch, commit aae4eb1):
- Duplicated code, two label readers: extracted `_bullet_body`.
- Duplicated code, planted violations written twice (in the table and in the named tests): one `VIOLATIONS` table now feeds both.
- Duplicated work: `BundleTree` was rebuilt for each target. It is now built once.
- Mysterious name `long`: removed by the `VIOLATIONS` change.

The narrow suite stayed green after each step.

Observed, not changed (follow-ups):
- `_frontmatter` repeats the fence parser of `tests/test_bundle_contract.py`. Trigger: a third caller.
- `tests/test_stack_knowledge.py` is about 350 lines and holds three concerns. Split it in C3, if C2b to C2e import the checker.

Audit scope, for the implementer:

- The checker in `tests/test_stack_knowledge.py`. Each predicate must do one thing. Count the branches in the function that runs them.
- `tests/test_packs.py`: the pack set construction.

## Git workflow

- Check out the loop branch with `git checkout feat/stack-knowledge`.
- Create the chapter branch with `git checkout -b feat/stack-knowledge-c2a-stack-docs-pack`.
- Commit the red tests first, then the green change.
- Run the local gate on the chapter branch. It passes when it exits 0.
- Do not push, and do not open a pull request. Remote CI runs once, on the release pull request.
- The chief merges the chapter branch into the loop branch locally, with `git merge --no-ff`.
