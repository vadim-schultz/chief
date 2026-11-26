---
name: supabase
description: Supabase work on Postgres, migrations, row-level security, API keys and the Supabase CLI, with the hosted Supabase MCP server. Use when a task names Supabase or a Supabase project.
---

# Supabase

Use this skill when a task touches a Supabase project: its Postgres database, its migrations, its row-level security, its API keys or the Supabase CLI.

## Agent tooling

- MCP: official
- Endpoint: https://mcp.supabase.com/mcp
- Auth: OAuth sign-in through the MCP client. The vendor page says no personal access token is needed. A CI job can pass a personal access token in an `Authorization` header instead.
- Scope: read-only first. Add `read_only=true` to the endpoint for investigation. Add `project_ref=${SUPABASE_PROJECT_REF}` to limit the server to one project.
- Docs index: https://supabase.com/docs/llms.txt. The full index is https://supabase.com/llms-full.txt.
- Verified: 2026-11-26 https://supabase.com/docs/guides/ai-tools/mcp
- Verified: 2026-11-26 https://supabase.com/docs/llms.txt

## When the server is missing

Say so. Point the user to the `mcp-setup` skill for the configuration layout. The agent never edits MCP configuration. Ask the user to add the server block, to set `SUPABASE_PROJECT_REF` in the environment and to sign in through the client.

## Local development

The Supabase CLI runs a local stack. Read the local MCP URL from the output of `supabase status` (https://supabase.com/docs/reference/cli/supabase-status), because the MCP page says the port can differ. The CLI reference names no local MCP URL, so the port and path are none verified.

## Working rules

- A client may hold the publishable key. The vendor page marks it "Safe to expose online: web page, mobile or desktop app, GitHub actions, CLIs, source code." Source: https://supabase.com/docs/guides/api/api-keys
- The secret key is the successor to the legacy `service_role` key. Never put it in a browser, a shipped application or source control. Keep it in the environment as `${SUPABASE_SECRET_KEY}`. Source: https://supabase.com/docs/guides/api/api-keys
- Enable row-level security on every table in an exposed schema. A table in an exposed schema without it is readable and writable by any role with a grant on it. Source: https://supabase.com/docs/guides/database/postgres/row-level-security
- Run migrations over a direct or session connection, not the transaction pooler. The connection page maps migrations to a direct connection, and the transaction pooler does not support prepared statements. Source: https://supabase.com/docs/guides/database/connecting-to-postgres
- Use read-only scope for investigation. Confirm each write through the MCP server with the user first.
- Never log or paste a key. The trust rules of the `mcp-setup` skill apply.
- This skill holds no prices and no plan limits. Check current limits on the vendor page before you state them.
