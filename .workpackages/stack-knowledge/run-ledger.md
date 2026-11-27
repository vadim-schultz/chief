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
| C2e | done | 12798df | ./ci.sh all @ 12798df, exit 0 (360 passed, 1 skipped) | not run (policy) | none (integrated locally) |
| C3 | done | e3dbebe | ./ci.sh all @ e3dbebe, exit 0 (371 passed, 1 skipped) | not run (policy) | none (integrated locally) |
| C4 | done | 8af4e3e | ./ci.sh all @ 8af4e3e, exit 0 (380 passed, 1 skipped) | not run (policy) | none (integrated locally) |
| C5 | waiting for release confirmation: live checks pass; strict leak gate needs the local denylist | 32be923 (loop head) | ./ci.sh all @ 8af4e3e, exit 0 (380 passed, 1 skipped); strict leak tests: 2 failed, denylist missing at ~/.config/chief/leak-denylist.txt | not run (policy) | none yet |


## C5 live checks (run on 32be923, nothing pushed)

- `chief list`: 9 core packs and stack packs listed.
- `chief install --target vscode --dry-run` in a temporary HOME: writes nothing, prints one skipped-rule line for each of six rules.
- `chief install --target all` in a temporary HOME: 22 skills per target; no MCP configuration file written; no rules under `~/.copilot`.
- `chief doctor`: no drift for cursor, claude, opencode and vscode.
- `chief export --target all`: 317 files.
- `tox -e docs` (sphinx -W): build succeeded.
- `CHIEF_LEAK_STRICT=1 pytest tests/test_no_leaks.py`: 2 failed, 27 passed. The two failures are `test_tree_stays_within_baseline` and `test_leak_gate_is_strict_after_sweep`. Both require the local denylist, which is not on this machine.
