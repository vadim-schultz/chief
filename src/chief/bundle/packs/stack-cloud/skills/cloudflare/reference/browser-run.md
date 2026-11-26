# Browser Run

Browser Run runs stateless browser tasks, such as screenshots, Markdown extraction and page snapshots. The vendor page describes them as: "Simple, stateless browser tasks like screenshots, PDFs, and scraping."

## REST endpoints

Each task is a POST request to the account API. Replace `<account_id>` with the account ID from the environment.

| Task | Path |
| --- | --- |
| Page HTML | `https://api.cloudflare.com/client/v4/accounts/<account_id>/browser-run/content` |
| Page Markdown | `https://api.cloudflare.com/client/v4/accounts/<account_id>/browser-run/markdown` |
| Snapshot | `https://api.cloudflare.com/client/v4/accounts/<account_id>/browser-run/snapshot` |
| Screenshot | `https://api.cloudflare.com/client/v4/accounts/<account_id>/browser-run/screenshot` |

The vendor examples send each request with `curl -X POST`.

## MCP server

- Endpoint: https://browser.mcp.cloudflare.com/mcp. The vendor page describes it as: "Fetch web pages, convert them to markdown and take screenshots."
- Tool names: none verified on the vendor page. The tool list may change, so read it from the server at runtime.

Source: https://developers.cloudflare.com/browser-run/

Verified: 2026-11-26 https://developers.cloudflare.com/browser-run/
Verified: 2026-11-26 https://developers.cloudflare.com/browser-run/quick-actions/content-endpoint/
Verified: 2026-11-26 https://developers.cloudflare.com/browser-run/quick-actions/markdown-endpoint/
Verified: 2026-11-26 https://developers.cloudflare.com/browser-run/quick-actions/snapshot/
Verified: 2026-11-26 https://developers.cloudflare.com/browser-run/quick-actions/screenshot-endpoint/
