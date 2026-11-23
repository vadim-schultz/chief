---
name: refactoring
description: Guides smell-first refactoring for Python and TypeScript code. Use after tests pass, before the refactor gate, or when a code review asks for smells and safe design improvements.
disable-model-invocation: true
---

# Refactoring

Use this skill after the green phase of a TDD loop.

## Glossary

- **Smell:** A code pattern that may signal a design problem.
- **Refactoring:** A behavior-preserving change to code structure.
- **Containing entity:** The method, class, module, or component under review.
- **Narrow suite:** The smallest test command that checks the current change.
- **Step:** One small refactoring change followed by the narrow suite.

## Required workflow

### Phase 1: Scan for smells

1. Identify the containing entity.
2. Read the whole containing entity.
3. Check the entity against [smells.md](reference/smells.md).
4. Record evidence for each smell.
5. Choose one refactoring for each smell.
6. Mark out-of-scope smells as observed, not touched.

Use this report:

```text
Containing entity: <path and symbol>
Scope: <method, class, module, or component>

| smell | evidence | chosen refactoring | action |
| <name> | <short fact> | <name> | apply or observed |
```

Report `none` when the scan finds no smell.

### Phase 2: Apply refactorings

1. Select the smallest useful refactoring.
2. Make one small step.
3. Run the narrow suite.
4. Keep the step when the suite stays green.
5. Revert the step when the suite turns red.
6. Take a smaller step after a red result.
7. Repeat until the selected smells are addressed.

Do not add behavior during this phase.
Do not add tests during this phase.
Keep the existing tests unchanged.

## Language rules

Use the editor language service for symbol renames, extraction, and file moves.

For Python, run `ruff check`, `ruff format --check`, `mypy`, and the narrow `pytest` command.

For TypeScript, run `tsc --noEmit`, ESLint, and the narrow Vitest command.

Keep types strict. Do not add `Any`, `any`, or a silencing cast.

Add a docstring to each new public Python function.
Add TSDoc to each new exported symbol in `src/core/`.

Use a handler, adapter, factory, or registry for three or more variants.
Use a Pydantic model or typed dataclass for Python data groups.
Use a typed interface or type alias for TypeScript data groups.

Apply the same steps by hand in other languages. Idioms for five languages are in [language-notes.md](reference/language-notes.md).

## Project rules

The repository rules remain authoritative:

- refactor-step.mdc defines the refactor gate.
- code-structure.mdc defines size and branch limits.
- docstrings.mdc defines Python docstrings.
- view-plugins.mdc defines frontend registry patterns.

The Comments smell does not remove required docstrings or TSDoc.
The smell list does not justify work outside the chapter scope.

## Quick lookup

| Smell | First choices |
| --- | --- |
| Mysterious Name | Change Function Declaration, Rename Variable, Rename Field |
| Duplicated Code | Extract Function, Slide Statements, Pull Up Method |
| Long Function | Extract Function, Replace Temp with Query, Split Loop |
| Long Parameter List | Replace Parameter with Query, Introduce Parameter Object |
| Global Data | Encapsulate Variable |
| Mutable Data | Encapsulate Variable, Split Variable, Separate Query from Modifier |
| Divergent Change | Split Phase, Move Function, Extract Class |
| Shotgun Surgery | Move Function, Move Field, Extract Class |
| Feature Envy | Move Function, Extract Function |
| Data Clumps | Extract Class, Introduce Parameter Object, Preserve Whole Object |
| Primitive Obsession | Replace Primitive with Object, Extract Class |
| Repeated Switches | Replace Conditional with Polymorphism |
| Loops | Replace Loop with Pipeline, Split Loop |
| Lazy Element | Inline Function, Inline Class, Collapse Hierarchy |
| Speculative Generality | Collapse Hierarchy, Inline Function, Remove Dead Code |
| Temporary Field | Extract Class, Move Function, Introduce Special Case |
| Message Chains | Hide Delegate, Extract Function, Move Function |
| Middle Man | Remove Middle Man, Inline Function |
| Insider Trading | Move Function, Move Field, Hide Delegate |
| Large Class | Extract Class, Extract Superclass |
| Alternative Classes with Different Interfaces | Change Function Declaration, Move Function |
| Data Class | Encapsulate Record, Remove Setting Method, Move Function |
| Refused Bequest | Push Down Method, Push Down Field, Replace Superclass with Delegate |
| Comments | Extract Function, Change Function Declaration, Introduce Assertion |

## Completion report

Report the scan before the refactoring result.

Use one of these forms:

```text
Refactor gate: smells found -> <smells>, refactorings applied -> <names>.
Narrow suite: <command>, green after each step.
```

```text
Refactor gate: no change needed -> <reason>.
Narrow suite: <command>, green.
```

Read [smells.md](reference/smells.md) for signals and [refactorings.md](reference/refactorings.md) for safe steps.
