---
name: designing-data-systems
description: Distilled decision rules from "Designing Data-Intensive Applications" (Kleppmann and Riccomini, 2nd ed.), tuned to an example stack of Litestar, MongoDB, Redis, worker and React. The stack is an example, not a requirement. Use when designing or reviewing a full-stack data design - a new collection or schema, a sync, outbox or worker flow, a materialized view or cache, realtime events, concurrency or retry behaviour, a migration, or any question of whether a design stays correct under failure. Not a general reference for the book.
---

# Designing data systems

A lens for design and review. It does not replace a repository's own architecture contract.
When the two disagree, the repository wins. Say so. Do not implement the skill's version.

## Glossary

- **System of record:** the one store that owns a fact. Its value wins any disagreement.
- **Derived data:** anything rebuildable from a system of record: indexes, caches, rollups, mirrors, client state.
- **Staleness budget:** how many seconds a derived view may lag. Staleness is temporary.
- **Integrity:** no lost, duplicated, or contradictory facts. A violation is permanent.
- **Command:** a document that records an intent and its outcome.

## Choose a mode

- **Design:** a new feature, collection, or flow. Run the design pass. Produce a design note.
- **Review:** an existing design, diff, or code path. Run the review scan. Produce a findings table.

Both modes use the same rules. Rule IDs are `DD1` to `DD33`. Cite them.

## Design pass

Do the steps in order. Write `n/a: <reason>` for a step that does not apply. Do not pad.

| # | Step | Ask | Rules |
| --- | --- | --- | --- |
| 0 | Numbers | Load, fan-out, p99 target, staleness budget, integrity-critical facts, retention, people data? | DD3 DD21 DD29 DD33 |
| 1 | Owners | Which store owns each fact? What is derived? How is it rebuilt? | DD1 DD4 DD5 |
| 2 | Shape | Where is the document boundary? One invariant per document? What is pinned? | DD4 DD10 DD11 |
| 3 | Write path | Precondition? Idempotency key? Uniqueness? Any clock used for order? | DD12 DD13 DD14 DD16 |
| 4 | Async path | Trigger? Delivery guarantee? Step outcome stored? Idempotent or fenced? Output atomic? Queue bounded? | DD2 DD15 DD17 DD18 DD19 DD20 |
| 5 | Read path | Which view? Which index? Own-write reads? Push or poll? | DD3 DD22 DD23 DD24 DD25 |
| 6 | Evolution | Mixed versions? Unknown fields? Expand then contract? Change feed contract? | DD6 DD7 DD8 DD9 |
| 7 | Failure | Timeouts and retries? External systems mirrored? Config as data? | DD26 DD27 DD28 |
| 8 | Verify | Which invariants? Which reconcile job? Recovery proven? Which metrics? | DD30 DD31 |
| 9 | Reversible | Rollback named? Could one node do this? | DD29 DD32 |

Rule text: [rules-data.md](reference/rules-data.md) (DD1-DD10), [rules-writes.md](reference/rules-writes.md) (DD11-DD20),
[rules-reads-ops.md](reference/rules-reads-ops.md) (DD21-DD33). Read only the file for the step you are on.

Design note template:

```text
Design note: <name>
Numbers:   <load, fan-out, p99, staleness budget, integrity-critical facts>
Records:   <fact -> owning store or collection>
Derived:   <view -> source -> rebuild path -> staleness budget>
Write:     <command -> precondition -> idempotency key -> uniqueness mechanism>
Async:     <trigger -> delivery guarantee -> idempotent step -> fence -> failure state>
Read:      <view -> index -> freshness -> client cache rule>
Evolution: <compatibility plan, expand and contract steps>
Failure:   <timeout, retry, overload, stale-serve behaviour>
Verify:    <invariant -> reconcile job -> metric>
Cost:      <what this design accepts: lag, write amplification, extra store>
Rejected:  <alternative -> rule that rejected it>
Open:      <unknowns that would change the design>
```

## Review scan

1. Read the whole artifact. List every write and every read in it.
2. Pick rows from the table that match the artifact types present. Check each rule listed.
3. Record evidence for each finding: `file:line` or a quoted design sentence.
4. Rank by class: **integrity** first, then **timeliness**, then **operability**.
5. Choose a fix. State the cost the fix accepts.
6. Mark each finding `apply`, `observed` (out of scope, not touched), or `accepted-risk` (name the trigger).

| Artifact | Rules |
| --- | --- |
| Handler, PATCH, POST | DD11 DD12 DD13 DD14 DD16 DD25 |
| Worker, job, parser | DD14 DD15 DD18 DD19 DD20 DD26 |
| Model, schema, migration | DD6 DD7 DD8 DD9 DD10 |
| Collection, rollup, cache | DD1 DD2 DD3 DD4 DD5 DD21 DD24 DD30 |
| Events, realtime, UI cache | DD17 DD22 DD23 |
| External integration | DD26 DD27 |
| Deploy, config, ops | DD28 DD29 DD31 DD32 DD33 |

Report format:

```text
Reviewed: <artifact and scope>
Numbers assumed: <load, staleness, integrity-critical facts, or "not stated">

| # | rule | evidence | class | fix (cost) | action |
| --- | --- | --- | --- | --- | --- |
| 1 | DD13 | `create_run` queries, then inserts (runs.py:41) | integrity | partial unique index (one extra index) | apply |

Checked, clean: <rule IDs>
Observed, out of scope: <findings outside the change>
```

Report `none` when the scan finds nothing.

## Reject on sight

These need no analysis. Name the rule and give the fix.

1. A handler writes to two systems. `DD2`
2. Load a document, change it, replace it. `DD7` `DD12`
3. Query, then insert, to enforce uniqueness or capacity. `DD13`
4. A worker applies a status change or increment unconditionally after a long step. `DD15`
5. A request handler waits on an external system. `DD27`
6. Order or "latest" decided by wall-clock timestamps. `DD16`
7. A retry with no cap, no backoff, or no idempotency key. `DD14` `DD20` `DD26`
8. State delivered only through pub/sub. `DD17`
9. A field renamed, removed, or made required in one release. `DD8`
10. A queue, proxy, or in-code registry served as a record. `DD1`

## Output rules

- Every recommendation names the cost it accepts. A design with no stated cost is unfinished.
- Do not propose heavy machinery (log broker, 2PC, consensus service, sharding, event sourcing as the
  primary store, workflow engine). It is parked in [local-stack.md](reference/local-stack.md) with a trigger.
  Propose it only when a stated number reaches the trigger.
- Do not quote or summarize the book. Cite `DDIA2 p.N` from the rule and stop.
- Project rules stay authoritative: TDD, refactor gate, code structure, chapter scope.
  Each applied finding gets a happy-path and a negative-path test. See the proving tests in
  [local-stack.md](reference/local-stack.md).

## Files

- [rules-data.md](reference/rules-data.md): truth, derivation, models, evolution
- [rules-writes.md](reference/rules-writes.md): concurrency, retries, async work
- [rules-reads-ops.md](reference/rules-reads-ops.md): freshness, failure, verification, lifecycle
- [local-stack.md](reference/local-stack.md): what each component guarantees, settled constructs, known smells, parked machinery, proving tests
