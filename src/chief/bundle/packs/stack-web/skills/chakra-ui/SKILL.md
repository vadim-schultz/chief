---
name: chakra-ui
description: Guides Chakra UI v3 component, theme and migration work. Use when a request names Chakra UI, a Chakra component, a theme token or a v2-to-v3 migration. Check the v3 migration file before you write component code.
---

# Chakra UI

Use this skill for Chakra UI v3 work. Chakra UI v3 APIs differ from v2. Confirm each API on the v3 docs before you write component code.

## Agent tooling

- MCP: official
- Endpoint: `npx -y @chakra-ui/react-mcp`
- Auth: none stated for six tools. The two Pro template tools need an active Chakra UI Pro license and the `CHAKRA_PRO_API_KEY` environment variable, set by the user.
- Scope: read-first. The vendor page lists eight tools and does not say which of them write. Allow the lookup tools first.
- Docs index: https://chakra-ui.com/llms.txt. The full v3 file is https://chakra-ui.com/llms-full.txt. The v2-to-v3 migration file is https://chakra-ui.com/llms-v3-migration.txt.
- Verified: 2026-11-26 https://chakra-ui.com/docs/get-started/ai/mcp-server
- Verified: 2026-11-26 https://chakra-ui.com/docs/get-started/ai/llms
- Verified: 2026-11-26 https://chakra-ui.com/llms.txt
- Verified: 2026-11-26 https://chakra-ui.com/llms-v3-migration.txt

## When the server is missing

If the `chakra-ui` server is not in the tool list, use the `mcp-setup` skill. Tell the user which file to edit and which environment variable to set. Do not edit MCP configuration yourself.

## Working rules

- Read the v3 migration file before you write component code. It covers the v2-to-v3 codemod, the manual setup steps and the renamed components and props. Source: https://chakra-ui.com/llms-v3-migration.txt, read 2026-11-26.
- Older examples can show v2 code. Do not copy a v2 pattern into a v3 project.
- The MCP server lists a migration review tool, `v2_to_v3_code_review`. Source: https://chakra-ui.com/docs/get-started/ai/mcp-server, read 2026-11-26.
- Use theme tokens, not hard-coded colors. The theming page says to use the `strictTokens` config property to enforce the usage of only design tokens. Source: https://chakra-ui.com/docs/theming/overview, read 2026-11-26.
- The Pro template tools need a Chakra UI Pro license. The user supplies the key. Read it from `${CHAKRA_PRO_API_KEY}` in the environment. Source: https://chakra-ui.com/docs/get-started/ai/mcp-server, read 2026-11-26.
- Check current limits and tool lists on the vendor page before you state them.
- For any other fact that may have changed, use the `docs-lookup` skill.
- Never write a key or token into a skill, a config file or chat. Use `${ENV_VAR}` placeholders.
