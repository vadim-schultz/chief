---
type: Catalogue
title: "Refactoring catalogue"
description: "Named refactorings, each with the safe steps to apply it."
tags: [refactoring]
generated: { by: "human:vadim-schultz", at: "2026-11-19T00:00:00Z" }
---

# Refactoring catalogue

Use this file after the smell scan selects a refactoring.
The names follow Fowler's catalogue.
The guidance uses new wording and new examples.

## Catalogue index

| chapter | refactoring | alias | inverse or pair | common smells |
| --- | --- | --- | --- | --- |
| 6 | Extract Function | formerly Extract Method | Inline Function | Duplicated Code, Long Function, Comments |
| 6 | Inline Function | formerly Inline Method | Extract Function | Lazy Element, Speculative Generality, Middle Man |
| 6 | Extract Variable | formerly Introduce Explaining Variable | Inline Variable | Long Function, Comments |
| 6 | Inline Variable | formerly Inline Temp | Extract Variable | Lazy Element |
| 6 | Change Function Declaration | formerly Rename Method, Add Parameter, Remove Parameter | Rename Variable | Mysterious Name, Alternative Classes with Different Interfaces |
| 6 | Encapsulate Variable | formerly Self-Encapsulate Field | Remove access | Global Data, Mutable Data |
| 6 | Rename Variable | none | Inline Variable | Mysterious Name |
| 6 | Rename Field | none | Inline Variable | Mysterious Name |
| 6 | Introduce Parameter Object | none | Remove Parameter Object | Long Parameter List, Data Clumps |
| 6 | Combine Functions into Class | none | Extract Class | Divergent Change, Feature Envy |
| 6 | Combine Functions into Transform | none | Extract Class | Divergent Change, Data Clumps |
| 6 | Split Phase | none | Combine Functions into Transform | Divergent Change, Long Function |
| 7 | Encapsulate Record | none | Expose Record | Data Class, Insider Trading |
| 7 | Encapsulate Collection | none | Expose Collection | Mutable Data, Insider Trading |
| 7 | Replace Primitive with Object | none | Inline Class | Primitive Obsession, Data Clumps |
| 7 | Replace Temp with Query | none | Inline Function | Long Function, Mutable Data |
| 7 | Extract Class | none | Inline Class | Large Class, Divergent Change, Data Clumps |
| 7 | Inline Class | none | Extract Class | Lazy Element, Speculative Generality, Middle Man |
| 7 | Hide Delegate | none | Remove Middle Man | Message Chains, Insider Trading |
| 7 | Remove Middle Man | none | Hide Delegate | Middle Man |
| 7 | Replace Function with Command | none | Replace Command with Function | Long Function, Primitive Obsession |
| 7 | Replace Command with Function | none | Replace Function with Command | Lazy Element |
| 7 | Remove Dead Code | none | none | Speculative Generality |
| 8 | Move Function | none | Move Statements into Function | Feature Envy, Divergent Change, Shotgun Surgery |
| 8 | Move Field | none | Move Statements to Callers | Insider Trading, Shotgun Surgery |
| 8 | Move Statements into Function | none | Move Statements to Callers | Duplicated Code, Divergent Change |
| 8 | Move Statements to Callers | none | Move Statements into Function | Duplicated Code |
| 8 | Replace Inline Code with Function Call | none | Inline Function | Duplicated Code |
| 8 | Slide Statements | none | none | Duplicated Code, Long Function |
| 8 | Split Loop | none | none | Long Function, Loops |
| 8 | Replace Loop with Pipeline | none | Split Loop | Loops, Long Function |
| 9 | Split Variable | none | Combine Variables | Mutable Data |
| 9 | Rename Field | none | none | Mysterious Name |
| 9 | Replace Derived Variable with Query | none | Replace Temp with Query | Mutable Data, Long Function |
| 9 | Change Reference to Value | none | Change Value to Reference | Mutable Data |
| 9 | Change Value to Reference | none | Change Reference to Value | Mutable Data |
| 10 | Decompose Conditional | none | Inline Function | Long Function, Comments |
| 10 | Consolidate Conditional Expression | none | Decompose Conditional | Long Function |
| 10 | Replace Nested Conditional with Guard Clauses | none | Decompose Conditional | Long Function, Comments |
| 10 | Replace Conditional with Polymorphism | none | Replace Type Code with Subclasses | Repeated Switches, Primitive Obsession |
| 10 | Introduce Special Case | none | Remove Special Case | Temporary Field, Message Chains |
| 11 | Separate Query from Modifier | none | Combine Query and Modifier | Mutable Data |
| 11 | Introduce Assertion | none | Remove Assertion | Comments |
| 11 | Parameterize Function | none | Change Function Declaration | Duplicated Code |
| 11 | Remove Flag Argument | none | Add Variant Function | Long Parameter List, Long Function |
| 11 | Preserve Whole Object | none | Introduce Parameter Object | Data Clumps, Long Parameter List |
| 11 | Replace Parameter with Query | none | Replace Query with Parameter | Long Parameter List |
| 11 | Replace Query with Parameter | none | Replace Parameter with Query | Long Parameter List |
| 11 | Remove Setting Method | none | Add Setting Method | Data Class, Mutable Data |
| 11 | Replace Constructor with Factory Function | none | none | Alternative Classes with Different Interfaces |
| 11 | Replace Function with Command | none | Replace Command with Function | Long Function |
| 11 | Replace Error Code with Exception | none | Replace Exception with Precheck | Long Function |
| 11 | Replace Exception with Precheck | none | Replace Error Code with Exception | Long Function |
| 12 | Pull Up Method | none | Push Down Method | Duplicated Code, Refused Bequest |
| 12 | Pull Up Field | none | Push Down Field | Duplicated Code |
| 12 | Pull Up Constructor Body | none | Push Down Method | Duplicated Code |
| 12 | Push Down Method | none | Pull Up Method | Refused Bequest |
| 12 | Push Down Field | none | Pull Up Field | Refused Bequest |
| 12 | Replace Type Code with Subclasses | none | Replace Conditional with Polymorphism | Primitive Obsession, Repeated Switches |
| 12 | Remove Subclass | none | Extract Subclass | Lazy Element |
| 12 | Extract Superclass | none | Collapse Hierarchy | Large Class, Alternative Classes with Different Interfaces |
| 12 | Collapse Hierarchy | none | Extract Superclass | Lazy Element, Speculative Generality |
| 12 | Replace Subclass with Delegate | none | Replace Type Code with Subclasses | Refused Bequest, Large Class |
| 12 | Replace Superclass with Delegate | none | Extract Superclass | Refused Bequest, Middle Man |

