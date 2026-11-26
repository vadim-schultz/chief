---
name: vite-react
description: Guides Vite build setup, VITE_ environment variables, React 19 routes with React Router 7, TanStack Query and Vitest tests. Use when a request names Vite, React, a route, a VITE_ variable or frontend tests. Confirm the current API first.
---

# Vite and React

Use this skill for the frontend build, routes, server state and tests. No MCP server is verified for these libraries. Check the vendor pages before you rely on an API.

## Agent tooling

- MCP: none verified
- Endpoint: none
- Auth: none
- Scope: none, because no server is verified
- Docs index: https://vite.dev/llms.txt for Vite. None verified for React, React Router, TanStack Query or supabase-js.
- Verified: 2026-11-26 https://vite.dev/llms.txt
- Verified: 2026-11-26 https://vite.dev/guide/env-and-mode
- Verified: 2026-11-26 https://vite.dev/config/
- Verified: 2026-11-26 https://vitest.dev/config/environment
- Verified: 2026-11-26 https://eslint.org/docs/latest/use/configure/configuration-files
- Verified: 2026-11-26 https://www.typescriptlang.org/tsconfig/strict.html
- Verified: 2026-11-26 https://tanstack.com/query/latest/docs/framework/react/guides/query-keys

## When the server is missing

No server is verified for these libraries, so there is none to add. If the user asks for an MCP server for one of them, use the `mcp-setup` skill to explain the layout. Do not invent a server name.

## Working rules

- A `VITE_` variable is public. Vite exposes it in the browser bundle, after bundling. Source: https://vite.dev/guide/env-and-mode, read 2026-11-26.
- Never put a secret under the `VITE_` prefix. The same page says `VITE_*` variables should not contain sensitive information such as API keys.
- Configure Vite in `vite.config.ts`. Vite supports TypeScript config files. Source: https://vite.dev/config/, read 2026-11-26.
- Keep test configuration in Vitest, with the `jsdom` environment for browser-like tests. The default environment is `node`. Source: https://vitest.dev/config/environment, read 2026-11-26.
- Use the ESLint flat configuration file, `eslint.config.js`, which is the default file name. Source: https://eslint.org/docs/latest/use/configure/configuration-files, read 2026-11-26.
- Use TypeScript strict mode. Setting `strict` to `true` turns on the strict mode family of checks. Source: https://www.typescriptlang.org/tsconfig/strict.html, read 2026-11-26.
- Check the React 19 and React Router 7 API for the version the project pins before you change a route. No docs index is verified for React or React Router. Write `none verified` for each fact that no vendor page confirms.
- Keep server state in TanStack Query. A query key must be an array at the top level, and item order matters. Keep all query keys in one module. Source: https://tanstack.com/query/latest/docs/framework/react/guides/query-keys, read 2026-11-26.
- Check current limits and versions on the vendor page before you state them.
- For a library with no docs index, use the `docs-lookup` skill. It names Context7 as an optional third-party source. The user decides whether to use it.
- Never write a key or token into a skill, a config file or chat. Use `${ENV_VAR}` placeholders.
