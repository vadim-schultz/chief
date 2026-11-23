---
type: Design Rules
title: "Read and operations rules"
description: "Design rules DD21 to DD33 on freshness, failure, verification and lifecycle."
tags: [data, design, operations]
generated: { by: "human:vadim-schultz", at: "2026-11-19T00:00:00Z" }
---

# Read and operations rules: freshness, failure, verification, lifecycle

Rule IDs are stable. Cite them in findings. `DDIA2 p.N` is a page in the 2nd edition.

## Reads and freshness

### DD21 Write the staleness budget; keep it apart from integrity

- **Rule:** For every view, state how stale it may be in seconds, and which facts must never be wrong. Staleness is temporary. An integrity violation is permanent. Spend effort on integrity first.
- **Smell:** "Eventually consistent" with no number. A stale rollup used for a gate decision. Integrity guarded only by timing.
- **Fix:** A staleness budget per view, with `computed_at` queryable. A decision that carries integrity weight reads the system of record, not the rollup.
- **DDIA2 p.571-573.**

### DD22 Session guarantees for the writer

- **Rule:** After a write, the same user reads it (read-your-writes) and never sees state older than before (monotonic reads).
- **Smell:** A read from a secondary right after a write. A list refetch that overwrites a newer cache entry. A materialized view that shows the pre-write value with no hint.
- **Fix:** Read from the primary on own-write paths, or use a causal-consistency session with majority concerns. The client updates its cache from the write response. Drop any payload with a lower `version`. Show `pending` until a derived view catches up.
- **DDIA2 p.209-214.**

### DD23 Push is cache invalidation

- **Rule:** A push channel extends the write path to the client. The client cache is derived data. Push identity and version; refetch the body. After a disconnect, refetch what is on screen.
- **Smell:** Client state built by applying event bodies. A design that relies on replay. Polling and push both writing the same state.
- **Fix:** Invalidate query keys from `{collection, id, version}`. Refetch on reconnect. Ignore an event whose `version` is not newer than the cached one.
- **DDIA2 p.555-558, p.562.**

### DD24 Index the query you serve

- **Rule:** A compound index serves a left prefix: equality fields first, then sort, then range. Every sort and every range filter has an index. A wildcard index serves one field per predicate.
- **Smell:** A filter on `trace.a` and `trace.b` with a sort on `created_at`, backed only by a wildcard index. A sort that scans. Pagination with no stable tiebreaker.
- **Fix:** Declare the compound index on the registry entry. Sort on `(sort key, _id)`. Confirm with `explain`.
- **Cost:** Slower writes and more storage per index.
- **DDIA2 p.132-133, p.145.**

### DD25 Percentiles, and count the calls

- **Rule:** Measure response time as percentiles per route. Aggregate histograms, never percentiles. A request that makes N calls is as slow as its slowest call.
- **Smell:** Average latency on a dashboard. An N+1 fetch per row from the UI or the API. Sequential awaits that could be one query. A handler that waits on an external system.
- **Fix:** p50, p95, and p99 per route and per worker step. A call budget per request. Batch with `$in`. Move slow work into a command.
- **DDIA2 p.38-42.**

## Failure and overload

### DD26 Remote calls: timeout, bounded retry, one retry layer

- **Rule:** Every remote call has a timeout and a bounded retry with exponential backoff and jitter. Only one layer retries. A failing dependency gets a circuit breaker or load shedding.
- **Smell:** No timeout. Retries in the client, the API, and the worker at once. A retry of a non-idempotent call. A retry storm after an outage.
- **Fix:** A timeout shorter than the caller's. The retry budget lives in the worker. A breaker per provider. A failure recorded as a `failed` command with `detail`.
- **DDIA2 p.38-39, p.352-353.**

### DD27 External systems are mirrors

- **Rule:** An external system is the source of a derived mirror, not a participant in a request. Read through a sync command. Write through an outbox. Serve stale data with `synced_at`.
- **Smell:** A handler calls an issue tracker. A UI action waits for an external write. Our availability depends on theirs.
- **Fix:** Sync and publication commands. Upsert on `(provider, external_id)`. Provenance fields. A poller for reference data.
- **DDIA2 p.20, p.501-507.**

### DD28 Configuration changes are the usual outage

- **Rule:** Operator and configuration changes cause more outages than hardware faults. Make them versioned data with review, gradual rollout, and rollback.
- **Smell:** A configuration edit that applies everywhere at once with no previous version. A production data "fix" with no record.
- **Fix:** Configuration documents with `schema_version` and an `enabled` toggle, pinned by results (DD10). A rehearsed rollback. A blameless review after an incident.
- **DDIA2 p.47-48.**

### DD29 One node first

- **Rule:** Add a store, service, queue, or shard only when the stated numbers need it. Every extra system is another derived-data pipeline with its own failure modes. Plan one order of magnitude ahead, no more.
- **Smell:** A new datastore for one query. Sharding before measuring. Autoscaling for predictable load. A service split with no team boundary.
- **Fix:** Put the load numbers in the design note. Use one Mongo, one Redis, and one worker pool. Name the metric that would trigger the next step. See the parked list in [local-stack.md](local-stack.md).
- **DDIA2 p.19-22, p.52.**

## Verification and lifecycle

### DD30 Verify end to end; prove recovery

- **Rule:** Declare the integrity invariants and check them continuously across the whole pipeline. Derived data can be dropped and rebuilt. Backups restore. A delete reaches every copy.
- **Smell:** A rollup nobody recomputes. A backup that was never restored. A deleted document still present in blobs, rollups, or caches.
- **Fix:** Reconcile jobs: rollup equals recompute from source; every `produced` id exists; every outbox row is terminal within its SLA; mirror count equals provider count. A restore drill. A deletion checklist per copy.
- **DDIA2 p.512, p.575-577.**

### DD31 Observe the joins between components

- **Rule:** Failures hide in the gaps between components. Make queue age, consumer lag, rollup drift, event-to-refetch latency, and step duration observable. Carry one trace id from command to worker to event.
- **Smell:** A failure diagnosed by reading logs of three services. No metric for "derived data is behind".
- **Fix:** A lag metric from `computed_at`. An alert on queue age. A correlation id stamped on the command and carried into worker logs and events.
- **DDIA2 p.20-21, p.53.**

### DD32 Prefer reversible steps

- **Rule:** Irreversible changes raise the stakes of every release. Prefer steps you can back out: expand and contract, flags, dual reads before cutover, soft delete (`enabled: false`).
- **Smell:** A one-way migration. Dropping the old collection in the same release as the new one. No rollback plan.
- **Fix:** Name the rollback for every release that touches data. Keep the old path until the new path is verified.
- **DDIA2 p.55.**

### DD33 People are in the data

- **Rule:** Actor stamps (`created_by`, the Entra oid) and run telemetry are personal data. Collect them to account for changes. Set retention. Do not build per-person performance views.
- **Smell:** A dashboard that ranks engineers. Personal fields kept forever. Tracking added "in case it is useful".
- **Fix:** Data minimization. Record the purpose of each personal field. Give it a retention class.
- **DDIA2 p.24-25, p.596.**
