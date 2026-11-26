---
type: Reference
title: "MCP configuration layouts"
description: "Config file, top-level key and environment syntax for MCP servers in Cursor, Claude Code, OpenCode and VS Code."
---

# MCP configuration layouts

Each table gives, for one tool, the file that holds MCP servers, the top-level key that holds the servers, and the environment syntax that the file accepts. Each row cites the vendor page that holds the fact. A fact that no vendor page confirmed reads `none verified`.

Layouts change between releases. Read the cited page before you give the user a path. Never write a secret value into these files. Use an environment reference.

## Cursor

The vendor page gives the exact name of the Cursor folder. Read it there before you give the user a path.

| Scope | File | Key | Environment syntax | Source |
| --- | --- | --- | --- | --- |
| Project | `mcp.json` in the Cursor folder at the project root | `mcpServers` | `${env:NAME}` | https://cursor.com/docs/context/mcp |
| Global | `mcp.json` in the Cursor folder under the home directory | `mcpServers` | `${env:NAME}` | https://cursor.com/docs/context/mcp |

The vendor page states that hosted Cloud Agents do not read the global file.

Verified: 2026-11-26 https://cursor.com/docs/context/mcp

## Claude Code

| Scope | File | Key | Environment syntax | Source |
| --- | --- | --- | --- | --- |
| Project | `.mcp.json` at the project root | `mcpServers` | `${VAR}` or `${VAR:-default}` | https://code.claude.com/docs/en/mcp |
| User | `~/.claude.json` | none verified | `${VAR}` in a server value (see note) | https://code.claude.com/docs/en/mcp |

The vendor page allows the environment syntax in a server's `command`, `args`, `env`, `url` and `headers` values. In a remote server's `url` and `headers`, some credential variables read as empty, such as `ANTHROPIC_API_KEY`. The vendor page states this.

Verified: 2026-11-26 https://code.claude.com/docs/en/mcp

## OpenCode

| Scope | File | Key | Environment syntax | Source |
| --- | --- | --- | --- | --- |
| Global | `opencode.json` or `opencode.jsonc` in `~/.config/opencode` | `mcp`, with each server under `servers` | `{env:NAME}` | https://opencode.ai/docs/config/ |
| Project | `opencode.json` or `opencode.jsonc` at the project root, or in `.opencode` | `mcp`, with each server under `servers` | `{env:NAME}` | https://opencode.ai/docs/config/ |

The MCP page nests server names under `servers`, and it says that server names do not sit directly under `mcp` in the newer layout. The page gives no version number. Check the layout that the installed version reads.

Unset variables expand to an empty string. A shell form such as `$NAME` is not expanded inside a JSON string.

Verified: 2026-11-26 https://opencode.ai/docs/config/
Verified: 2026-11-26 https://opencode.ai/docs/mcp-servers/

## VS Code

Copilot reads more than one layout. The reference page names the layout for each harness. The vendor page says that new Copilot configurations use the native destinations, and that they do not use `.vscode/mcp.json` or a profile `mcp.json`.

| Scope | File | Key | Environment syntax | Source |
| --- | --- | --- | --- | --- |
| Workspace, recommended | `.mcp.json` at the workspace root. The guided setup offers it only when the experimental setting `chat.mcp.workspaceRootConfig.enabled` is on. | `mcpServers` | `${NAME}`. A bare `$NAME` is literal text. | https://code.visualstudio.com/docs/agents/reference/mcp-configuration |
| User | `mcp-config.json` in `$COPILOT_HOME`, or `~/.copilot/mcp-config.json` when `COPILOT_HOME` is unset | `mcpServers` | `${NAME}`, or `${NAME:-default}` for a non-secret default | https://code.visualstudio.com/docs/agents/reference/mcp-configuration |
| Editor-managed, deprecated for the Local harness | `.vscode/mcp.json` | `servers` | `${env:NAME}`. `${input:id}` prompts for a value and is not allowed in portable files. | https://code.visualstudio.com/docs/agents/reference/mcp-configuration |
| User profile | none verified. The page names a profile `mcp.json` and gives no path. | none verified | none verified | https://code.visualstudio.com/docs/agents/reference/mcp-configuration |

Verified: 2026-11-26 https://code.visualstudio.com/docs/agents/reference/mcp-configuration
Verified: 2026-11-26 https://code.visualstudio.com/docs/copilot/customization/mcp-servers
