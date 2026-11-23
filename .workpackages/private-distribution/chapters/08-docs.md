---
name: Chapter C8 - Documentation
overview: "Describe the private, GitHub-only distribution in the README and the docs, in ASD-STE100 style. Start the changelog at 0.1.0."
id: C8
depends_on: ["C3", "C4", "C6", "C7"]
touches: ["README.md", "docs/*.md", "CHANGELOG.md", "tests/test_readme.py"]
execution: chapter-implementer
isProject: false
---

# C8 - Documentation

**Depends on:** C3, C4, C6, C7 · **Architecture:** [00-architecture.md](../00-architecture.md) · **Rollout:** [../01-rollout.md](../01-rollout.md)

## Goal

After this chapter, the README and the docs describe the private, GitHub-only distribution. They follow the technical-writing standard. The changelog starts at version 0.1.0.

## Read first

- [00-architecture.md](../00-architecture.md): read decisions A1 to A5.
- [../gaps-and-decisions.md](../gaps-and-decisions.md): read D1, D8 and open item O5.
- [../01-rollout.md](../01-rollout.md): read "Per-chapter gate".
- The `technical-writing` skill of the style pack. It is the prose standard for every file in this chapter.
- `tests/test_readme.py`: read the required headings, the command pattern and the style checks. Keep each check.

## Coordination scope

**Add:**

- None.

**Edit:**

- `README.md`: the header links, the purpose, the install steps, the quick start, the command table, the local gate section, the security section, the contributing section, the license line and the third-party note.
- `docs/*.md`: keep the thin includes. Fix any section that names a removed command.
- `CHANGELOG.md`: add the 0.1.0 entry.
- `tests/test_readme.py`: add the new tests. Keep the existing checks.

**Do not edit:**

- The bundled text. Chapters C5 to C7 own it.
- `pyproject.toml`. C4 owns it.

## Work items

1. **Red.**
   - Add `test_readme_names_git_url_install`. It checks that the install command uses `git+https://github.com/vadim-schultz/chief` with a tag.
   - Add `test_readme_has_no_mcp_or_package_index`. It checks that the README names no `mcp-snippet`, no "Package index" heading and no MCP term.
   - Both fail now. Commit them with the type `test`.

2. **README.**
   - **Green:** Write the README in ASD-STE100 style. Use short sentences. Put one instruction in each step. The README holds these sections:
     - Header links to the GitHub repository and its issues.
     - A one-sentence purpose.
     - Installation from the tagged git URL.
     - A quick start.
     - The command table, without `mcp-snippet`.
     - A section named "Local gates, remote CI at the release pull request". It states decision D8 in plain words.
     - A short `## Security` section. The repository is private, so it names the repository owner as the contact.
     - A `## Contributing` section.
     - The license line: MIT.
     - A note that bundled third-party text keeps its own terms (O5).
   - **Refactor:** Remove install text that repeats in `docs/installation.md`. Keep the thin include.

3. **Changelog.**
   - **Green:** Add the 0.1.0 entry. Name the private distribution, the commands and the GitHub host handling. Remove the entry that names the removed command.

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| README install | `test_readme_names_git_url_install` | `test_readme_has_no_mcp_or_package_index` |
| Existing checks | `test_readme_required_headings` | `test_readme_style_checks_pass` |

## Review gate

- Check every procedural sentence. It has no more than 20 words.
- Check that `git grep -n -i -E "mcp-snippet|package index" -- README.md docs` returns no output.
- Check that the docs build in strict mode.

## Out of scope

- The license review of third-party text. Open item O5 owns it.
- The repository settings. C10 owns them.

## Verification

```bash
# Run from the repository root.
tox -e test-pytest -- tests/test_readme.py
tox -e docs
```

Expected: the README tests pass. The docs build exits 0.

## Refactor report

_To be filled by the implementer before the chapter commit._

## Git workflow

- Check out the loop branch: `git checkout feat/private-distribution`.
- Create the chapter branch: `git checkout -b feat/private-distribution-c08-docs`.
- Commit the red tests first, with the type `test`.
- Commit the documentation with the type `docs`.
- Run `./ci.sh all` before the hand-off.
- Do not push. The chief merges the chapter branch into the loop branch with `git merge --no-ff`.
