# Stack knowledge and VS Code target - run ledger

Every chapter starts as `pending`. The chief moves a row to `running` when the implementer starts. Then the chief moves it to `done` or `blocked`. A `done` row records the local commit and the local merge. Nothing is pushed before the release chapter.

**Loop branch:** `feat/stack-knowledge`
**Release branch:** `main`
**Rollout:** [01-rollout.md](01-rollout.md) · **Decisions:** [gaps-and-decisions.md](gaps-and-decisions.md) · **Chapters:** [chapters/README.md](chapters/README.md)

## Chapter status

| Chapter | Status | Commit | Local gate | Remote CI | Pull request |
| --- | --- | --- | --- | --- | --- |
| C0 | done | 906f0ce | ./ci.sh all @ 906f0ce, exit 0 (290 passed, 1 skipped) | not run (policy) | none (integrated locally) |
| C1 | done | 754e735 | ./ci.sh all @ 754e735, exit 0 (302 passed, 1 skipped in 111.18s (0:01:51)) | not run (policy) | none (integrated locally) |
| C2a | done | 6483c74 | ./ci.sh all @ 6483c74, exit 0 (327 passed, 1 skipped) | not run (policy) | none (integrated locally) |
| C2b | done | a5dd84f | ./ci.sh all @ a5dd84f, exit 0 (343 passed, 1 skipped) | not run (policy) | none (integrated locally) |
| C2c | done | 2dbf29a | ./ci.sh all @ 2dbf29a, exit 0 (349 passed, 1 skipped) | not run (policy) | none (integrated locally) |
| C2d | done | 551a2a6 | ./ci.sh all @ 551a2a6, exit 0 (354 passed, 1 skipped) | not run (policy) | none (integrated locally) |
| C2e | verified, waiting for serial integration | ef128d7 (chapter branch) | ./ci.sh all @ ef128d7, exit 0, before the C2b merge | not run (policy) | none (integrated locally) |
| C3 | pending | none | none | not run (policy) | none (integrated locally) |
| C4 | pending | none | none | not run (policy) | none (integrated locally) |
| C5 | pending | none | none | not verified | none |
