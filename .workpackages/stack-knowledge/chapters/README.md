# Stack knowledge and VS Code target - chapters

Each chapter file names its own dependencies, its own paths and its own gate. The scheduling matrix in [../01-rollout.md](../01-rollout.md) is the source of truth for `depends_on` and `touches`. Read the chapters in ID order.

## Chapter list

| ID | Chapter | Depends on | Chapter file |
| --- | --- | --- | --- |
| C0 | Name scrub | none | [00-name-scrub.md](00-name-scrub.md) |
| C1 | VS Code target | none | [01-vscode-target.md](01-vscode-target.md) |
| C2a | Stack docs pack | none | [02-stack-docs.md](02-stack-docs.md) |
| C2b | Stack cloud pack | C2a | [03-stack-cloud.md](03-stack-cloud.md) |
| C2c | Stack data services pack | C2a | [04-stack-data-services.md](04-stack-data-services.md) |
| C2d | Stack python pack | C2a | [05-stack-python.md](05-stack-python.md) |
| C2e | Stack web pack | C2a | [06-stack-web.md](06-stack-web.md) |
| C3 | Bundle complete gate | C2b, C2c, C2d, C2e | [07-bundle-complete-gate.md](07-bundle-complete-gate.md) |
| C4 | Docs and changelog | C1, C3 | [08-docs-and-changelog.md](08-docs-and-changelog.md) |
| C5 | Release | C1, C3, C4 | [09-release.md](09-release.md) |

## Dependency graph

```text
C0
C1  ------------------------------------------------> C4 -> C5
C2a -> C2b --\                                        ^
     -> C2c ---> C3 -------------------------------> /
     -> C2d --/
     -> C2e --/
```

C0, C1 and C2a start together in batch 1. C2b, C2c, C2d and C2e start together in batch 2, once C2a is integrated. C3 waits for all four. C4 waits for C1 and C3. C5 waits for C1, C3 and C4.
