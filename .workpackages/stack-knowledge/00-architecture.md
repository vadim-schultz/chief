---
name: Stack knowledge and VS Code target - architecture
overview: "Purpose, invariants and design decisions for the stack knowledge packs, the MCP guidance skill and the vscode install target."
isProject: false
---

# Stack knowledge and VS Code target - architecture

This work package adds stack knowledge packs and a `vscode` install target to chief.

## Purpose

Chief installs skills, agents and rules from packs into the folders of each tool.
This work package adds five things:

1. Five new packs of service skills: `stack-docs`, `stack-cloud`, `stack-data-services`, `stack-python` and `stack-web`.
2. In each service skill, an `Agent tooling` section. It names the MCP server or documentation index the agent must use for that service, and it records when each fact was verified.
3. A shared `mcp-setup` skill. It shows where each supported tool keeps its MCP configuration. The user adds the configuration. Chief does not write it.
4. A `vscode` install target that writes skills and agents under `~/.copilot`.
5. Tests that enforce the skill contract, the identifier rules and the target list.

The source of the stack is the sibling project. The service list, with the MCP and docs findings for each item, is in [inventory.md](inventory.md).

**Out of scope:**

- The installer writing MCP configuration. This is decision D1 in [gaps-and-decisions.md](gaps-and-decisions.md). It is a separate work package if the user wants it.
- Any change to the sibling project.
- Skills for the public-data sources (GovData, PVOG, LeiKa, FIM, OpenPLZ). The sibling project keeps its own skills for them.
- Skills for Flutter and Firebase. Neither is built yet.
- Per-pack install selection. Every pack installs into every target.
- Any release tag other than `v0.2.0`. See decision D10.

## Invariants

| ID | Invariant | Enforced by |
| --- | --- | --- |
| I1 | The installer never writes MCP configuration files. | `tests/test_install.py::test_mcp_config_files_are_never_touched`, `tests/test_api.py::test_install_still_refuses_mcp_config_paths`, and the planner refusal test `test_planner_refuses_mcp_config_targets`. C1 extends the refusal to `mcp-config.json`. |
| I2 | The README never uses the term "MCP". | `tests/test_readme.py::test_readme_has_no_mcp_or_package_index`. |
| I3 | Stack skills hold no account identifiers, project references, hostnames of a user project, keys or tokens. Configuration examples use `${ENV_VAR}` placeholders. | The identifier scan in `tests/test_stack_knowledge.py`, added in C2a, and the leak gate `tests/test_no_leaks.py`. |
| I4 | Every stack skill has an `Agent tooling` section with the required lines. Every `Verified:` line holds a source URL and a date. | The contract checker in `tests/test_stack_knowledge.py`, added in C2a. |
| I5 | Every stack skill description is 300 characters or fewer. Every stack skill is 100 lines or fewer. Depth goes into `reference/` files. | The contract checker. |
| I6 | The `vscode` target writes only under `~/.copilot`. | `tests/test_install.py` with the isolated `HOME` fixture. |
| I7 | Every chapter passes `./ci.sh all` on its chapter branch and on the loop branch. | The per-chapter gate in [01-rollout.md](01-rollout.md). |
| I8 | Chapters do not push, and no chapter opens a pull request. | The git workflow of every chapter file, and [git-model.md](/home/porco/.claude/skills/chief-of-staff/git-model.md). |
| I9 | No file under `src/chief/`, and no stack pack, names the sibling project. This folder names it nowhere either. | `tests/test_sibling_name.py` (chapter C0), the identifier scan in `tests/test_stack_knowledge.py` (chapter C2a), and the cross-pack test (chapter C3). Each test builds the name from parts. |

## Design

### Pack layout

| Pack | Skills | Requires |
| --- | --- | --- |
| `stack-docs` | `mcp-setup`, `docs-lookup` | none |
| `stack-cloud` | `cloudflare`, `render`, `github-actions`, `uptimerobot` | `stack-docs` |
| `stack-data-services` | `supabase`, `azure-translator` | `stack-docs` |
| `stack-python` | `litestar`, `sqlalchemy-alembic`, `pydantic` | `stack-docs` |
| `stack-web` | `chakra-ui`, `vite-react` | `stack-docs` |

Each pack holds one or more skills. Each skill is one folder with `SKILL.md`, and optionally `reference/*.md`.

### Skill contract

Every service skill has this shape:

- Frontmatter with `name` and `description`. The description is 300 characters or fewer, and it names the trigger words.
- A section `## Agent tooling`. It has these lines:
  - `MCP: official`, `MCP: community` or `MCP: none verified`.
  - `Endpoint:` one or more HTTPS URLs or install commands, or `none`.
  - `Auth:`.
  - `Scope:`. Read-only scope comes first.
  - `Docs index:`. A vendor `llms.txt`, a vendor docs URL, or `none verified`.
  - `Verified: YYYY-MM-DD <source URL>`.
- A section `## When the server is missing`. It says so, and it points to the `mcp-setup` skill. The agent never edits MCP configuration by itself.
- A section `## Working rules`. It lists the rules that matter for that service. It holds no prices and no limits that change over time. It says to check current limits on the vendor page.

### MCP guidance

The `mcp-setup` skill holds the configuration layout for each supported tool:

| Tool | Configuration file | Key | Environment syntax |
| --- | --- | --- | --- |
| Cursor | `~/.cursor/mcp.json`, or `.cursor/mcp.json` in a project | `mcpServers` | `${env:NAME}` |
| Claude Code | `.mcp.json` in a project | `mcpServers` | `${NAME}` |
| OpenCode | `opencode.json` or `opencode.jsonc`, under `~/.config/opencode` or in a project | `mcp` | `{env:NAME}` |
| VS Code | `.vscode/mcp.json`, or the profile `mcp.json` | `servers` | `${env:NAME}` |

The table holds the facts from the research. C2a checks each row against the vendor page and records the source in the skill.

### `vscode` target

- The target name is `vscode`. It joins `CONCRETE_TARGETS`, so `--target all` installs into four targets.
- The config root is `~/.copilot`.
- Skills go to `skills/<name>/SKILL.md`.
- Agents go to `agents/<name>.agent.md`.
- Rules are written only when the official docs confirm a personal instructions location. Otherwise the target does not support rules, and the plan output lists each skipped rule. See D3.
- The `claude` target does not change. Claude Code in VS Code keeps reading `~/.claude`.

### Leak and identifier rules

The new packs and this work package folder are scanned by the leak gate. The gate exempts only `.workpackages/private-distribution/`. The text in this folder must not contain:

- Hostnames, project references or account identifiers of any real project.
- The sibling project's name (I9).
- Private package-index hosts.
- Keys, tokens or secret-key prefixes.

Skills describe services in general terms. Real values go in the user's environment, never in a file.

## Decided

Each decision has a reason in [gaps-and-decisions.md](gaps-and-decisions.md). The design sections above follow from these:

- MCP guidance lives in skills. The installer never writes MCP configuration (D1).
- `vscode` installs under `~/.copilot` (D2).
- Rules for `vscode` depend on verified official facts (D3).

## Open

Each open question has a default. The default applies unless the user answers. See [gaps-and-decisions.md](gaps-and-decisions.md) for the full table.
