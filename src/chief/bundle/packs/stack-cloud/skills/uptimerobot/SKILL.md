---
name: uptimerobot
description: UptimeRobot monitors for the stack, used as an external HTTP check that keeps a free Render service awake. Use when a task names UptimeRobot, a keep-alive monitor, a monitor interval or the UptimeRobot MCP server.
---

# UptimeRobot

Use this skill for keep-alive and uptime monitors. A monitor checks a health path from outside the service.

## Agent tooling

- MCP: official
- Endpoint: https://mcp.uptimerobot.com/mcp
- Auth: browser sign-in, which asks the user to approve read-only or full access. A client that cannot open a browser sign-in sends an API key as a Bearer token.
- Scope: read-only first. Creating or updating monitors needs the Main API key.
- Docs index: https://uptimerobot.com/mcp/ (vendor page; no llms.txt verified)
- Verified: 2026-11-26 https://uptimerobot.com/mcp/

## When the server is missing

Say so. Point the user to the mcp-setup skill. The user adds the server. Do not edit MCP configuration.

## Working rules

- A keep-alive monitor is an HTTP check of the service's health path. Read the plan's limits and the interval rules on the vendor page before you set an interval.
- Use the narrowest key that the plan offers.
- Never write a key into a committed file. Use `${UPTIMEROBOT_API_KEY}`.
- Whether MCP calls share the rate limit of the REST API: none verified. Check the vendor page before you run a bulk change.
