---
type: Design Rules
title: "Write rules"
description: "Design rules DD11 to DD20 on concurrency, retries and asynchronous work."
tags: [data, design, concurrency]
generated: { by: "human:vadim-schultz", at: "2026-11-19T00:00:00Z" }
---

# Write rules: concurrency, retries, async work

Rule IDs are stable. Cite them in findings. `DDIA2 p.N` is a page in the 2nd edition.

## Concurrency and identity

### DD11 One invariant, one document

- **Rule:** Draw the document boundary so each invariant is checked and written in one document. A single-document write is atomic. A cross-document or cross-system write is not.
- **Smell:** An invariant split over two collections that must change together. A transaction used to cover a split that did not need to exist.
- **Fix:** Merge into one aggregate. Or make the second write derived (DD2). Use a multi-document transaction only inside Mongo, short, with retry on abort. Never across Mongo and another system.
- **Cost:** Larger documents. Less independent change.
- **DDIA2 p.285-287, p.329.**

### DD12 No read-modify-write in application code

- **Rule:** Use atomic operators (`$inc`, `$push`, `$set` on named paths) or compare-and-set on `version`. A PATCH carries a precondition (`If-Match`, or the expected `version`).
- **Smell:** `doc = await find(); doc.count += 1; await replace(doc)`. A PATCH with no precondition. A counter recomputed in the handler.
- **Fix:** `find_one_and_update({_id, version: n}, {$set: ..., $inc: {version: 1}})`. No match: return 412 or 409 and the client refetches. Retry blindly only when the operation is commutative.
- **DDIA2 p.299-302.**

### DD13 Check-then-act is write skew

- **Rule:** "Query, decide, write" over different documents is unsafe under concurrency. Pick one mechanism: a unique index, one document that holds the invariant, a single writer per key, or a serializable transaction.
- **Smell:** "If no active run exists for this setup, create one" as two statements. A uniqueness check in code. A quota or capacity check. A double-booked setup or device.
- **Fix:** A unique (partial) index on the invariant, for example one active run per setup. An upsert on the natural key. Or serialize by key in the worker.
- **Cost:** An extra index. A duplicate-key error the caller must handle.
- **DDIA2 p.303-307, p.566-567.**

### DD14 Idempotency key on every command

- **Rule:** Retries happen: client, proxy, worker, redelivery. Every command carries a key from the originator to the effect. A timeout means the outcome is unknown, not failed.
- **Smell:** A POST that creates a second document on client retry. A worker step that appends, increments, or sends again on re-run. "Exactly once" claimed with no key or constraint.
- **Fix:** A client-generated id or a natural key, with a unique index on the command document. Worker steps keyed by `(command id, step)`. External calls pass the same key.
- **DDIA2 p.334-335, p.528, p.562-565.**

### DD15 Tolerate or fence the zombie

- **Rule:** Anything that owns work (a job attempt, a lease, a claim, a leader) can outlive its ownership after a pause or a slow network. Either the step tolerates a second run, or the write proves the owner is still current.
- **Tolerate:** A deterministic upsert, or a call with an idempotency key (DD14), is safe when run twice. Prefer this. It needs no extra mechanism.
- **Fence:** A status transition, a read-modify-write, or a non-idempotent side effect is not safe. Condition the write on the lease or an `attempt` number (compare-and-set).
- **Smell:** A worker finishes a long step, then applies a status change or an increment with an unconditional `$set` after its lease expired and the item was reclaimed. "Set a Redis key, then write Mongo" with no token check at the write. Two attempts of one job both appending.
- **Fix:** Classify each step as idempotent or fenced. Store the `attempt` or lease number on the command. Terminal states are never left.
- **DDIA2 p.366, p.373-376, p.528.**

### DD16 Order by version, not by clock

- **Rule:** Correctness uses the per-document `version` or one writer's sequence. Wall-clock time is for display. IDs built from time (UUIDv7, ObjectId) are only roughly ordered across writers.
- **Smell:** "Latest" chosen by `max(updated_at)` across writers. Last-write-wins on timestamps. Comparing `at` values from the API host and a worker host. Deadlines computed from the wall clock.
- **Fix:** `version` or a sequence for order. A monotonic clock for durations. When time must order events, state the allowed skew.
- **DDIA2 p.362-364, p.417-419.**

## Async work and delivery

### DD17 State the delivery guarantee of every channel

- **Rule:** Each hop has one stated guarantee: at-most-once (lossy), at-least-once (duplicates), or a durable document. The consumer matches it: lossy means refetch, at-least-once means idempotent.
- **Smell:** State delivered only by pub/sub. A consumer that assumes order or single delivery. "We never miss an event."
- **Fix:** Put the state on the document. Use the channel only to say "look again". Refetch on connect and reconnect.
- **DDIA2 p.489-491, p.528, p.562.**

### DD18 A command is a document with a lifecycle; steps resume

- **Rule:** The intent is a document with `status`. Progress and outcome are fields. A terminal state is never left. Retry is a new command. A multi-step flow stores each step's outcome and resumes after the last completed step.
- **Smell:** Progress sent as a message. Step state held in memory and lost at restart. A flow that must run start to finish in one process. A PATCH on a terminal command.
- **Fix:** `status`, `step`, and `produced` on the document. Every step is idempotent (DD14) and fenced (DD15). Do not wrap steps in a distributed transaction.
- **DDIA2 p.187-189.**

### DD19 Output becomes visible all at once

- **Rule:** A job or parser that writes many rows must not leave a partial result readable as final. Inputs are immutable. A rerun gives the same output.
- **Smell:** A parser inserts rows one by one while the case already reads `succeeded`. A rerun duplicates rows. Derivation reads the wall clock or a random value.
- **Fix:** Write under a run id and flip the status last. Or use deterministic keys with upsert. Address inputs by content or key. Inject time and randomness.
- **Order for blobs:** Write the immutable blob first, then the document that references it. A sweep removes orphan blobs.
- **DDIA2 p.479-480, p.528.**

### DD20 Bound every queue

- **Rule:** A queue hides overload until it fails. State the maximum depth or age, the retry cap, the backoff, and the terminal failure state.
- **Smell:** Unbounded retries. No alert on queue age. A poison job that retries forever. One slow external system holding every worker.
- **Fix:** A retry cap with exponential backoff and jitter. A terminal `failed` status with `detail`. A concurrency limit per provider. Alert on age, not only depth.
- **DDIA2 p.38, p.489-490.**
