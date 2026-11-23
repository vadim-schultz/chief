---
name: google-docguide
description: Applies Google engineering documentation guide rules to Markdown in code repos (README, docs/, plan files). Use when writing or editing repo documentation, Markdown style, doc structure, TOC, or when the user names Google docguide or engineering docs style.
disable-model-invocation: true
---

# Google engineering documentation (docguide)

Paraphrased from the Google documentation guide, `styleguide/docguide/`. For full detail see [reference.md](reference/reference.md).

## When to use

- New or revised **README**, `docs/`, plan files, or other **repo Markdown**
- Doc **lifecycle** questions (update with code, delete stale pages, avoid duplication)
- **Formatting** (headings, lists, code fences, links, line length)

Not for: Google Docs/Drive (use the `docs` connector skill), STE-controlled procedure text (use `asd-ste100`), or Python docstrings (use `docstrings.mdc`).

## Quick workflow

1. **Classify** the doc layer (name → comment → API doc → README → docs dir → design archive).
2. **Minimum viable:** keep only what readers need now; delete or fix wrong content.
3. **Draft** in plain Markdown; separate content from presentation.
4. **Format** per reference (one H1, ATX headings, fenced code with language, prefer Markdown over HTML).
5. **Ship with code** when the doc describes behavior that changed in the same change.

## Checklist (high signal)

- [ ] Short intro (1–3 sentences) before deep content
- [ ] Single `#` title; further sections start at `##`
- [ ] Unique, descriptive heading text (good anchor names)
- [ ] `[TOC]` after intro when the host supports it and content is long
- [ ] ~80-character lines where practical (exceptions: links, tables, headings, code)
- [ ] No trailing whitespace; avoid `  ` line breaks — use paragraph breaks
- [ ] Fenced code blocks with language tag; inline code for identifiers
- [ ] Link to canonical guides instead of duplicating org-wide process docs
- [ ] Update or delete docs in the same change set as code when possible

## Philosophy (defaults)

- **Radical simplicity** — few distractions; Markdown for the busy engineer.
- **Readable source** — plain text wins; content separate from theme/renderer.
- **Minimum viable documentation** — small, accurate set beats a sprawling wiki.
- **Better over best** — iterate; do not block on perfect prose.

## Examples

**Before (README):**

```markdown
# tidelog

this is a thing that does stuff. you might want to use it. see below.
```

**After:**

```markdown
# Tidelog

Tidelog records tide readings for the forecast API.
This directory holds the worker binary and its configuration.

## Get started

See [docs/get-started.md](docs/get-started.md).
```

## Additional resources

- [reference.md](reference/reference.md) — philosophy, best practices, Markdown rules with source URLs
- Sibling: `technical-writing` — merged checklist with STE provenance
- Sibling: `asd-ste100` — controlled English for procedures and safety text
