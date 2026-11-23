---
type: Catalogue
title: "Code smells"
description: "Code smells, the signals that reveal each one, and the refactorings that address it."
tags: [refactoring, smells]
generated: { by: "human:vadim-schultz", at: "2026-11-19T00:00:00Z" }
---

# Code smells

Use this file during Phase 1 of the refactoring workflow.
Each entry gives a signal, a first choice, and a stop condition.

## Mysterious Name

**Signal:** A name does not tell the reader what the value or operation means.

**First choice:** Use Change Function Declaration, Rename Variable, or Rename Field.

**Python hint:** Name a predicate with `is_`, `has_`, or `can_`.
**TypeScript hint:** Name a boolean with `is`, `has`, or `can`.

**Leave it alone when:** The name is a stable external contract or a standard term.

## Duplicated Code

**Signal:** The same logic appears in more than one place.

**First choice:** Use Extract Function, Slide Statements, or Pull Up Method.

**Python hint:** Extract a typed helper without hiding an important domain rule.
**TypeScript hint:** Extract a typed function or a shared module.

**Leave it alone when:** The two blocks only look alike and their reasons to change differ.

## Long Function

**Signal:** One function has several concerns or needs a long explanation.

**First choice:** Use Extract Function, Replace Temp with Query, or Split Loop.

**Python hint:** Separate validation, transformation, and persistence.
**TypeScript hint:** Separate state selection, rendering, and I/O.

**Leave it alone when:** The function is short, linear, and easy to name.

## Long Parameter List

**Signal:** A call needs many values or several values always travel together.

**First choice:** Use Replace Parameter with Query or Introduce Parameter Object.

**Python hint:** Use a Pydantic model or typed dataclass.
**TypeScript hint:** Use a typed interface or type alias.

**Leave it alone when:** The parameters are independent and the public contract needs them.

## Global Data

**Signal:** Many callers can change shared data without a clear owner.

**First choice:** Use Encapsulate Variable.

**Python hint:** Replace module state with an object passed at the boundary.
**TypeScript hint:** Replace exported mutable data with a service or `readonly` value.

**Leave it alone when:** The value is immutable configuration with one clear owner.

## Mutable Data

**Signal:** A value changes in several places, so the update order matters.

**First choice:** Use Encapsulate Variable, Split Variable, or Separate Query from Modifier.

**Python hint:** Avoid mutable default arguments and hidden list changes.
**TypeScript hint:** Prefer `readonly` fields and return new values.

**Leave it alone when:** Mutation belongs to one owner and the invariant is visible.

## Divergent Change

**Signal:** One module changes for several unrelated reasons.

**First choice:** Use Split Phase, Move Function, or Extract Class.

**Python hint:** Separate external translation from domain decisions.
**TypeScript hint:** Separate data access from view selection.

**Leave it alone when:** The concerns always change together and the module is small.

## Shotgun Surgery

**Signal:** One change requires small edits in many unrelated files.

**First choice:** Use Move Function, Move Field, or Extract Class.

**Python hint:** Put data and the rule that owns it in one module.
**TypeScript hint:** Put a capability lookup and its component beside one registry entry.

**Leave it alone when:** The files are deliberate adapters at separate boundaries.

## Feature Envy

**Signal:** A function reads more data from another object than from its owner.

**First choice:** Use Move Function or Extract Function.

**Python hint:** Move the rule next to the model or port that owns its data.
**TypeScript hint:** Move the selector next to the registry that owns the entries.

**Leave it alone when:** The function is an intentional boundary adapter.

## Data Clumps

**Signal:** The same values appear together in signatures, fields, or filters.

**First choice:** Use Extract Class, Introduce Parameter Object, or Preserve Whole Object.

**Python hint:** Use one typed object across repository and service boundaries.
**TypeScript hint:** Pass one interface instead of parallel primitive values.

**Leave it alone when:** The values only share a call site by chance.

## Primitive Obsession

**Signal:** Strings, numbers, or booleans carry a rule that deserves a named type.

**First choice:** Use Replace Primitive with Object or Extract Class.

**Python hint:** Add a value object or constrained Pydantic field.
**TypeScript hint:** Add a branded type or a small immutable object.

**Leave it alone when:** The primitive is a simple boundary value with no rule.

## Repeated Switches

**Signal:** Several functions branch on the same variant or capability id.

**First choice:** Use Replace Conditional with Polymorphism.

**Python hint:** Select a handler from a registry or factory.
**TypeScript hint:** Select a component or function from a typed registry.

**Leave it alone when:** The decision has two stable branches and no third variant exists.

## Loops

**Signal:** A loop hides a simple selection, mapping, or reduction.

**First choice:** Use Replace Loop with Pipeline or Split Loop.

