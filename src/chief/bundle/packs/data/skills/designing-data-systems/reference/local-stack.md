---
type: Reference
title: "Local stack"
description: "What each component of the local stack guarantees, its settled constructs, known smells, parked machinery and proving tests."
tags: [data, stack, design]
generated: { by: "human:vadim-schultz", at: "2026-11-19T00:00:00Z" }
---

# Local stack: guarantees, settled constructs, parked machinery

This file turns the rules into this stack. Read it before a design or review on this stack.
Verify any claim about repository code in that repository before you assert it.

## What each component gives, and does not

| Component | Gives | Does not give | Rules |
| --- | --- | --- | --- |
| MongoDB (Motor) | Atomic single-document writes, embedded data included. Unique indexes. `find_one_and_update` as compare-and-set. Short multi-document transactions on a replica set. Majority concerns. Causal-consistency sessions. Change streams (replica set only). | A cross-document invariant without a unique index or a transaction. Fresh reads from a secondary. Order across collections. Multi-field predicates from one wildcard index. Instant TTL deletes. | DD11 DD12 DD13 DD22 DD24 |
| Redis pub/sub | Low-latency fanout to connected subscribers. | Persistence. Replay. Delivery to an offline subscriber. | DD17 DD23 |
| Worker loop | Claim, lease, heartbeat, retry. A Mongo claim with `claim_one` and `lease_until`, or a Redis queue such as SAQ. | Exactly-once execution. No overlap between an expired attempt and its reclaim. | DD14 DD15 DD18 DD20 |
| Litestar handler | One request with a client timeout. | Work that outlives the request. A safe place to call an external system. | DD25 DD26 DD27 |
| Pydantic model | Validation at the boundary. | Unknown-field preservation: the default `extra="ignore"` drops them on write-back. | DD7 DD8 |
| Blob store (GridFS, S3-compatible) | Immutable objects by key. | Atomicity with a Mongo document. | DD19 |
| WebSocket `/events` | Push of `ChangeEvent` while connected. | Events missed during a disconnect. | DD17 DD23 |
| React and TanStack Query | A local replica of server state. | Freshness. Order between responses. | DD22 DD23 |
| Container pod (managed platform) | Rolling updates, rescheduling, restart at maintenance. | One long-lived process. One code version at a time. Local disk state. | DD6 DD8 |
| External system (issue tracker) | Its API, its ids. | Our availability targets. Our latency. | DD26 DD27 |

Deployment limits, probes, and quotas belong to the platform. Do not repeat them here.

## Settled decisions: apply, do not re-argue

| Rules | Construct |
| --- | --- |
| DD1 DD2 | Three kinds only: stored, materialized, command. No read-time aggregation. No in-code registry or live queue served as a collection. Redis is never authoritative. |
| DD2 DD27 | `syncs` in, `publications` outbox out. CI fence: no outbound HTTP client reachable from a handler. |
| DD3 | Materialized collections fed by contributor `rollups`. Write amplification accepted. Coalescing and TTL are the named mitigations. |
| DD5 DD33 | `created_by` and `updated_by` stamped by the repository from the principal. `retention` is required on every registry entry. |
| DD6 DD8 DD9 | `schema_version` per collection, additive only inside a major. Committed contract snapshot, diffed and classified in CI. Generated client. |
| DD10 | `trace.configuration` plus `schema_version`. A configuration is disabled, never deleted. |
| DD12 | `version` plus `If-Match` on PATCH. A missing header returns 428. |
| DD13 | Natural-key upsert `(provider, external_id)`. Atomic `claim_one` through `find_one_and_update`. |
| DD14 | Publication idempotency key `(source_collection, source_id, payload_kind)`. |
| DD15 | Duplicate execution is tolerated, not prevented. Steps must be idempotent. No consensus service. |
| DD17 DD23 | One `ChangeEvent`, identity and `version` only. Best-effort fanout. Refetch on reconnect. No replay. |
| DD18 | Command collections: status lifecycle, `produced`, terminal states never left, retry is a new POST. |
| DD20 | `attempts`, exponential backoff, `failed` with `last_error`. The dead-letter view is `GET /publications?status=failed`. |
| DD24 | Generated wildcard index on `trace.$**`. Compound indexes declared on the registry entry. |
| DD28 | Configuration as versioned documents. |
| DD29 | One Mongo. No external queue, no log, no durable pub/sub. |
| DD30 | `reconciliations` command collection: recompute, report drift, optional repair. |

