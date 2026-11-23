---
name: tdd
description: Test-driven development — red-green-refactor loop for features and fixes
---

# Test-Driven Development

In compiled languages, a red test must compile before it fails.

Use the **red → green → refactor** loop for feature work and non-trivial bug fixes. Tests define behavior; production code exists to satisfy them.

## One loop = happy path + negative path

Each TDD loop covers **one slice of behavior** with **two tests**:

| Test | Asserts |
|------|---------|
| **Happy path** | Valid input produces the expected success outcome |
| **Negative path** | Invalid, missing, or forbidden input fails in an **expected** way |

A loop is not complete until **both** tests exist and pass. Do not start the next slice on a happy-path-only green.

**Negative path** means the failure mode is explicit and stable — not "something went wrong":

- Raised exception type (and message when user-facing or diagnostic)
- Validation / rejection result (HTTP 4xx, `Result::Err`, `pytest.raises`, etc.)
- Empty or unchanged state when the operation must not proceed
- No side effects when input is rejected (no partial writes, no enqueue)

Pick the assertion that matches how callers observe failure. Skip the negative test only when the slice has no meaningful failure mode (e.g. a pure getter with no invalid input).

## Planning

When planning implementation, structure the plan around the TDD loop—not around files or classes first.

1. **Red** — define the happy-path and negative-path tests for one slice
2. **Green** — implement the minimum code to pass **both**
3. **Refactor** — audit the result per refactor-step.mdc

Every step in a written plan must spell out all three phases. Name **both** tests and what each asserts, then name the refactor candidates you already expect — including in the **containing method or class**, not only the lines about to change.

## Red: write failing tests first

Before writing production code:

- Identify the slice: happy path, the primary failure mode, and any regressions.
- Write **both** tests — success outcome and expected failure — before implementation.
- Run the relevant test suite and **confirm both fail** for the right reason (missing behavior, not typos or setup errors).
- Do not proceed to implementation until you have seen meaningful failures on both paths.

```text
# ❌ BAD — implement first, test later
1. Add parse_syslog() in parsers/syslog.py
2. Wire it into the CLI
3. Add tests if time permits

# ❌ BAD — happy path only, then move on
1. test_parse_syslog_returns_log_record
2. Implement parse_syslog until green
3. Start the next feature

# ✅ GOOD — paired tests drive each loop
1. test_parse_syslog_returns_log_record — standard line
2. test_parse_syslog_rejects_malformed_timestamp — ParseError, no record returned
3. Run pytest; confirm both fail (ImportError / NotImplemented)
4. Implement parse_syslog until both pass
5. Refactor: extract _parse_timestamp() and _split_header(); re-run pytest
6. Next loop: next input variant or caller concern — again with happy + negative tests
```

## Green: implement to pass

- Write the **smallest** change that makes **both** failing tests in the current loop pass.
- Do not add untested behavior in the same step.
- Re-run tests after each meaningful change until the loop is fully green (happy + negative).

## Refactor: improve while staying green

**The refactor step is a gate, not an optional cleanup.** A loop is not complete until you have walked the audit checklist in refactor-step.mdc over the **containing method or class** — including boolean-parameter, data-clump, and **total branch-count** checks (pre-existing arms count; extract when the total for one decision is more than 2) — and reported the outcome, including when the outcome is "no change needed".

- Behavior must not change, and no new tests belong in this step.
- Flatten nesting where feasible: one level of `if` / `try` / `loop` per unit; extract inner `try/except` or `if` blocks to named helpers instead of stacking them.
- Re-run the relevant suite after each extraction; **never leave tests red**.
- Do not start the next loop (next happy/negative pair) on top of unrefactored green code.

## When TDD applies

| Work | TDD |
|------|-----|
| New feature or capability | Required |
| Non-trivial bug fix | Required — add a regression test first |
| Docs-only, config, or chore with no behavior change | Skip |
| Exploratory spike | Optional; convert to tests before merging |

## Discovering how to run tests

Use the project's test entry point (same order as CI discovery):

1. `scripts/ci.sh` or `make test`
2. `tox -e py` (or project-documented env)
3. `pytest`, `npm test`, `cargo test`, etc.

Run the **narrowest** command that includes your new tests during the loop; run the broader suite before finishing.
