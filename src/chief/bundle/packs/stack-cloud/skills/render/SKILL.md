---
name: render
description: Render hosting for the stack - web services, the free plan's idle spin-down, deploy checks and the Render MCP server. Use when a task names Render, a Render service or blueprint, a spin-down, or the Render MCP server.
---

# Render

Use this skill for Render services, deploys and plan limits. Read the vendor pages before you change a service.

## Agent tooling

- MCP: official
- Endpoint: https://mcp.render.com/mcp
- Auth: OAuth, through a browser sign-in on first use. An API key is for non-interactive environments.
- Scope: read-only first. OAuth grants access to the user's workspaces and services. An API key reaches only the workspace and permissions that the key grants.
- Docs index: https://render.com/docs/mcp-server (vendor docs page; no llms.txt verified)
- Verified: 2026-11-26 https://render.com/docs/mcp-server
- Verified: 2026-11-26 https://render.com/docs/free
- Verified: 2026-11-26 https://github.com/render-oss/render-mcp-server

## When the server is missing

Say so. Point the user to the mcp-setup skill. The user adds the server. Do not edit MCP configuration.

## Working rules

- The MCP server makes limited changes to existing resources. For other modifications or deletions, the vendor page says to use the Render Dashboard. The server does not change scaling settings or other operational service controls.
- The open-source server, `render-oss/render-mcp-server`, supports the stdio and Streamable HTTP transports.
- A free web service spins down after 15 minutes without inbound traffic, and it takes about one minute to spin back up. HTTP requests and WebSocket messages count as traffic, so a keep-alive check of the health path prevents the spin-down. See the uptimerobot skill.
- Read the plan's limits before you add a hook or a background job. The free plan's terms are on the vendor page: https://render.com/docs/free
- Set secrets in the Render Dashboard, not in a committed blueprint.
- Never write an API key into a committed file. Use `${RENDER_API_KEY}`.
