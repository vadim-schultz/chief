---
name: Chapter C2b - Stack cloud pack
overview: "Create the stack-cloud pack with cloudflare, render, github-actions and uptimerobot skills, each with its Agent tooling facts and its vendor sources."
id: C2b
depends_on: ["C2a"]
touches: ["src/chief/bundle/packs/stack-cloud/**", "tests/test_stack_cloud_pack.py"]
execution: chapter-implementer
isProject: false
---

# C2b - Stack cloud pack

**Depends on:** C2a · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [../01-rollout.md](../01-rollout.md)

## Goal

After this chapter, the `stack-cloud` pack exists with four service skills. Each skill tells the agent which MCP server or docs index to use for that service, what is verified, and what to check before it acts. The skills hold no account identifiers, hostnames of user projects, keys or tokens.

## Read first

- [00-architecture.md](../00-architecture.md): section Skill contract; invariants I3 to I5.
- [gaps-and-decisions.md](../gaps-and-decisions.md): decisions D6 and D7; open question O6.
- [02-stack-docs.md](02-stack-docs.md): the contract checker and the identifier scan. Reuse them. Do not copy them.

## Coordination scope

**Add:**

- `tests/test_stack_cloud_pack.py`
- `src/chief/bundle/packs/stack-cloud/pack.toml`
- `src/chief/bundle/packs/stack-cloud/skills/cloudflare/SKILL.md`, with `reference/workers-and-pages.md`, `reference/r2.md`, `reference/workers-ai.md` and `reference/browser-run.md`
- `src/chief/bundle/packs/stack-cloud/skills/render/SKILL.md`
- `src/chief/bundle/packs/stack-cloud/skills/github-actions/SKILL.md`
- `src/chief/bundle/packs/stack-cloud/skills/uptimerobot/SKILL.md`

**Edit:** None.

**Do not edit:**

- `tests/test_stack_knowledge.py`. It belongs to C2a. If the checker lacks a rule for this pack, stop and report to the chief of staff.
- Every other pack under `src/chief/bundle/packs/`.

## Work items

1. **Red, happy path.** Add `tests/test_stack_cloud_pack.py` with `test_stack_cloud_pack_declares_expected_skills`. It asserts that the four skill names exist in the pack and that `pack.toml` requires `stack-docs`. Run it. Confirm it fails because the pack is missing.

2. **Red, negative path.** In the same file, add:
   - `test_stack_cloud_pack_names_no_project_identifier`: scans every file of the pack with the identifier scan from C2a. It must find no hit.
   - `test_stack_cloud_skills_pass_contract`: runs the C2a checker on each skill of the pack. It must find no violation.

   Confirm both fail before the pack exists.

