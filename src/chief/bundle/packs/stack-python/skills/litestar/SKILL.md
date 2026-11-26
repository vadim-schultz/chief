---
name: litestar
description: Working rules for Litestar, the Python ASGI framework: route handlers, Pydantic request bodies, dependency injection and tests. Use when a request names Litestar or changes a Litestar route, handler or provider.
---

# Litestar

Litestar is an ASGI framework for Python. Use these rules when you write or review a Litestar application. For the current version and API names, follow the docs-lookup skill in the stack-docs pack.

## Agent tooling

- MCP: none verified
- Endpoint: none
- Auth: none. The framework has no hosted server.
- Scope: read-only first. Read the project code before you change a handler.
- Docs index: none verified. The vendor site is https://litestar.dev
- Verified: 2026-11-26 https://litestar.dev
- Verified: 2026-11-26 https://docs.litestar.dev/latest/usage/dependency-injection.html
- Verified: 2026-11-26 https://docs.litestar.dev/latest/usage/testing.html

## When the server is missing

Litestar has no documentation MCP server that a vendor page confirms. Read the vendor pages with the docs-lookup skill.

- Litestar MCP (`litestar-mcp`) is a third-party plugin. Its page, https://litestar.dev/plugins/litestar-mcp, says it exposes route handlers as MCP tools. It is not a documentation source. Add it only when the project wants MCP endpoints, and follow the mcp-setup skill to do so.

The agent never edits MCP configuration.

## Working rules

- Describe request and response bodies with Pydantic models. Let the model validate the input.
- Provide each database session through dependency injection. A callable that a handler depends on is wrapped in a `Provide` object. See https://docs.litestar.dev/latest/usage/dependency-injection.html
- Keep route handlers thin. Move the logic into service functions that take the session as an argument, and test those functions directly.
- Test handlers with the test client. The test client is built on httpx and calls the ASGI app without a running server. See https://docs.litestar.dev/latest/usage/testing.html
- Check the current version and its limits on the vendor site before you state them.
