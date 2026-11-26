# Workers AI

Workers AI runs models on Cloudflare. Its model catalogue changes over time.

## OpenAI-compatible API

- The vendor page says: "Workers AI provides OpenAI-compatible endpoints for text generation through Chat Completions".
- Base URL pattern, from the vendor SDK example: `https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/ai/v1`.
- Point the standard OpenAI SDK at that base URL. The vendor page says: "Easily call Workers AI by swapping the `baseURL` in the standard OpenAI SDK."

## Model IDs

- Model IDs change. The changelog announces model deprecations with their dates.
- The vendor page for the model catalogue says that an unavailable model should be replaced: "Choose an available model from the catalog below."
- Working rule: choose the model from the current catalogue, and check its ID before each use. Do not copy a model ID from memory.

Source: https://developers.cloudflare.com/workers-ai/configuration/open-ai-compatibility/, https://developers.cloudflare.com/workers-ai/changelog/ and https://developers.cloudflare.com/workers-ai/models/

Verified: 2026-11-26 https://developers.cloudflare.com/workers-ai/configuration/open-ai-compatibility/
Verified: 2026-11-26 https://developers.cloudflare.com/workers-ai/changelog/
Verified: 2026-11-26 https://developers.cloudflare.com/workers-ai/models/
