# Stack knowledge and VS Code target - run ledger

Every chapter starts as `pending`. The chief moves a row to `running` when the implementer starts. Then the chief moves it to `done` or `blocked`. A `done` row records the local commit and the local merge. Nothing is pushed before the release chapter.

**Loop branch:** `feat/stack-knowledge`
**Release branch:** `main`
**Rollout:** [01-rollout.md](01-rollout.md) · **Decisions:** [gaps-and-decisions.md](gaps-and-decisions.md) · **Chapters:** [chapters/README.md](chapters/README.md)

## Chapter status

| Chapter | Status | Commit | Local gate | Remote CI | Pull request |
| --- | --- | --- | --- | --- | --- |
| C0 | done | 906f0ce | ./ci.sh all @ 906f0ce, exit 0 (290 passed, 1 skipped) | not run (policy) | none (integrated locally) |
| C1 | running: skipped-rule line blocked; D12 amends touches | 58e5ff0 (chapter branch, not yet merged) | pending re-run | not run (policy) | none (integrated locally) |
| C2a | pending | none | none | not run (policy) | none (integrated locally) |
| C2b | pending | none | none | not run (policy) | none (integrated locally) |
| C2c | pending | none | none | not run (policy) | none (integrated locally) |
| C2d | pending | none | none | not run (policy) | none (integrated locally) |
| C2e | pending | none | none | not run (policy) | none (integrated locally) |
| C3 | pending | none | none | not run (policy) | none (integrated locally) |
| C4 | pending | none | none | not run (policy) | none (integrated locally) |
| C5 | pending | none | none | not verified | none |
