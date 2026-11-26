---
name: Chapter C2c - Stack data services pack
overview: "Create the stack-data-services pack with the supabase and azure-translator skills, and record the vendor sources for their Agent tooling facts, including the open URL questions."
id: C2c
depends_on: ["C2a"]
touches: ["src/chief/bundle/packs/stack-data-services/**", "tests/test_stack_data_services_pack.py", "tests/fixtures/install_snapshot.json"]
execution: chapter-implementer
isProject: false
---

# C2c - Stack data services pack

**Depends on:** C2a · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [../01-rollout.md](../01-rollout.md)

## Goal

After this chapter, the `stack-data-services` pack exists with two service skills. Each skill names its MCP server or docs index and its verified facts. Where the research could not confirm a URL, the skill says so and does not guess.

## Read first

- [00-architecture.md](../00-architecture.md): section Skill contract; invariants I3 to I5.
- [gaps-and-decisions.md](../gaps-and-decisions.md): decisions D6 and D7; open questions O5 and O7.
- [02-stack-docs.md](02-stack-docs.md): the contract checker and the identifier scan. Reuse them.

## Coordination scope

**Add:**

- `tests/test_stack_data_services_pack.py`
- `src/chief/bundle/packs/stack-data-services/pack.toml`
- `src/chief/bundle/packs/stack-data-services/skills/supabase/SKILL.md`
- `src/chief/bundle/packs/stack-data-services/skills/azure-translator/SKILL.md`

**Edit:**

- `tests/fixtures/install_snapshot.json`: regenerate it after the loop merge, as decision D13 says. Do not edit it by hand.

**Do not edit:**

- `tests/test_stack_knowledge.py`, owned by C2a.
- Every other pack under `src/chief/bundle/packs/`.

## Work items

1. **Red, happy path.** In `tests/test_stack_data_services_pack.py`, add `test_stack_data_services_pack_declares_expected_skills`: both skill names exist, and `pack.toml` requires `stack-docs`. Confirm it fails because the pack is missing.

2. **Red, negative path.** In the same file, add:
   - `test_stack_data_services_pack_names_no_project_identifier`: the identifier scan finds no hit in the pack.
   - `test_stack_data_services_skills_pass_contract`: the C2a checker finds no violation.
   - `test_azure_translator_names_no_unverified_server`: the `azure-translator` skill states `MCP: none verified`. It does not name a third-party listing as an official server.

   Confirm each fails before the pack exists.

3. **Green.** Write the pack. Facts for each skill:

   - **supabase.**
     - `MCP: official`. Vendor page: https://supabase.com/docs/guides/ai-tools/mcp. Source: `supabase/mcp`.
     - The hosted endpoint is on the vendor page. Do not write a URL that you did not read there (O5).
     - Scope: URL parameters limit the server to one project and can make it read-only. Use read-only scope for investigation.
     - Auth: sign-in through the MCP menu of the client, with dynamic client registration.
     - Local development: the Supabase CLI exposes an MCP endpoint on localhost. Confirm the port and path in the CLI reference before you write them down.
     - Docs index: a `llms.txt` file exists. Record only the URL that the vendor page shows (O5). Guide pages also have `.md` copies.
     - Working rules: the publishable key is safe in a client. The secret key replaces the service role key, and it never goes into a browser bundle or a committed file. Keep row-level security on every exposed table. Run migrations over the session connection, not the transaction pooler. Confirm each MCP write with the user.

   - **azure-translator.**
     - `MCP: none verified`. The Azure MCP Server does not list Translator in its tool reference. That reference may be stale. A third-party connector listing is not a vendor source, so do not cite it.
     - Docs index: the Microsoft Learn MCP server, endpoint `https://learn.microsoft.com/api/mcp`. Tools: `microsoft_docs_search`, `microsoft_docs_fetch` and `microsoft_code_sample_search`. No sign-in is needed. Confirm the endpoint on the Microsoft Learn MCP developer reference before you write it (O7).
     - Name: the service is now called Azure Translator in Foundry Tools. Older docs say Azure AI Translator.
     - Auth: a key header with the resource region. The global endpoint is `https://api.cognitive.microsofttranslator.com`. Regional resources need their own endpoint and region.
     - Working rules: a search query goes to Microsoft. Send no secrets and no customer text in a query. Check the current API version on the Learn page before each change. Count characters before a batch call. Never log a key.

4. **Refactor (see Refactor report).**

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| Pack declares its skills | `test_stack_data_services_pack_declares_expected_skills` | the same test fails on a planted copy with one skill removed |
| Identifier scan | `test_stack_data_services_skills_pass_contract` | `test_stack_data_services_pack_names_no_project_identifier` |
| Unverified server | `test_stack_data_services_skills_pass_contract` | `test_azure_translator_names_no_unverified_server` |

## Review gate

- Each `Endpoint:` line matches a URL that the vendor page shows. A URL that the research did not confirm is absent or marked `none verified`.
- O5 and O7 are answered in the commit body, with the page each answer came from.
- The identifier scan finds no hit in the pack.
- `./ci.sh all` exits 0 on the chapter branch.

## Out of scope

- Cloud services. Owned by C2b.
- Changing the sibling project, including its secrets and its Supabase settings.

## Verification

```bash
# Run from the repository root.
uv run --group test pytest tests/test_stack_data_services_pack.py tests/test_stack_knowledge.py -q
./ci.sh all
```

Expected: both commands exit 0.

## Refactor report

Smells found -> refactorings applied (chapter branch, commits 089e4b3 and 3d40503):
- Test module, Duplicated Code: the skill path was built in two helpers. Applied: `_skill_file`.
- Test module, Mysterious Name: `_missing_skills` returned problem lines, not names. Applied: it returns names, and `_pack_problems` formats them.
- Test module, Duplicated Code: two negative tests copied the pack the same way. Applied: `_planted_pack`.
- Skill text, Divergent Change: the Supabase local-development note sat under "When the server is missing". Applied: its own "## Local development" section.
- The shared key-line wording was applied in 3d40503 and reverted under D14 in 685608f. The Translator key rule keeps its own plain-text wording.

The narrow suite stayed green after each step.

Observed, not changed: the `_assert_pack_exists()` guard is repeated in five tests. It reads clearly.

Audit scope, for the implementer: shared wording moves to `mcp-setup`. Two skills with the same security sentence share one reference line, not two copies.

## Git workflow

- Check out the loop branch with `git checkout feat/stack-knowledge`. C2a must already be merged into it.
- Create the chapter branch with `git checkout -b feat/stack-knowledge-c2c-stack-data-services-pack`.
- Commit the red tests first, then the green change.
- Run the local gate on the chapter branch. It passes when it exits 0.
- Do not push, and do not open a pull request. Remote CI runs once, on the release pull request.
- The chief merges the chapter branch into the loop branch locally, with `git merge --no-ff`.
