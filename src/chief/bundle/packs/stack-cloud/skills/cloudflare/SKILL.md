---
name: cloudflare
description: Cloudflare for the stack - Workers and static assets, R2 object storage, Workers AI and Browser Run. Use when a task names Cloudflare, Wrangler, Workers, R2, Workers AI or Browser Run, or needs a Cloudflare MCP server.
---

# Cloudflare

Use this skill for Workers and static assets, R2, Workers AI and Browser Run. Each product has a reference file. Read the reference before you act on it.

## Agent tooling

- MCP: official
- Endpoint: https://mcp.cloudflare.com/mcp (Cloudflare API server); https://browser.mcp.cloudflare.com/mcp (Browser Run server)
- Auth: OAuth, through a sign-in to Cloudflare. For automation, a token sent as a bearer token in the Authorization header.
- Scope: read-only first. Add write permissions only for a task that needs them.
- Docs index: https://developers.cloudflare.com/llms.txt (site index; each product links its own llms.txt)
- Verified: 2026-11-26 https://developers.cloudflare.com/agents/model-context-protocol/cloudflare/servers-for-cloudflare/
- Verified: 2026-11-26 https://developers.cloudflare.com/llms.txt
- Verified: 2026-11-26 https://github.com/cloudflare/mcp-server-cloudflare

## When the server is missing

Say so. Point the user to the mcp-setup skill. The user adds the server. Do not edit MCP configuration.

## Reference files

- [Workers and Pages](reference/workers-and-pages.md): static assets and the `run_worker_first` option.
- [R2](reference/r2.md): the S3 endpoint, the region and token scope.
- [Workers AI](reference/workers-ai.md): the OpenAI-compatible API and model IDs.
- [Browser Run](reference/browser-run.md): REST endpoints for page content, Markdown, snapshot and screenshot.

## Working rules

- Check the plan limits on the vendor pricing page before a change depends on them: https://developers.cloudflare.com/workers/platform/pricing/
- Deploy Workers from `wrangler.jsonc` with the Wrangler CLI (`wrangler deploy`). Do not deploy by hand. Source: https://developers.cloudflare.com/workers/wrangler/configuration/
- Never print a token. Read it from the environment, for example `${CLOUDFLARE_API_TOKEN}`.
- The header that selects the account for a token with several accounts: none verified. Check the vendor page before you add one.
- Do not use the `/sse` endpoint. The repository says it is retired and answers `410 Gone` with a pointer to `/mcp`.
- The Browser Run server's tool list may change. Read the tool list from the server at runtime.
