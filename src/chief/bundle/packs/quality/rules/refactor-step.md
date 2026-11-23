---
name: refactor-step
description: The refactor step is a mandatory gate — audit checklist to run after every green
---

# Refactor Step (the third phase)

The size rules apply to every language. The line counts are defaults.

Green is not done. Every red → green → **refactor** loop ends with an explicit refactor pass. Never open the next failing test on top of unrefactored green code.

## Rules of the pass

- **Behavior stays identical.** No new features, no new branches, no new tests in this step.
- **Tests stay green.** Re-run the narrow suite after *each* extraction, not once at the end.
- **Extract, don't branch.** When a change wants an `if`, ask whether it wants a named unit instead.

## Scope

Audit the **containing entity**, not just the lines you added or edited.

| Change landed in… | Refactor scope |
|---|---|
| A method or function | The **entire method** — including pre-existing branches, helpers, and control flow |
| A class | The **entire class** — all methods and shared state |
| Module-level helpers only | Those helpers **and** every method that calls them |

**Count every arm in the containing entity.** Pre-existing `if` / `elif` / `else` / `match` / `case` arms count toward the total. The trigger is **total > 2** for the same decision — not "this loop caused a 2→3 transition." A chain that already has five variants must be extracted in this pass even if this loop added none. Do not skip because the extra branches were already there.

## Audit checklist

Walk the **containing entity** (per scope above) against code-structure.mdc, and answer each explicitly:

- [ ] **~5 LOC** per function/method — if not, extract named helpers.
- [ ] **~100 LOC** per class/module/file — if not, split into a directory module.
- [ ] **Single concern** per unit — describable without "and"? Split orchestration / transformation / I/O.
- [ ] **Rule of three** — count **all** logical paths for the same decision in the containing entity (pre-existing arms included). If the **total is more than 2** (three or more), replace the chain with a factory, adapter, port, or handler per variant. Do not skip because the extra branches were already there, or because this loop only added one.
- [ ] **One nesting level** — aim for a single `if` / `try` / `loop` depth where feasible. Prefer guard clauses, early returns, and extracted helpers over nested `try/except`, `if` chains, or `match` arms. When a second layer appears, extract the inner block to a named unit before adding the next test.
- [ ] **Dispatch only** in `match`/`switch` — arms route to named units, never hold logic.
- [ ] **Duplication** — same shape twice with one differing detail? Extract a helper parameterized by that detail.
- [ ] **Boolean parameters** — does a method change behavior based on a passed flag (`is_manual`, `execution_mode` threaded as a switch)? That is two methods in disguise. Select the variant once at the boundary (handler, strategy, overload) and call the named unit.
- [ ] **Data clumps** — is the same tuple of fields checked together in multiple places (`test_plan_key` + `batch_id` + `ticket_run_key`, or `execution_mode` + parser + model class)? Centralize in one predicate, handler, or discriminated-union member.
- [ ] **Names** — does each unit say what it does rather than how it was built?
- [ ] Types per type-hinting.mdc, docstrings per docstrings.mdc.

## Report the outcome

State what the pass produced, including when nothing was needed:

- ✅ `extracted _cases_by_definition(); ReportPayloadBuilder 112 → 78 LOC`
- ✅ `no refactor needed — two 4-line methods, one concern each`
- ❌ moving to the next test without saying anything

## Don't over-engineer

Stay within the containing entity — do not refactor unrelated methods, classes, or files. Pre-existing branches **inside** the containing entity are in scope; "unrelated" means other methods, classes, or files. An abstraction with one caller and no second variant in sight is speculation, not refactoring — leave it inline and note the trigger that would justify it.
