---
name: azure-translator
description: Azure Translator in Foundry Tools for text translation: key and region headers, API version, character limits and the Microsoft Learn docs server. Use when a task calls the Translator or asks how it works.
---

# Azure Translator

Use this skill when a task calls the Azure Translator text API or asks how it works. Name the service Azure Translator in Foundry Tools in new text.

## Agent tooling

- MCP: none verified
- Endpoint: none
- Auth: none for the Microsoft Learn docs server, which the vendor page describes as a public endpoint. The Translator API takes a key header. See Working rules.
- Scope: the Learn docs server provides three tools: `microsoft_docs_search`, `microsoft_docs_fetch` and `microsoft_code_sample_search`.
- Docs index: the Microsoft Learn MCP server at https://learn.microsoft.com/api/mcp. The Translator documentation root is https://learn.microsoft.com/en-us/azure/ai-services/translator/.
- Verified: 2026-11-26 https://learn.microsoft.com/en-us/azure/developer/azure-mcp-server/tools/
- Verified: 2026-11-26 https://learn.microsoft.com/en-us/training/support/mcp-developer-reference
- Verified: 2026-11-26 https://learn.microsoft.com/en-us/azure/ai-services/translator/

## When the server is missing

No Translator MCP server is verified, so there is no server to add. The Azure MCP Server tool reference lists no Translator tool. That reference may be stale, so check it again before you repeat the claim. A third-party connector listing is not a vendor source. Do not name one as official.

For API questions, use the Learn docs server in the Docs index. To add it, point the user to the `mcp-setup` skill. The agent never edits MCP configuration.

## Working rules

- Send the key in the `Ocp-Apim-Subscription-Key` header, as `${AZURE_TRANSLATOR_KEY}`. Add the `Ocp-Apim-Subscription-Region` header for a multi-service or regional resource. The region is optional for a global resource. Source: https://learn.microsoft.com/en-us/azure/ai-services/translator/text-translation/reference/authentication
- The global host is `https://api.cognitive.microsofttranslator.com`. A regional resource uses the same host with the region header. With virtual network support on, use the resource's custom endpoint, because the global host does not accept the request. Source: the same authentication page.
- Check the API version on the Learn page before each change. The text API examples use `api-version=3.0`. The what's-new page names text translation API 2026-06-06 as GA and the latest. Sources: https://learn.microsoft.com/en-us/azure/ai-services/translator/translator-text-apis and https://learn.microsoft.com/en-us/azure/ai-services/translator/whats-new
- Count characters before a batch call. Charges are per character, and each request has a character limit across all target languages. Check the current limits on https://learn.microsoft.com/en-us/azure/ai-services/translator/service-limits before you state them.
- A docs search query goes to Microsoft. Put no secret and no customer text in it.
- Never log a key. Keep it in the environment, and use `${...}` placeholders in files. The trust rules of the `mcp-setup` skill apply.
- The older product name Azure AI Translator is none verified on the pages read.
