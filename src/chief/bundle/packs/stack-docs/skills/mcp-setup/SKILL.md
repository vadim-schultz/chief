---
name: mcp-setup
description: Shows where Cursor, Claude Code, OpenCode and VS Code keep MCP server configuration. Use when a service's MCP server is missing or the user asks to connect one. The user edits the configuration; the agent does not.
---

# MCP setup

Use this skill when a service skill names an MCP server that the tool does not list, or when the user asks to connect a server.

The agent never edits MCP configuration. Tell the user which file to change, which key to add, and which environment variable to set.

## Find the layout

Open the [configuration layouts](reference/config-layouts.md). Each section gives the file, the top-level key and the environment syntax for one tool. Every row cites its vendor page. Read that page before you give the user a path, because layouts change between releases.

## Add a server

1. Give the user the server block for the file that the layout names.
2. Use the environment syntax of that layout, such as `${env:NAME}`, for every key and account value. No value goes into the file.
3. Ask the user to set each environment variable in their shell or secret store.
4. Ask the user to save the file.

## Check that the server connects

Ask the tool to list the tools of that server. If none appear, check in this order: the file path, the top-level key, the server name, and the environment variable.

## Trust rules

- Review a third-party server before the user adds it. Check its publisher and its source.
- Prefer OAuth over a static key when the server offers it.
- Start with read-only scope. Add write scope only for a task that needs it.
- Connect one project at a time. Prefer a project file over a global file.
- Never paste a key into chat or into a shared file. The VS Code MCP page gives the same rule: https://code.visualstudio.com/docs/copilot/customization/mcp-servers
