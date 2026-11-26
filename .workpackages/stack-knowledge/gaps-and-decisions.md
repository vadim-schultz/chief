# Stack knowledge and VS Code target - gaps and decisions

Each decision holds for the whole work package. Each open question has a default that applies when nobody answers.

## Decided

| ID | Decision | Reason | Chapters affected |
| --- | --- | --- | --- |
| D1 | MCP guidance lives in skills. Each service skill names its server, endpoint, auth and scope. The shared `mcp-setup` skill shows each tool's configuration layout. The user adds the configuration. The installer never writes it. | The installer refuses MCP configuration files by design (I1). MCP servers run code under the user's credentials, so a silent install needs its own review. | C1, C2a to C2e, C3 |
| D2 | The `vscode` target installs skills to `~/.copilot/skills` and agents to `~/.copilot/agents`. It joins `--target all`. The `claude` target is unchanged. | The official VS Code documentation names `~/.copilot/skills/` as the personal skill folder. Claude Code in VS Code already reads `~/.claude`, so changing `claude` would break a working setup. | C1, C4 |
| D3 | `vscode` writes rules only when the official docs confirm a personal instructions folder. Otherwise it skips rules, and the plan output names each skipped file. | Sources disagree on the personal instructions location. A wrong guess writes files that VS Code never reads. | C1, C4 |
| D4 | No skill for the public-data sources (GovData, PVOG, LeiKa, FIM, OpenPLZ). | The sibling project keeps its own skills for these sources. | none |
| D5 | No skill for Flutter or Firebase. | Neither is built in the sibling project yet. | none |
| D6 | No runbooks or budget values from the sibling project in the bundle. Skills hold generic service rules only. | Project runbooks hold private values, and they change often. | C2b to C2e |
| D7 | A fact that the research could not confirm ships as `MCP: none verified` or `none verified`, with the date of the check. Nothing claims a server exists without a vendor page. | Search snippets are not vendor sources. | C2b to C2e |
| D8 | Context7 is named as an optional third-party docs fallback in `docs-lookup`. Chief never installs it. | Queries reach a third party. The user chooses whether to use it. | C2a |
| D9 | The sibling project's name appears in no file under `src/chief/` and in no stack pack. The same holds for this work package folder. The name is never written out in a test file. A test builds it from parts. | The user's direction: the name is a leak in the skills and the package. Chapter C0 removes the one shipped occurrence. Chapter C2a and chapter C3 extend the scan to the stack packs. | C0, C2a, C3 |
| D10 | The release tag is `v0.2.0`, not `v0.1.0`. The changelog heading `0.1.0 (not yet released)` becomes `0.2.0 (not yet released)`. The README install command and release text name `v0.2.0`. | The user's direction. No `0.1.0` tag is made, so the unreleased changes ship as `0.2.0`. | C4, C5 |
| D11 | The work package folder stays uncommitted until execution starts. The chief of staff commits it on the loop branch when execution starts. | The user's direction. | Start of execution |
| D13 | Each chapter that adds installed paths regenerates `tests/fixtures/install_snapshot.json` on its own branch, after it merges the loop branch. The chapter lists the file in its touches. Four-target install into an empty HOME, as C1 did. Those chapters integrate one at a time, so the file has one merge at a time. | The snapshot test is a gate (I7). A new pack adds installed paths, so it fails on the loop branch without a regenerated snapshot. C2a's gate failed on 12 new paths. | C2a, C2b, C2c, C2d, C2e, C3 |
| D12 | `src/chief/installation/installer.py` joins chapter C1's touches. The install command prints one line per skipped rule (C1, green step 4). Only the installer passes the skipped names from the tree to the command. | D3 and the green step require the line. The plan omitted the file that carries it. No other chapter touches the file, so batch 1 stays disjoint. | C1 |

## Open

| ID | Question | Owner | Blocks | Default if unanswered |
| --- | --- | --- | --- | --- |
| O5 | Exact Supabase `llms.txt` URL and hosted MCP endpoint. The search gave two URLs for the index and no endpoint. | chapter-implementer, C2c | C2c | Name the docs page that lists the endpoint, not a guessed URL. |
| O6 | Browser Run MCP status. The vendor README calls the project a work in progress. | chapter-implementer, C2b | C2b | Record the server as `MCP: official` with the date, and add a line that the tool list may change. |
| O7 | Microsoft Learn MCP endpoint `https://learn.microsoft.com/api/mcp`. It comes from search snippets. | chapter-implementer, C2c | C2c | Cite the Microsoft Learn MCP developer reference, not a snippet. |