## Safe steps for common refactorings

### Extract Function

Use this move when one block has one clear purpose.

1. Select a contiguous block.
2. Name the block with its purpose.
3. Pass values that the block reads.
4. Return values that the block changes.
5. Replace the block with the new call.
6. Run the narrow suite.

Python example:

```python
def result_label(verdict: str, detail: str) -> str:
    label = _label_for(verdict)
    return f"{label}: {detail}"


def _label_for(verdict: str) -> str:
    return {"pass": "Passed", "fail": "Failed"}.get(verdict, "Unknown")
```

TypeScript example:

```typescript
function resultLabel(verdict: string, detail: string): string {
  const label = labelFor(verdict)
  return `${label}: ${detail}`
}

function labelFor(verdict: string): string {
  return { pass: 'Passed', fail: 'Failed' }[verdict] ?? 'Unknown'
}
```

### Introduce Parameter Object

Use this move when several arguments form one concept.

1. Group the related values in a typed object.
2. Replace the arguments with the object.
3. Update each caller.
4. Remove the old signature.
5. Run the narrow suite.

Python example:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ResultScope:
    case_id: str
    run_id: str


def find_results(scope: ResultScope) -> list[str]:
    return load_results(scope.case_id, scope.run_id)
```

TypeScript example:

```typescript
type ResultScope = {
  caseId: string
  runId: string
}

function findResults(scope: ResultScope): string[] {
  return loadResults(scope.caseId, scope.runId)
}
```

### Replace Nested Conditional with Guard Clauses

Use this move when preconditions surround the main operation.

1. Identify one failure condition.
2. Return or raise at that condition.
3. Remove one level of nesting.
4. Repeat for the next precondition.
5. Run the narrow suite.

Python example:

```python
def publish_result(result: Result, enabled: bool) -> str:
    if not enabled:
        return "disabled"
    if result.verdict is None:
        return "missing verdict"
    return send_result(result)
