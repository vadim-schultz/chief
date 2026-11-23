---
type: Design Rules
title: "Data rules"
description: "Design rules DD1 to DD10 on truth, derivation, models and evolution of data."
tags: [data, design]
generated: { by: "human:vadim-schultz", at: "2026-11-19T00:00:00Z" }
---

# Data rules: truth, derivation, models, evolution

Rule IDs are stable. Cite them in findings. `DDIA2 p.N` is a page in the 2nd edition.
Each rule has a smell (what to look for) and a fix (what to propose).

## Truth and derivation

### DD1 One owner per fact

- **Rule:** Every fact has one system of record. Everything else is derived data and can be rebuilt from it.
- **Smell:** Two writers for one fact. A cache, queue, search index, in-code registry, or live proxy served as the record. A derived value with no rebuild path.
- **Fix:** Name the owner. Stamp derived values with `computed_at` or `synced_at`. Add a rebuild or reconcile job. Mirror external systems (DD27).
- **DDIA2 p.10, p.540.**

### DD2 Derive after commit; never dual-write

- **Rule:** The record write and a durable intent to derive commit together, in one document or one transaction. A worker derives the rest. A handler never writes to two systems.
- **Smell:** A handler writes Mongo, then Redis, search, an issue tracker, or a cache. A crash between two awaits loses the second write. Two clients that interleave leave two systems permanently different, with no error raised.
- **Fix:** Put a status document or outbox row in the same Mongo write. A worker consumes it. Derivation is idempotent (DD14). Publishing happens after commit, inside the repository.
- **Cost:** One extra document per write. Derived data lags.
- **DDIA2 p.501-503, p.507.**

### DD3 Set the read/write boundary with numbers

- **Rule:** Materializing moves work from reads to writes. Decide from the read-to-write ratio, the fan-out factor, and the staleness budget. Cap the fan-out.
- **Smell:** A materialized collection with no fan-out estimate. One write that updates an unbounded set of rows in the request. A read-time join or aggregation over a growing collection. One hot parent (a requirement with 100k results) handled like a normal one.
- **Fix:** Write the numbers in the design note. Enqueue the fan-out and accept the lag. Coalesce repeated updates. Handle outliers apart (merge on read, or sample). Expire rows nobody reads.
- **Cost:** Write amplification. Staleness (DD21).
- **DDIA2 p.35-36, p.143, p.555-557.**

### DD4 Normalize what changes; denormalize what is read

- **Rule:** Store an id reference for anything shared or independently changing. Embed only data with the same lifecycle and the same atomicity. Every denormalized copy is derived data (DD1) and needs an owner and an update path.
- **Smell:** Human-readable names copied into many documents with no refresh path. An embedded array that grows without bound. A `$lookup` chain on a hot read path.
- **Fix:** Reference by id with one resolver. Or copy the value and label it an as-of snapshot that is never refreshed.
- **DDIA2 p.72-74.**

### DD5 Append facts; correct with new facts

- **Rule:** Where accountability matters, store immutable facts (verdicts, status changes, actor, time) and correct by adding a superseding fact. Derived views are recomputable from them.
- **Smell:** A verdict overwritten in place. Rows deleted to "fix" data. No way to answer "why does this value hold?".
- **Fix:** An append-only document or a history. Derive the current state. Keep actor and cause. Plan deletion explicitly: retention class, and crypto-shredding where immutable copies exist.
- **Scope:** Evidence and audit data. Do not apply to every collection.
- **DDIA2 p.101-104, p.509-512, p.576-577.**

## Models and evolution

### DD6 Data outlives code; mixed versions are normal

- **Rule:** Old and new code run at the same time: rolling upgrades, long worker jobs, messages queued by old code. Require backward compatibility (new code reads old data) and forward compatibility (old code tolerates new data).
- **Smell:** A deploy that works only if every pod flips at once. A queued job payload that new code cannot read. A migration that must finish before new code can serve.
- **Fix:** Expand, then migrate, then contract (DD8). Version payloads. Test both directions in CI.
- **DDIA2 p.161-162, p.178-179.**

### DD7 Unknown fields survive read-modify-write

- **Rule:** Code that loads a document and writes it back must not drop fields it does not know.
- **Smell:** A pydantic model with the default `extra="ignore"`, then `replace_one(model.model_dump())`. PATCH implemented as load, modify, replace. A client that re-sends a whole object built from an older generated type.
- **Fix:** Update named paths with `$set`; never replace the whole document. Or keep extras on the model. Clients send only changed fields.
- **DDIA2 p.162-163.**

### DD8 Additive inside a version; expand and contract otherwise

- **Rule:** A new optional field or enum value is safe only if readers ignore what they do not know. A rename, removal, narrowing, or new required field takes several releases.
- **Smell:** A rename in one deploy. A new required field with no default. A client `switch` over an enum with no default arm. A migration script as the only path.
- **Fix:** Add the new field. Write both. Backfill, or migrate lazily on read, and record `schema_version` on the document. Switch readers. Remove the old field when no reader remains. Render an unknown enum value as a visible "unknown".
- **Cost:** Several releases. Temporary double writes.
- **DDIA2 p.80, p.162, p.178-179.**

### DD9 A change feed is an API

- **Rule:** Events, outbox rows, change-stream consumers, and published clients are contracts. Do not leak the internal document shape through them by accident.
- **Smell:** A consumer reads raw change-stream documents. An event carries the whole document body. Renaming an internal field breaks a worker or a client.
- **Fix:** A dedicated, versioned envelope: identity and version, body by refetch. Diff the contract snapshot in CI.
- **DDIA2 p.507.**

### DD10 Pin the version of what a result was computed with

- **Rule:** When a result depends on something that changes (configuration, schema, field map, rate table), store the identifier and version used at the time. "Current" gives a different answer on reprocessing.
- **Smell:** Re-running a parser or rollup changes old results. "Which configuration produced this?" has no answer.
- **Fix:** Store the configuration id and `schema_version` on the produced document. Keep old versions: disable them, do not delete.
- **DDIA2 p.525-526.**
