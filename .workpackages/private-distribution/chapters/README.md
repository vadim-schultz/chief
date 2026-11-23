# Private distribution - chapters

Eleven chapters, numbered C0 to C10. Each chapter is one unit of work. Each chapter ends with `./ci.sh all` green on its branch.

**Rollout:** [../01-rollout.md](../01-rollout.md) · **Architecture:** [../00-architecture.md](../00-architecture.md) · **Ledger:** [../run-ledger.md](../run-ledger.md)

The rollout file is the scheduling contract. This index repeats the chapter list for reading convenience. If the two disagree, the rollout wins.

## Chapter list

| ID | Chapter | Depends on | Chapter file |
| --- | --- | --- | --- |
| C0 | Seed the tree | none | [00-seed.md](00-seed.md) |
| C1 | Rename the package | C0 | [01-rename.md](01-rename.md) |
| C2 | Guards: hermetic env, leak gate, bundle contract | C1 | [02-guards.md](02-guards.md) |
| C3 | Remove corporate code | C2 | [03-corporate-code.md](03-corporate-code.md) |
| C4 | Packaging metadata | C2 | [04-packaging.md](04-packaging.md) |
| C5 | Scrub bundled reference text | C2 | [05-bundle-scrub.md](05-bundle-scrub.md) |
| C6 | GitHub host handling | C3 | [06-github-host.md](06-github-host.md) |
| C7 | Local-first CI policy | C4, C6 | [07-ci-policy.md](07-ci-policy.md) |
| C8 | Documentation | C3, C4, C6, C7 | [08-docs.md](08-docs.md) |
| C9 | Final sweep | C8 | [09-final-sweep.md](09-final-sweep.md) |
| C10 | Release pull request | C9 | [10-release-pr.md](10-release-pr.md) |

## Dependency graph

```text
C0 -> C1 -> C2
C2 -> C3, C4, C5
C3 -> C6
C4, C6 -> C7
C3, C4, C6, C7 -> C8
C8 -> C9 -> C10
```
