---
type: Style Guide
title: "Google docguide reference"
description: "Philosophy, best practices and Markdown rules from the Google developer documentation style guide, with source URLs."
tags: [style, writing]
generated: { by: "human:vadim-schultz", at: "2026-11-19T00:00:00Z" }
---

# Google docguide reference

Paraphrased rules. Source: Google documentation guide, `styleguide/docguide/`.

## Philosophy

Source: Google documentation guide, `styleguide/docguide/philosophy.html`

- Prefer **radical simplicity**: scalability and interoperability over feature sprawl; Markdown for the average engineer.
- **Readable source text**: plain text; keep content separate from presentation; portability over bespoke renderers.
- **Static over dynamic** when possible; balance with keeping content fresh.
- **Minimum viable documentation**: treat docs like tests — necessary work that pays off over time; brief and utilitarian beats exhaustive.
- **Better is better than best**: incremental improvement; tolerate imperfection to keep authors productive.

## Best practices

Source: Google documentation guide, `styleguide/docguide/best_practices.html`

### Minimum viable documentation

- Prefer a **small, fresh, accurate** doc set over a large broken corpus.
- **Trim continually** — remove wrong, redundant, and out-of-date material.

### Update docs with code

- Change documentation in the **same change** as the code it describes.
- Reviewers should expect README, headers, and API comments to move with behavior changes.

### Delete dead documentation

- Stale docs mislead; delete or migrate aggressively; recover from VCS if needed.

### Prefer good over perfect

- No perfect document; use proven patterns and ship improvements.

### Documentation layers (spectrum)

1. **Meaningful names** in code (variables through directories).
2. **Inline comments** — why, not what the code already says.
3. **Method/class API comments** — contract, args, returns, gotchas, errors; behavior here should often have tests.
4. **README.md** — orient newcomers: purpose, entry files, APIs, maintainers, links.
5. **`docs/`** — get started, run tests, debug, release.
6. **Design docs / PRDs** — decision record; after implementation, archive — do not treat as living user docs.
7. **External wikis** — link prominently from the repo when used.

### Duplication is evil

- Do not maintain a second guide for a common technology; **link** to the canonical guide and contribute upstream.

## Markdown style

Source: Google documentation guide, `styleguide/docguide/style.html`

Goals: readable portable source, maintainable corpus, simple memorable syntax.

### Minimum viable / iteration

- Same as philosophy: fresh accurate subset; delete cruft in small batches.
- **Better/Best rule** for doc reviews: fast iteration; reviewers suggest alternatives; authors may invoke better-over-best.

### Capitalization

- Preserve official product/tool/binary capitalization in prose and backticks.

### Document layout

```text
# Document Title

Short introduction (1–3 sentences).

[TOC]   # when supported and content is long

## Topic

## See also
```

- One **H1** per page (often matches filename).
- Optional author under title; revision history usually enough.
- **`[TOC]`** after introduction, before first H2, when not above the fold on a laptop.
- Place **See also** at the end.

### Line length

- Target **~80 characters** for body text (aligns with code review tooling).
- Exceptions: links, tables, headings, code blocks.

### Trailing whitespace

- Avoid trailing spaces; do not rely on two-space hard breaks.
- Prefer paragraph breaks; use trailing `\` sparingly for rare hard breaks.

### Headings

- Use **ATX** headings (`#`, `##`), not underline styles.
- **Unique, complete** heading names across the doc (anchor quality).
- Add blank lines around headings.

### Lists

- **Lazy numbering** for long ordered lists (`1.` on every item).
- Consistent nesting spacing for sublists.

### Code

- **Inline** backticks for identifiers and short literals.
- **Fenced** blocks with **language** declared.
- Prefer fences over indented code blocks.
- Nest fences correctly inside lists when needed.

### Links

- Prefer **explicit** paths for in-repo Markdown links.
- Avoid `../` hops unless staying in the same directory.
- Informative link titles; use **reference links** for long or repeated URLs (define after first use).

### Images and tables

- Use Markdown tables; keep tables readable; long tables may exceed 80 columns.

### HTML

- **Strongly prefer Markdown to HTML** unless Markdown cannot express the need.

## README (layer guidance)

Source: best practices layer 4 (dedicated README HTML page was not available at docguide index during skill authoring).

A README should answer:

- What belongs in this directory?
- Which files should a developer open first? What is public API?
- Who maintains this tree and where is deeper documentation?
