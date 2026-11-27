---
name: Stack knowledge and VS Code target - inventory
overview: "The technology and service inventory of the sibling project, with the MCP server or agent documentation found for each item, and the skill that covers it."
isProject: false
---

# Stack knowledge and VS Code target - inventory

This file is the source list for the stack packs. Each row names one technology or service that the sibling project uses. It records whether a vendor publishes an MCP server or an agent documentation index, and which skill covers it.

**Evidence:** the project's manifests (`pyproject.toml`, `package.json`), `render.yaml`, `wrangler.jsonc`, `docker-compose.yml`, the GitHub Actions workflows and the operations docs.

**Status words:**

- `official`: the vendor publishes it, and the vendor page was found.
- `community`: a third party publishes it.
- `none verified`: the research did not find a vendor source. The chapter that owns the row must check it again.

The research was done with web search snippets. Each chapter that uses a row verifies it on the vendor page before it writes the `Verified:` line.

## Cloud and platform services

| Service | Role in the project | MCP server | Agent docs | Skill |
| --- | --- | --- | --- | --- |
| Cloudflare Workers and static assets | Serves the single-page web app | official: Cloudflare API server (more than 2,500 endpoints) and product servers | per-product `llms.txt` under developers.cloudflare.com | `cloudflare` |
| Cloudflare R2 | Object store, used through the S3 API | covered by the Cloudflare API server (R2 tools not confirmed) | Cloudflare index | `cloudflare` |
| Cloudflare Workers AI | Model inference: extraction, embeddings, translation fallback | none verified | model catalogue and changelog; model IDs change often | `cloudflare` |
| Cloudflare Browser Run | Page fetch, snapshot and screenshot over REST | official: Browser Run server (tools `get_url_html_content`, `get_url_markdown`; work in progress) | Browser Run documentation | `cloudflare` |
| Render | Hosts the API web service on the free plan | official: hosted server; open-source `render-oss/render-mcp-server` | render.com/docs/mcp-server | `render` |
| Supabase | Postgres, authentication and the JavaScript client | official: Supabase MCP server (`supabase/mcp`) | `llms.txt` (URL to confirm) | `supabase` |
| Azure Translator (formerly Azure AI Translator) | Default translation engine, with a character ledger | none verified. The Azure MCP Server does not list it. | Microsoft Learn MCP server (`microsoft_docs_search`, `microsoft_docs_fetch`, `microsoft_code_sample_search`) | `azure-translator` |
| GitHub Actions | Scheduled and manual workflows | official: GitHub MCP server, Actions toolset (opt-in) | docs.github.com | `github-actions` |
| UptimeRobot | External pinger that keeps the free Render service awake (in use) | official: hosted server `mcp.uptimerobot.com/mcp` | uptimerobot.com/mcp | `uptimerobot` |

## Python backend

| Technology | Role | MCP server | Agent docs | Skill |
| --- | --- | --- | --- | --- |
| Litestar | API framework | none as a docs source. The community `litestar-mcp` plugin exposes routes as MCP tools. | none verified | `litestar` |
| SQLAlchemy, Alembic, psycopg, pgvector | ORM, migrations, driver, vector type | none verified | none verified | `sqlalchemy-alembic` |
| Pydantic, pydantic-settings | Input and output models, settings | none official | official LLM index, short and full forms | `pydantic` |
| PyJWT, boto3, uvicorn, httpx, selectolax, typer, prometheus-client | Libraries | none official | none | none |
| pytest, ruff, mypy, moto, uv | Tooling | not checked | not applicable | none |

## Web frontend

| Technology | Role | MCP server | Agent docs | Skill |
| --- | --- | --- | --- | --- |
| Chakra UI 3 | Component library | official: `@chakra-ui/react-mcp` | official `llms.txt`, `llms-full.txt` and a v2-to-v3 migration file | `chakra-ui` |
| Vite 7 | Build tool | none verified | `vite.dev/llms.txt`, reported by the maintainers (confirm) | `vite-react` |
| React 19, React Router 7, TanStack Query 5, supabase-js | Application libraries | none verified | none verified | `vite-react` |
| Vitest, ESLint, Prettier, TypeScript, Testing Library | Tooling | not checked | not applicable | none |

## Data sources of the project domain

GovData (CKAN), OpenPLZ, PVOG, LeiKa and the FIM portal.

- MCP: only community servers exist (for example `govdata-mcp`, `openplz-mcp` and the generic `ckan-mcp-server`). None was found for PVOG, LeiKa or FIM.
- Skill: none. The project keeps its own skills for these sources (decision D4).

## Planned, not built

- Flutter: official Dart and Flutter MCP server (`dart mcp-server`). No skill yet (D5).
- Firebase Cloud Messaging: official Firebase MCP server (`firebase-tools mcp`). No skill yet (D5).
- Alternatives named in the project's planning notes: Neon, Fly.io, Railway, Upstash, Netlify and Vercel. No skill.

## Not checked or inconclusive

- cron-job.org: no official server. A feature request exists, and community servers do. It is not used, so it gets no skill.
- Docker MCP catalogue entries and a PostgreSQL MCP server for the local database: not confirmed.
- Prometheus: community servers only. The API exports metrics, but no skill covers it.

## Docs fallback (all skills)

Context7 is a third-party docs server (`@upstash/context7-mcp`). It covers libraries that publish no `llms.txt`. The `docs-lookup` skill names it as optional (decision D8). Chief never installs it.
