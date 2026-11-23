# hello suite: gaps and decisions

## Decisions

| ID | Decision | Reason |
| --- | --- | --- |
| D1 | No remote. Chapter branches merge locally into `feat/plans-hello` with `--no-ff`. | The toy repo has no GitHub remote. The real workflow would use pull requests. |
| D2 | `UnsupportedLanguageError` subclasses `ValueError`. | Carried over from the level 3 contract. An unknown code is a bad argument. |
| D3 | `require_name` rejects only the empty string. It does not trim whitespace. | Matches the plan wording: "empty name raises `ValueError`". Keeps the rule visible. |
| D4 | `--language` is required. `--name` defaults to `world`. | The plan's CLI signature has no default for the language. |
| D5 | Both an unknown language and an empty name exit with code 2. The CLI maps both to `typer.BadParameter`. | Click's usage-error exit code is 2, so both errors get the same code. |
| D6 | Runtime dependency `typer>=0.12`. | Pin a floor, let `uv.lock` pin the exact version. |
| D7 | Worktrees live under `.worktrees/`, which is gitignored. | Keeps isolated checkouts inside the repo without tracking them. |

## Gaps

| ID | Gap | Handling |
| --- | --- | --- |
| G1 | The chief-of-staff skill expects a `.plans/PLAN_TEMPLATE.md`. This toy repo has none. | This suite uses the same metadata: frontmatter with `id`, `depends_on`, `touches`, `execution`, plus a rollout with a matrix, batches, integration order, and critical path. |
| G2 | No implementer has seen the level 3 code. Chapters start from an empty package. | Implementers must write from the chapter plans, not copy `03-subagent/`. Levels are standalone snapshots. |
| G3 | Whitespace-only names pass `require_name`. | Accepted under D3. Revisit only if the talk needs it. |
