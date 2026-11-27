---
type: Reference
title: "Workers and static assets"
description: "Static assets served by Workers, and the run_worker_first option."
---

# Workers and static assets

Static assets are files that a Worker project serves without running Worker code.

## Serve static assets

- Wrangler uploads the files of the assets directory during deployment. The vendor page says: "During deployment, Wrangler automatically uploads the files from this directory to Cloudflare's infrastructure."
- By default, a request that matches a file in the assets directory gets that file. No Worker code runs.

## Set the assets directory

Set the directory in the Wrangler configuration file. In `wrangler.jsonc`:

```jsonc
{
  "assets": {
    "directory": "./dist/",
    "run_worker_first": true
  }
}
```

## Use run_worker_first

- `true` runs the Worker script for every request, before any asset is served.
- An array of route patterns runs the Worker script first only for the matching paths. The vendor example uses `["/api/*", "!/api/docs/*"]`.

Source: https://developers.cloudflare.com/workers/static-assets/

Verified: 2026-11-26 https://developers.cloudflare.com/workers/static-assets/
