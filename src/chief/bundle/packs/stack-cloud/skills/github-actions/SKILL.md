---
name: github-actions
description: GitHub Actions for the stack - scheduled and manual workflows, workflow runs and job logs through the GitHub MCP server. Use when a task names a workflow, a workflow run, a job log, a scheduled run or GitHub Actions.
---

# GitHub Actions

Use this skill for workflow runs, job logs and workflow changes. Read the workflow file before you change it.

## Agent tooling

- MCP: official
- Endpoint: https://api.githubcopilot.com/mcp/
- Auth: OAuth, or a GitHub personal access token (PAT).
- Scope: read-only first. Enable the Actions toolset only for a task that needs it. Read-only mode skips write tools.
- Docs index: https://docs.github.com/en/actions (vendor docs page; no llms.txt verified)
- Verified: 2026-11-26 https://github.com/github/github-mcp-server
- Verified: 2026-11-26 https://docs.github.com/en/actions

## When the server is missing

Say so. Point the user to the mcp-setup skill. The user adds the server. Do not edit MCP configuration.

## Actions tools

- The vendor README, read on 2026-11-26, names these Actions tools: `actions_get`, `actions_list`, `actions_run_trigger` and `get_job_logs`. Read the server's tool list at runtime, because the names can change.
- The README's default toolsets do not include Actions. Enable it on purpose.
- Path forms that limit the server to Actions tools or to reads: none verified.

## Working rules

- Use a concurrency group, so that a new run cancels the run it supersedes.
- Treat scheduled runs as best-effort.
- Pass a secret through an environment variable. Never print a secret in a step.
- Put a workflow change behind a `workflow_dispatch` trigger first. Add the schedule after the manual run passes.
