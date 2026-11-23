---
name: asd-ste100
description: Applies ASD-STE100 Issue 9 Part 1 writing rules for controlled technical English in procedures, safety text, and user-facing documentation. Use when the user asks for STE, simplified technical English, aerospace-style procedures, or plain safe instructions.
disable-model-invocation: true
---

# ASD-STE100 (Part 1)

Paraphrased **Part 1 — Writing rules** from [ASD-STE100 Issue 9](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf). **Do not** paste Part 2 (controlled dictionary) into outputs — use the official dictionary and your company glossary.

## When to use

- Procedures, work instructions, maintenance steps
- Safety instructions (warning / caution)
- User-facing technical English that must stay unambiguous
- Rewriting jargon-heavy sentences into controlled English

Not for: repo Markdown layout (use `google-docguide`), or casual chat/plan prose unless the user requests STE.

## Dictionary workflow (mandatory)

1. Prefer words **approved** in ASD-STE100 Part 2 dictionary with the **correct part of speech** and **approved meaning**.
2. Use **technical nouns** and **technical verbs** from your company glossary when not in the dictionary.
3. If a word is not approved, use dictionary **alternatives** or **rebuild the sentence** (Rule 9.1).
4. Keep American English spelling unless an official directive says otherwise (Rule 1.14).

## Quick rules by section

| Section | Focus |
| --- | --- |
| 1 Words | Approved dictionary words; technical nouns/verbs; consistent terms |
| 2 Multi-word nouns | Max three words; write long terms in full |
| 3 Verbs | Approved forms; active voice; no phrasal clutter |
| 4 Sentences | Short, clear; lists; articles where needed |
| 5 Procedural | ≤20 words/sentence; imperative; one instruction per sentence |
| 6 Descriptive | Gradual detail; ≤25 words/sentence; focused paragraphs |
| 7 Safety | Risk label; command/condition first; explain hazard |
| 8 Punctuation | No semicolons; hyphenation; word-count rules |
| 9 Practices | Consistent terminology; no phrasal verbs; rewrite when needed |

Full rule list with examples: [reference.md](reference/reference.md).

## Example rewrite

**Non-STE:** Test the system for leaks.

**STE:** Do the leak test of the system.

(or: Do a test for leaks in the system.)

## Additional resources

- [reference.md](reference/reference.md) — Part 1 rules with `[ste:x.y]` ids
- Official PDF: https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf
- Sibling: `technical-writing` — merged rules with provenance tags