## Open seams: look here first

- **DD15 final writes.** Idempotent steps tolerate duplicate runs. Check that the
  final status transition and any non-idempotent effect are conditional on the lease, so a late run
  cannot overwrite newer state.
- **DD24 wildcard limit.** One wildcard index cannot serve a multi-key
  filter. Each hot multi-key filter needs its own declared compound index.
- **DD17 event loss.** Mongo change streams are the named escape hatch. Trigger: clients report stale views that a refetch fixes, more than rarely.
- **DD22 reads.** The design does not state a read preference. When reads can reach a secondary, ask
  how a user reads their own write.

## Common symptoms: first hypotheses

Test these first in a review of an existing system. Read its code before asserting any of them.

| Symptom | Rule | Direction |
| --- | --- | --- |
| A read endpoint reads a live queue, or an in-code registry. | DD1 | Mirror queue state into a stored collection. |
| A request handler blocks on a remote API. | DD27 DD25 | Sync command and mirror. Serve stale with `synced_at`. |
| Several channel factories and several progress payload models. | DD9 DD18 | One change envelope. Progress is a field on the command. |

## Parked machinery

Do not propose these. Propose one only when the trigger is met and the number is written down.

| Machinery | Why parked | Trigger to reconsider |
| --- | --- | --- |
| Log broker (Kafka-style) | Mongo is the record. Refetch recovers a missed event. | A consumer needs ordered replay that a refetch cannot give. |
| Distributed transactions (2PC, XA) | Cost and fragility. DD2, DD11, and DD14 replace them. | None. Do not span Mongo and another system. |
| Consensus or lock service | A unique index, compare-and-set, and idempotent steps cover it. | A real need for one leader among workers, after a Mongo lease with a fence fails. |
| Sharding | One replica set is enough at stated load. | Measured storage or write throughput at the limit. Choose the key from the access pattern. |
| Event sourcing as primary store | Documents with `trace` and `version` already give audit (DD5). | A routine need to rebuild state by replaying full history. |
| Durable-execution engine | Command steps (DD18) are readable and queryable. | A step graph with loops and branches that command steps cannot keep clear. |
| Multi-leader or local-first sync | No offline editing requirement. | A requirement for offline editing. |
| Columnar or OLAP store | Materialized collections serve the matrix. | The p99 of a materialized query breaches its target at stated load. |

## Proving tests

Pair each with the project TDD rule: one happy path, one negative path.

| Rule | Happy path | Negative path |
| --- | --- | --- |
| DD7 | PATCH one field. A field the model does not know stays on the document. | A whole-document replace is rejected or absent from the code path. |
| DD12 | Two PATCH calls with the same `If-Match` race. One succeeds. | The other gets 412. The document holds exactly one change. |
| DD13 | Two concurrent creates of one invariant. One document exists. | The second is rejected with a duplicate-key error. |
| DD14 | The same POST twice with one key. One document, same id returned. | The same key with a different payload is rejected. |
| DD15 | A step run twice gives the same result. | A late run after a reclaim cannot overwrite the newer status. |
| DD19 | A killed run leaves no partial output readable as final. | A rerun after the kill gives the same rows, no duplicates. |
| DD23 | An event with a newer `version` triggers a refetch. | An event with an older or equal `version` is ignored. |
| DD26 | A provider timeout ends as a `failed` command with `detail`. | No handler imports an HTTP client (repo fence). |
| DD30 | Reconcile reports zero drift on clean data. | Tamper with one derived row. Reconcile reports it. |

## Handoffs

- New endpoint or route: review it against the API rules before it is written. The route table is derived from the registry.
- New collection: a change that needs more than a registry entry, a model, and a field-map deviation has found a core gap: stop and report it.
- One chapter per context. A finding outside the chapter's scope is `observed`, not applied.
