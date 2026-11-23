---
name: type-hinting
description: Strict Python type hints; no lazy Any/object; Pydantic unions and TypeAdapter
---

# Type Hinting

Scope: Python only.

Use the **strictest correct type** everywhere. Types document intent and let static checkers catch mistakes — loose annotations defeat both purposes.

## Non-negotiable

- **Never reach for `Any` or `object` as a shortcut.** They are cop-outs. Model the real shape.
- Pick the **narrowest** type that is still correct: concrete classes, unions, `Literal`, `TypedDict`, `Protocol`, `NewType`, bounded `TypeVar`, `Callable` with full signatures.
- Type function inputs/outputs, public attributes, and collection element types.
- Use `from __future__ import annotations` and modern syntax (`str | None`, `list[str]`).
- Narrow with `isinstance`, `match`, or Pydantic validation — not `cast(Any, ...)`.

## When the shape is unclear, try harder

| Situation | Use instead of `Any` / `object` |
|-----------|----------------------------------|
| Fixed dict keys | `TypedDict` |
| Duck-typed interface | `Protocol` |
| One of several models | Discriminated union + `TypeAdapter` |
| Homogeneous collection | `list[T]`, `set[T]`, `tuple[T, ...]` |
| Key-value with known value type | `Mapping[str, T]` or `dict[str, T]` |
| Callback | `Callable[[Arg1, Arg2], Return]` |
| Domain identifier | `NewType` or branded `str`/`int` |
| Unknown JSON with known schema | Pydantic model or `TypedDict` |
| Truly dynamic JSON (rare) | Recursive `JsonValue` alias — still typed |

```python
# ❌ BAD — lazy
def process(data: Any) -> Any: ...
def handle(payload: object) -> object: ...
def load(raw: dict[str, object]) -> BaseModel: ...


# ✅ GOOD — precise
def process(data: EventPayload) -> LogRecord: ...
def handle(payload: JsonEvent | SyslogEvent) -> ParsedEvent: ...
def load(raw: EventDict) -> JsonEvent | SyslogEvent: ...
```

## Pydantic: one of several models

When a value may be one of several Pydantic models, model them as a **discriminated union** and validate with **`TypeAdapter`**.

- Add a shared discriminator field (usually `type` or `kind`) with distinct `Literal` values per variant.
- Compose variants with `Annotated[ModelA | ModelB, Field(discriminator="type")]`.
- Use `TypeAdapter(UnionType).validate_python(data)` at boundaries instead of manual `if`/`isinstance` chains.
- Type the result as the union alias, not `BaseModel`, `Any`, or `object`.

```python
from typing import Annotated, Literal, TypedDict
from pydantic import BaseModel, Field, TypeAdapter


class JsonEvent(BaseModel):
    type: Literal["json"] = "json"
    message: str


class SyslogEvent(BaseModel):
    type: Literal["syslog"] = "syslog"
    hostname: str
    message: str


class EventDict(TypedDict):
    type: str
    message: str


Event = Annotated[JsonEvent | SyslogEvent, Field(discriminator="type")]
event_adapter = TypeAdapter(Event)


def parse_event(data: EventDict) -> JsonEvent | SyslogEvent:
    return event_adapter.validate_python(data)
```

## Last resort only

`Any` is acceptable **only** at an untyped third-party boundary with no stubs — convert to a precise type in the very next line. `object` is acceptable **only** in `isinstance(x, object)`-style runtime checks, never as a parameter or return annotation.
