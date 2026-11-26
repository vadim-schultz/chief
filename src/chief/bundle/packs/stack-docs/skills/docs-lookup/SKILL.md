---
name: docs-lookup
description: Finds current vendor documentation before an answer depends on it. Use when a version, limit, flag, endpoint or API may have changed. Each fact cites its URL and the date the page was read.
---

# Docs lookup

Use this skill before you state a fact that may have changed: a version, a limit, a flag, an endpoint or an API signature.

## Source order

1. The vendor documentation index, `llms.txt`, when the vendor publishes one. Example: https://code.claude.com/docs/llms.txt. The format is defined at https://llmstxt.org/.
2. The vendor documentation pages that the service skill names.
3. The vendor MCP server that the service skill names in its Agent tooling section, when that section names one.
4. Optional: Context7, a third-party documentation server: https://github.com/upstash/context7. The user decides whether to use it. Chief never installs it.
5. A web search. A search snippet is a lead, not a source. Open the page before you cite it.

## Rules

- Cite each fact with its URL and the date you read the page.
- If no vendor page confirms a fact, write `none verified`. Do not state the fact.
- Do not write a URL that you have not read. A link that a vendor page gives you counts as read only after you open it.
- Name the version that a fact applies to. Prefer the version the project pins.
- A query to a third party carries no secret and no customer data.
- Check each date. A fact older than the project's last check needs a new check.
