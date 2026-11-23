---
name: Chapter C5 - Scrub bundled reference text
overview: "Remove the corporate login, the product names and the internal examples from the bundled reference text. Keep the third-party text."
id: C5
depends_on: ["C2"]
touches: ["src/chief/bundle/packs/quality/**", "src/chief/bundle/packs/style/**", "src/chief/bundle/packs/data/**"]
execution: chapter-implementer
isProject: false
---

# C5 - Scrub bundled reference text

**Depends on:** C2 · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [../01-rollout.md](../01-rollout.md)

## Goal

After this chapter, the bundled reference text names no corporate login, no product and no internal example. The third-party text keeps its rules and its examples of the rules.

## Read first

- [00-architecture.md](../00-architecture.md): read invariants I1 and I8.
- [../gaps-and-decisions.md](../gaps-and-decisions.md): read D1, D7 and D14, and open item O5.
- [../01-rollout.md](../01-rollout.md): read "Per-chapter gate".

## Coordination scope

**Add:**

- None.

**Edit:**

- The `generated:` front matter in ten reference files. Replace the corporate login with `human:vadim-schultz`. The files are:
  - `data/skills/designing-data-systems/reference/`: `local-stack.md`, `rules-data.md`, `rules-reads-ops.md`, `rules-writes.md`.
  - `quality/skills/refactoring/reference/`: `language-notes.md`, `refactorings.md`, `smells.md`.
  - `style/skills/`: `asd-ste100/reference/reference.md`, `google-docguide/reference/reference.md`, `technical-writing/reference/provenance-map.md`.
- `quality/rules/code-structure.md`: the example block near line 81. Replace the corporate domain names with neutral names.
- `quality/rules/refactor-step.md`: the checklist items near lines 42 and 50. Replace the domain names with neutral names.
- `style/skills/google-docguide/SKILL.md`: the example heading and text near lines 51 and 61. Use a neutral example.
- `data/skills/designing-data-systems/reference/local-stack.md`: the rows near lines 26 and 27. Use neutral wording.
- `data/skills/designing-data-systems/reference/rules-data.md` near line 26, and `rules-reads-ops.md` near line 63. Use neutral wording.
- `data/skills/designing-data-systems/SKILL.md`: the description on line 3. State that the stack is an example.

**Do not edit:**

- The rule content of the third-party texts. Only the examples change (D1, O5).
- The orchestration, git and work-package packs. C6 owns their host text.

## Work items

1. **Front matter.**
   - **Red:** Add `test_reference_front_matter_uses_public_author`. It checks that each `generated:` line names `human:vadim-schultz`. Add `test_reference_files_name_no_other_author`. It fails on any other name. Both fail now.
   - **Green:** Replace the value in the ten files.
   - **Refactor:** None expected. Record "no change needed" if so.

2. **Examples.**
   - **Red:** Add `test_bundled_examples_use_neutral_names`. It reads the denylist and fails on any listed domain name in the bundle. It fails now.
   - **Green:** Replace each example with a neutral one. Keep the structure of the example, so that it still shows the rule.
   - **Refactor:** Check that each replaced example still illustrates the rule it sits under. Record each change.

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| Front matter | `test_reference_front_matter_uses_public_author` | `test_reference_files_name_no_other_author` |
| Examples | `test_bundled_examples_use_neutral_names` | `test_example_scrub_keeps_third_party_rules` checks that the rule headings of the style texts remain |

## Review gate

- Check that every third-party rule heading still exists. For example, the ASD-STE100 headings `[ste:1.1]` and `[ste:4.1]` remain.
- Check that no example names a product or a domain from the denylist.
- Check that the rule files still read the same as before, apart from the replaced examples.

## Out of scope

- Host text in the git, orchestration and work-package packs. C6 owns it.
- The license review of the third-party text. Open item O5 owns it.

## Verification

```bash
# Run from the repository root.
./ci.sh unit
CHIEF_LEAK_STRICT=0 tox -e test-pytest -- tests/test_no_leaks.py
```

Expected: the unit tests pass. The leak ratchet reports fewer hits than the baseline in the scrubbed files.

## Refactor report

_To be filled by the implementer before the chapter commit. List each example that changed._

## Git workflow

- Check out the loop branch: `git checkout feat/private-distribution`.
- Create the chapter branch: `git checkout -b feat/private-distribution-c05-bundle-scrub`.
- Commit the red tests first, with the type `test`.
- Commit the scrub with the type `docs`. Use the subject `docs(bundle): replace corporate examples with neutral ones`.
- Run `./ci.sh all` before the hand-off.
- Do not push. The chief merges the chapter branch into the loop branch with `git merge --no-ff`.
