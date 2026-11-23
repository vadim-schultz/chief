---
type: Reference
title: "Language notes"
description: "Idioms for applying the refactoring steps in Python, TypeScript, Rust, C/C++ and Go."
tags: [refactoring, languages]
generated: { by: "human:vadim-schultz", at: "2026-11-19T00:00:00Z" }
---

# Language notes

| Language | Early return | Dispatch with three or more arms |
| --- | --- | --- |
| Python | `if not user: return None` | `match` on the kind |
| TypeScript | `if (!user) return null;` | Lookup table typed as `Record<Kind, Handler>` |
| Rust | `let Some(user) = user else { return None };` | `match` on an enum |
| C/C++ | `if (!user) return -EINVAL;` | `switch` on an enum |
| Go | `if err != nil { return err }` | `map[Kind]func(...)` lookup table |
