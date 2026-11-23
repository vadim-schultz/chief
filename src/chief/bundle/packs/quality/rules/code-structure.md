---
name: code-structure
description: Small methods, single concern, factories/adapters over nesting
---

# Code Structure

The size rules apply to every language. The line counts are defaults.

Prefer small, focused units of code. These are guidelines, not hard limits — use judgment on tight glue code and obvious one-liners.

## Factories and adapters

Prefer **factories** and **adapters** over long nested functions or methods.

- **Rule of 3 — count the total, not the delta.** Two variants for the same decision may stay inline. **Three or more** must become a factory, adapter, port, or handler per variant.
- Count **every** `if` / `elif` / `else` / `match` / `case` arm for that decision in the containing entity, including arms this loop did not add. The trigger is **total > 2**, not a 2→3 crossing in this loop. A method that already has four `elif`s is already over the limit; extracting them is this pass's job.
- Isolate variation behind a narrow interface; keep call sites flat.

```python
# ❌ BAD — four arms already in the method; "they were there before this loop" is not a pass
def parse(source: str) -> Event:
    if kind == "json":
        ...
    elif kind == "syslog":
        ...
    elif kind == "cef":
        ...
    elif kind == "journald":
        ...


# ✅ GOOD — adapter per variant, factory selects
def parse(source: str, *, kind: str) -> Event:
    return parser_for(kind).parse(source)
```

## Size (Sandi Metz, as a rule of thumb)

- Aim for **~5 lines of code per function/method** when practical.
- Keep classes/modules around **~100 LOC** when practical.
- When a unit grows past that, extract helpers rather than adding branches.

## Conditionals

- Aim for **one level of nesting** (`if` / `match` / loop).
- Deeper nesting usually means a missing helper, guard clause, or early return.

```python
# ❌ BAD
if user:
    if user.active:
        if user.has_permission("read"):
            return load()

# ✅ GOOD
if not user or not user.active:
    return None
if not user.has_permission("read"):
    return None
return load()
```

## Single concern

Each function or method should do **one thing**. If you need "and" to describe it, split it:

- orchestration vs. transformation vs. I/O
- validation vs. business logic vs. persistence

Name helpers after what they do; keep the public method a short, readable sequence of steps.

## No pointless one-line wrappers

Do **not** extract a function or method whose body is a single trivial delegation — especially when the helper name and the callee are the same operation.

Extract when the unit adds real structure: multiple steps, a guard, error mapping, or a non-obvious expression that benefits from a name. A one-liner is fine **inline** when it reads clearly at the call site.

```python
# ❌ BAD — wrapper adds nothing; name and body are the same idea
def _build_status(build_client: BuildClient, build_id: str) -> BuildStatus:
    return build_client.get_build_status(build_id)


build_status = _build_status(build_client, task.build_id)

# ✅ GOOD — call the dependency directly
build_status = build_client.get_build_status(task.build_id)


# ✅ GOOD — one line, but complex enough to name
def _active_build_statuses() -> list[str]:
    return [status.value for status in BuildStatus if not status.is_terminal()]
```

## One file, one concern

Files over **~100 lines** are suspect. When a file holds more than one **independent** type definition (not a tightly-coupled struct+enum pair), split it into a directory module: `foo.rs` → `foo/{mod.rs, a.rs, b.rs}`. Use `cli/commands/*.rs` as the reference layout.

## Match statements only dispatch

A `match` should route to a named function or value per arm — never contain multi-line business logic inline. When two or more arms repeat the same shape with one differing detail, extract a shared helper parameterized by that detail.

```python
# ❌ BAD — logic inside match arms
match outcome:
    case Ok(Ok(())):
        match store.mark_complete(id):
            case Ok(): return True
            case Err(e): log(e); return False
    case Ok(Err(err)):
        match store.mark_failed(id, str(err)):
            ...

# ✅ GOOD — match dispatches, helpers own the logic
match outcome:
    case Ok(Ok(())): return mark_complete_finished(store, id)
    case Ok(Err(err)): return mark_failed_finished(store, id, &err.to_string())
    case Err(_): return mark_failed_finished(store, id, "background task panicked")
```

## Guard clauses over wrapping ifs

Even a single, non-nested `if` should invert-and-return rather than wrap the rest of the function body:

```python
# ❌ BAD
if condition:
    do_the_actual_work()

# ✅ GOOD
if not condition:
    return
do_the_actual_work()
```

## Repeated error-mapping is a helper

When the same multi-line `match` / `map_err` shape appears more than once for the same reason (e.g. "turn a not-found error into `None`", "map mutex poison into a domain error"), extract it once — even if each call site is individually short.

## DTOs and data clumps

Avoid passing the same tuple of fields across multiple boundaries (repository, publisher, handler). Centralize it in one DTO.

- **Rule of 3 parameters**: when a function or method has **more than three** arguments (excluding `self` / `cls`), use a Pydantic model (or typed dataclass) instead of a long positional/kwarg list.
- **Partial writes**: use `model_dump(exclude_none=True)` (or `exclude_unset=True` when appropriate) so optional fields stay omitted.
- **Mapping**: put boundary-specific transforms on the DTO (`to_job_update()`, `to_progress_message()`) instead of re-threading fields at each call site.

```python
# ❌ BAD — same fields threaded through persist + publish
await repository.apply_update(
    job_id, step=step, status=status, template_id=template_id, run_id=run_id
)
await publisher.publish_step(
    job_id, plan, step, template_id=template_id, run_id=run_id, status=status
)

# ✅ GOOD — one event DTO, two adapters
event = JobProgressEvent(job_id=job_id, plan=plan, step=step, ...)
await repository.apply_update(event.job_id, event.to_job_update())
await publisher.publish(event)
```