3. **Green.** Write the pack, one skill at a time. Each skill has a red check in the same file: its `Agent tooling` lines are present, and its `Verified:` line has a source URL and a date. Facts for each skill:

   - **cloudflare.**
     - `MCP: official`. The Cloudflare API server covers more than 2,500 endpoints, including DNS, Workers, R2, Zero Trust and developer documentation. Check the exact endpoint on the vendor page: https://developers.cloudflare.com/agents/model-context-protocol/cloudflare/servers-for-cloudflare/
     - The Browser Run server. The vendor lists it with the endpoint `https://browser.mcp.cloudflare.com/mcp`. The project README lists two tools: `get_url_html_content` and `get_url_markdown`. It says more tools are planned. Mark the tool list as subject to change (O6).
     - Auth: Cloudflare OAuth. For a token with several accounts, pass `account_id` or the `cf-account-id` header. The old `/sse` endpoint is retired.
     - Docs index: the site index `https://developers.cloudflare.com/llms.txt`, with a per-product index for each product. Record the URL that you verify.
     - Workers AI: an OpenAI-compatible API. Model IDs change, and the changelog deprecates models. Working rule: choose the model from the current catalogue and check its ID before each use. Do not copy a model ID from memory.
     - R2: an S3-compatible endpoint of the form `https://<account_id>.r2.cloudflarestorage.com` with region `auto`. Working rule: scope each token to one bucket and one permission.
     - Working rules: check current free-plan limits on the pricing page; never print a token; deploy Workers from `wrangler.jsonc` or the Wrangler CLI, not by hand.
     - Reference files: `workers-and-pages.md` (static assets and `run_worker_first`), `r2.md`, `workers-ai.md`, `browser-run.md` (REST endpoints `content`, `snapshot` and `screenshot` under the account API path, with `<account_id>` as a placeholder).

   - **render.**
     - `MCP: official`. Hosted endpoint `https://mcp.render.com/mcp`. Source: `render-oss/render-mcp-server`, which runs as a local binary or in Docker. Docs: https://render.com/docs/mcp-server
     - Auth: a browser sign-in on first use, or an API key for non-interactive use. Working rule: an API key can reach every workspace and service of the account. Prefer the browser sign-in.
     - Limits: some update actions return a link to the dashboard instead of doing the update.
     - Working rules: free web services sleep when idle, so a keep-alive pinger is needed (see `uptimerobot`). Read the plan's limits before you add a hook or a background job. Set secrets in the dashboard, not in a committed blueprint.

   - **github-actions.**
     - `MCP: official`. The GitHub MCP server, hosted at the Copilot endpoint. The Actions tools sit in the `actions` toolset, which is opt-in. The `/x/actions` path limits the server to Actions tools, and a `/readonly` suffix limits it to reads. Source: https://github.com/github/github-mcp-server
     - Tools named in the README: `actions_get`, `actions_list` and `get_job_logs`. Sources disagree on the count and on `actions_run_trigger`. Record only the names that the vendor README shows on the day of the check.
     - Working rules: cancel superseded runs with a concurrency group; treat scheduled runs as best-effort; never echo secrets in a step; keep workflow changes behind a `workflow_dispatch` trigger first.

   - **uptimerobot.**
     - `MCP: official`. Hosted endpoint `https://mcp.uptimerobot.com/mcp` over streamable HTTP. Docs: https://uptimerobot.com/mcp/
     - Auth: browser OAuth by default. Clients without OAuth use an API key sent as a Bearer token.
     - Creating or updating monitors needs the Main API key. MCP calls share the rate limit of the REST API.
     - Working rules: a keep-alive monitor is an HTTP check of the health path. Use the narrowest key the plan offers. Never write a key into a committed file.

4. **Refactor (see Refactor report).**

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| Pack declares its skills | `test_stack_cloud_pack_declares_expected_skills` | a missing skill fails the same test on a planted copy |
| Identifier scan | `test_stack_cloud_skills_pass_contract` | `test_stack_cloud_pack_names_no_project_identifier` |
| Contract | `test_stack_cloud_skills_pass_contract` | the checker rejects a skill without `Verified:` (C2a test) |

## Review gate

- Each skill cites a vendor URL for each `MCP:` and `Docs index:` fact, or it says `none verified`.
- No `Verified:` line is older than the chapter's verification date. Record that date in the commit body.
- The identifier scan finds no hit in the pack.
- `./ci.sh all` exits 0 on the chapter branch.

## Out of scope

- Data services (Supabase, Azure Translator). Owned by C2c.
- The shared MCP layout. Owned by C2a.
- Any change to the sibling project.

## Verification

```bash
# Run from the repository root.
uv run pytest tests/test_stack_cloud_pack.py tests/test_stack_knowledge.py -q
./ci.sh all
```

Expected: both commands exit 0.

## Refactor report

_Pending. The implementer fills this in during the refactor pass. Name the containing entity, the arms of each decision, and the outcome._

Audit scope, for the implementer: the four skills are text, so the refactor pass checks shared wording. Any sentence that repeats in two or more skills moves to `mcp-setup`, and the skills link to it.

## Git workflow

- Check out the loop branch with `git checkout feat/stack-knowledge`. C2a must already be merged into it. Do not start this chapter before that.
- Create the chapter branch with `git checkout -b feat/stack-knowledge-c2b-stack-cloud-pack`.
- Commit the red tests first, then the green change.
- Run the local gate on the chapter branch. It passes when it exits 0.
- Do not push, and do not open a pull request. Remote CI runs once, on the release pull request.
- The chief merges the chapter branch into the loop branch locally, with `git merge --no-ff`.
