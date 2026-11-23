---
name: technical-writing
description: Unified technical writing checklist merging Google engineering docguide and ASD-STE100 Part 1 with provenance tags on each rule. Use when drafting or editing documentation, README, procedures, safety text, or when the user asks for clear technical prose with traceable standards.
disable-model-invocation: true
---

# Technical writing

Merged guidance from `google-docguide` and `asd-ste100`. Every bullet below is **normative** and
tagged with its source(s). For depth, load sibling skills or their `reference/reference.md` files.

## Workflow

1. **Classify** the piece:
   - **Repo Markdown** (README, `docs/`, plan files) → emphasize `[google-docguide:…]` bullets.
   - **Procedure / safety / user-facing technical English** → emphasize `[ste:…]` bullets.
   - **Mixed** (e.g. README with install steps) → apply both; use Precedence below.
2. **Draft** using the checklists in order: purpose → structure → sentences → format.
3. **Verify** STE sentences against dictionary/glossary when `[ste:…]` applies.
4. **Ship** doc updates with code when behavior changed. `[google-docguide:best-practices]`

## Precedence

| Situation | Wins |
| --- | --- |
| Markdown layout, TOC, fences, links, doc lifecycle | Google docguide |
| Word choice, sentence length in procedures, imperatives, safety | STE |
| Both say “short, clear sentences” | One bullet, **dual tags** |

## Principles

- Prefer radical simplicity and readable plain-text source. `[google-docguide:philosophy]`
- Minimum viable documentation: small, accurate, trimmed often. `[google-docguide:philosophy]` `[google-docguide:best-practices]`
- Better over best: iterate; do not block on perfect prose. `[google-docguide:philosophy]` `[google-docguide:markdown]`
- Use approved STE vocabulary and structure for controlled passages. `[ste:1.1]` `[ste:9.4]`

## Doc lifecycle and corpus

- Update documentation in the **same change** as the code it describes. `[google-docguide:best-practices]`
- Delete or fix wrong, redundant, and stale docs; recover from VCS if needed. `[google-docguide:best-practices]`
- Link to canonical org guides; do not duplicate them in-repo. `[google-docguide:best-practices]`
- Treat design docs as archives after implementation, not living user manuals. `[google-docguide:best-practices]`

## Structure and layers

- Use meaningful names in code before extra comments. `[google-docguide:best-practices]`
- Inline comments explain **why**; API comments state **contract** (args, returns, errors). `[google-docguide:best-practices]`
- README orients newcomers: purpose, entry files, API surface, maintainers, links. `[google-docguide:best-practices]` `[google-docguide:readme]`
- `docs/` covers get started, test, debug, release. `[google-docguide:best-practices]`

## Markdown format (repo docs)

- One `#` title; sections from `##`; unique descriptive headings. `[google-docguide:markdown]`
- Short introduction (1–3 sentences) before deep content. `[google-docguide:markdown]`
- Put `[TOC]` after the intro when the host supports it and content is long. `[google-docguide:markdown]`
- Target ~80-character lines except links, tables, headings, code. `[google-docguide:markdown]`
- ATX headings; fenced code with language; prefer Markdown over HTML. `[google-docguide:markdown]`
- No trailing whitespace; prefer paragraph breaks over hard-break tricks. `[google-docguide:markdown]`
- Preserve official product capitalization. `[google-docguide:markdown]`

## Words and terms (STE)

- Use dictionary-approved words with correct part of speech and meaning. `[ste:1.1]` `[ste:1.2]` `[ste:1.3]`
- Use company/industry technical nouns and verbs from glossary when needed. `[ste:1.5]` `[ste:1.8]` `[ste:1.12]`
- One technical noun per item; no slang/jargon as technical nouns. `[ste:1.10]` `[ste:1.11]`
- American English spelling unless a directive says otherwise. `[ste:1.14]`
- Multi-word nouns: max three words; write long terms in full. `[ste:2.1]` `[ste:2.2]`
- Rebuild sentences when dictionary swap changes meaning (no phrasal verbs). `[ste:9.1]` `[ste:9.3]`

## Verbs and voice

- Use approved verb forms; describe actions with verbs, not nominalizations. `[ste:3.1]` `[ste:3.7]`
- Prefer active voice; passive only if agent unknown in descriptive text. `[ste:3.6]`
- Avoid complex auxiliary constructions. `[ste:3.4]`

## Sentences and lists

- Write short, clear sentences; no contractions or careless omissions. `[ste:4.1]` `[ste:4.2]` `[google-docguide:philosophy]`
- Use vertical lists for complex content; connect related sentences. `[ste:4.3]` `[ste:4.4]`
- Use articles/demonstratives before nouns when applicable. `[ste:4.5]`
- Procedural sentences: max **20** words; descriptive: max **25** words. `[ste:5.1]` `[ste:6.3]`
- One imperative instruction per sentence unless simultaneous actions. `[ste:5.2]` `[ste:5.3]`
- Condition before command: descriptive clause, comma, then imperative. `[ste:5.4]`
- Notes inform; they do not instruct. `[ste:5.5]`
- Descriptive text: gradual detail; one topic per paragraph; ≤6 sentences per paragraph. `[ste:6.1]` `[ste:6.4]` `[ste:6.5]` `[ste:6.6]`

## Safety text

- Label risk (e.g. warning vs caution). `[ste:7.1]`
- Start with clear command or required condition. `[ste:7.2]`
- State hazard or consequence if disobeyed. `[ste:7.3]`

## Punctuation and STE word count

- No semicolons; use hyphens for related compounds. `[ste:8.1]` `[ste:8.2]`
- Follow STE parentheses and list colon word-count rules when counting STE sentences. `[ste:8.3]` `[ste:8.4]` `[ste:8.5]` `[ste:8.6]` `[ste:8.7]`

## Consistency

- Use each approved word correctly; keep terminology consistent. `[ste:9.2]` `[ste:9.4]`

## Sibling skills

| Skill | Use for |
| --- | --- |
| `google-docguide` | Full Google Markdown and doc-lifecycle reference |
| `asd-ste100` | Full Part 1 rule text and STE examples |

## Related rules

- Python docstrings: the `docstrings` rule (code API comments, not user manuals).

## Additional resources

- [provenance-map.md](reference/provenance-map.md) — tag index to sibling references