```

TypeScript example:

```typescript
function publishResult(result: Result, enabled: boolean): string {
  if (!enabled) return 'disabled'
  if (result.verdict === undefined) return 'missing verdict'
  return sendResult(result)
}
```

### Replace Conditional with Polymorphism

Use this move when the same variant decision appears in three or more places.

1. Define one small handler interface.
2. Create one handler for each variant.
3. Register the handlers by stable id.
4. Select the handler from the registry.
5. Remove one conditional.
6. Run the narrow suite.

Python example:

```python
from collections.abc import Callable

Handler = Callable[[str], str]
HANDLERS: dict[str, Handler] = {
    "pass": lambda detail: f"Passed: {detail}",
    "fail": lambda detail: f"Failed: {detail}",
}


def render_result(verdict: str, detail: str) -> str:
    return HANDLERS[verdict](detail)
```

TypeScript example:

```typescript
type ResultHandler = (detail: string) => string

const handlers: Record<string, ResultHandler> = {
  pass: detail => `Passed: ${detail}`,
  fail: detail => `Failed: ${detail}`
}

function renderResult(verdict: string, detail: string): string {
  return handlers[verdict]?.(detail) ?? `Unknown: ${detail}`
}
```

Use a reviewed registry or factory for repository variants.
Do not use a branch chain when the project rules require a lookup.

### Remove Flag Argument

Use this move when a boolean chooses a different behavior.

1. Name the two behaviors.
2. Create one function for each behavior.
3. Move each call to the matching function.
4. Remove the flag from the shared function.
5. Run the narrow suite.

Python example:

```python
def start_run(run: Run) -> str:
    return _start_run(run)


def start_dry_run(run: Run) -> str:
    return _start_dry_run(run)
```

TypeScript example:

```typescript
function startRun(run: Run): string {
  return startLiveRun(run)
}

function startDryRun(run: Run): string {
  return startPreviewRun(run)
}
```

### Extract Class

Use this move when one class has two reasons to change.

1. List the fields for the new concern.
2. Create a focused class.
3. Move the fields and their functions.
4. Replace old access with the new class.
5. Run the narrow suite.

Prefer composition in Python and TypeScript.
Use Extract Superclass only when the shared contract is current and stable.

### Move Function

Use this move when a function uses another object more than its current owner.

1. Identify the data that the function needs.
2. Move the function beside that data.
3. Update its callers.
4. Remove the old function.
5. Run the narrow suite.

Keep boundary adapters near the boundary.

### Split Phase

Use this move when one operation reads data and then transforms it.

1. Name the input phase.
2. Name the transformation phase.
3. Pass a typed result between the phases.
4. Run each phase from the original entry point.
5. Run the narrow suite.

### Replace Temp with Query

Use this move when a temporary value hides a reusable calculation.

1. Extract the calculation into a named function.
2. Replace the temporary with the function call.
3. Remove the temporary.
4. Run the narrow suite.

### Decompose Conditional

Use this move when a conditional mixes several rules.

1. Name the condition.
2. Name the true branch.
3. Name the false branch.
4. Replace the blocks with calls.
5. Run the narrow suite.

### Split Loop

Use this move when one loop calculates and changes data.

1. Copy the loop boundary.
2. Keep one concern in each loop.
3. Remove the old mixed loop.
4. Run the narrow suite.

Prefer clarity over fewer loop statements.

### Replace Loop with Pipeline

Use this move when a loop has one simple collection operation.

1. Identify the map, filter, or reduction.
2. Write the pipeline beside the loop.
3. Compare the outputs.
4. Remove the loop.
5. Run the narrow suite.

Keep a loop when a pipeline hides state or control flow.

### Hide Delegate

Use this move when callers reach into private object structure.

1. Name the value or operation that callers need.
2. Add one method at the owning boundary.
3. Replace the message chain at each caller.
4. Run the narrow suite.

Do not hide a deliberate serialization path.

### Preserve Whole Object

Use this move when a caller unpacks an object only to pass its values again.

1. Pass the whole typed object.
2. Read its fields at the receiving boundary.
3. Remove the unpacked parameters.
4. Run the narrow suite.

### Remove Middle Man

Use this move when a wrapper adds no rule, type, or boundary.

1. Confirm that the wrapper adds no protection.
2. Replace the wrapper call with its target call.
3. Remove the wrapper.
4. Run the narrow suite.

Keep wrappers that enforce an invariant or hide an external system.

## Choosing a move

Prefer the smallest move that removes the selected smell.
Use one move per step.
Run the narrow suite after every step.
Stop when the containing entity is clear and the smell is gone.