**Python hint:** Use a comprehension or generator when it stays readable.
**TypeScript hint:** Use `map`, `filter`, or `reduce` when types remain clear.

**Leave it alone when:** The loop has state, branching, or an early exit that a pipeline hides.

## Lazy Element

**Signal:** A function, class, or module adds little value over direct code.

**First choice:** Use Inline Function, Inline Class, or Collapse Hierarchy.

**Python hint:** Remove a wrapper that only delegates one call.
**TypeScript hint:** Remove a component that only forwards props without behavior.

**Leave it alone when:** The element is a public boundary or a planned extension point.

## Speculative Generality

**Signal:** An abstraction exists for a possible future case, not a current need.

**First choice:** Use Collapse Hierarchy, Inline Function, or Remove Dead Code.

**Python hint:** Remove an unused base class or strategy with one caller.
**TypeScript hint:** Remove an unused generic or interface member.

**Leave it alone when:** A current caller needs the abstraction and its contract is clear.

## Temporary Field

**Signal:** A field has a value only during one operation or lifecycle.

**First choice:** Use Extract Class, Move Function, or Introduce Special Case.

**Python hint:** Keep operation state in a local typed object.
**TypeScript hint:** Keep temporary state in a scoped object or function.

**Leave it alone when:** The field expresses a real lifecycle state.

## Message Chains

**Signal:** A caller follows several objects to reach one value or operation.

**First choice:** Use Hide Delegate, Extract Function, or Move Function.

**Python hint:** Add a meaningful boundary method on the owning object.
**TypeScript hint:** Expose one typed selector instead of nested property access.

**Leave it alone when:** The chain is a clear data traversal at a serialization boundary.

## Middle Man

**Signal:** A function only forwards calls and adds no rule or boundary value.

**First choice:** Use Remove Middle Man or Inline Function.

**Python hint:** Keep a wrapper only when it enforces an invariant or port.
**TypeScript hint:** Keep a wrapper only when it narrows types or selects a capability.

**Leave it alone when:** The wrapper hides an external client or protects a stable port.

## Insider Trading

**Signal:** Modules exchange too much private data to complete one operation.

**First choice:** Use Move Function, Move Field, or Hide Delegate.

**Python hint:** Pass a small DTO instead of exposing internal collections.
**TypeScript hint:** Pass a readonly view instead of a mutable object.

**Leave it alone when:** The exchange is the defined DTO boundary.

## Large Class

**Signal:** One class owns several unrelated responsibilities or many fields.

**First choice:** Use Extract Class or Extract Superclass.

**Python hint:** Prefer focused modules and composition over a large class.
**TypeScript hint:** Prefer focused services and typed composition.

**Leave it alone when:** The class has one concern and its size comes from data only.

## Alternative Classes with Different Interfaces

**Signal:** Two classes provide the same role through different method names.

**First choice:** Use Change Function Declaration, Move Function, or Extract Superclass.

**Python hint:** Define one protocol and adapt each implementation to it.
**TypeScript hint:** Define one interface and adapt each implementation to it.

**Leave it alone when:** The classes serve different boundaries with no shared caller.

## Data Class

**Signal:** A class stores data but has no behavior that protects the data.

**First choice:** Use Encapsulate Record, Remove Setting Method, or Move Function.

**Python hint:** Use an immutable value object when callers only read data.
**TypeScript hint:** Use a readonly type when no behavior belongs to the object.

**Leave it alone when:** The class is a deliberate DTO at an API or persistence boundary.

## Refused Bequest

**Signal:** A subtype inherits members that it cannot support or should not expose.

**First choice:** Use Push Down Method, Push Down Field, or Replace Superclass with Delegate.

**Python hint:** Use a protocol and composition when inheritance adds unused members.
**TypeScript hint:** Use an interface or adapter instead of a broad base class.

**Leave it alone when:** The inherited contract is valid for every subtype.

## Comments

**Signal:** A comment explains code that a clearer name or structure could explain.

**First choice:** Use Extract Function, Change Function Declaration, or Introduce Assertion.

**Python hint:** Keep required public docstrings and remove only redundant inline comments.
**TypeScript hint:** Keep required TSDoc and remove comments that repeat the code.

**Leave it alone when:** The comment records a reason, invariant, external constraint, or warning.

## Project-rule mapping

Apply these repository rules with the smell scan:

- Map Long Function to the small-unit rule.
- Map Repeated Switches to the three-path rule.
- Map Long Parameter List and Data Clumps to the DTO rule.
- Map boolean behavior to Remove Flag Argument in [refactorings.md](refactorings.md).
- Map Middle Man to the no-wrapper rule.
- Map Speculative Generality to the one-caller rule.
- Treat refactor-step.mdc as the refactor gate.
- Treat code-structure.mdc as the structure rule.
- Treat docstrings.mdc as the Python documentation rule.
