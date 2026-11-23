# Private distribution - gaps and decisions

Each decision holds for the whole work package. Each open question has a default that applies when nobody answers.

## Decided

| ID | Decision | Reason | Chapters affected |
| --- | --- | --- | --- |
| D1 | The repository `chief` is private. It is public today. Change the visibility before the work package is pushed. | Private hosting keeps licensed third-party text in the repository. The package must not go public before the license review (O5). | Before C0, C10 |
| D2 | The new history starts fresh. The corporate commit history, author addresses and merge-request links stay in the corporate repository. | A rewritten history still carries the corporate content it changed. | C0 |
| D3 | Chapter branches and the loop branch stay local until C10. C10 squashes the loop branch into one commit. | Only the squashed commit reaches GitHub. Intermediate corporate history stays out. | C0 to C10 |
| D4 | The distribution, the import name and the command are all `chief`. The skill stays `chief-of-staff`. The agent stays `chapter-implementer`. The package is never published to PyPI, where `chief` belongs to another project. | Short names match the repository. The PyPI name is taken. | C1, C4 |
| D5 | The repository-local identity is `Vadim Schultz <vadim.schultz@me.com>`. The license is MIT. The global identity stays as it is. | Commits and package metadata show the personal identity. | C0, C4 |
| D6 | GitHub only. GitLab handling is removed. GitHub handling comes from the hand-installed skill and the Cursor rules on the workstation. | The distribution targets GitHub. | C6 |
| D7 | The `mcp` pack, the MCP snippet command, the MCP package and the corporate build environment file are deleted. The orchestration, git, quality, style, data and work-package packs stay. | The deleted parts hold corporate endpoints. The other packs are generic after the scrub. | C3, C5 |
| D8 | Local gates run for every chapter. One remote run happens, on the pull request into `main`. A tag starts only the release workflow. | Hosted minutes are limited on private repositories. The workflow trigger limits remote runs to the release pull request. | C7, C10 |
| D9 | The release pull request is chapter C10. The chief of staff runs it. It is the final gate. | The final gate runs once, outward, and only after the user confirms. | C10 |
| D10 | The leak gate has two layers. The repository layer holds generic names. The local layer holds corporate tokens in the file named by `CHIEF_LEAK_DENYLIST`, outside the repository. Chapters run the gate in ratchet mode. C9 and C10 run it in strict mode. This work package folder is the only exempt path. | Corporate tokens in a public-facing test file would publish them. | C2, C9 |
| D11 | `ci.sh` sets a hermetic tool environment: `UV_NO_CONFIG=1`, `PIP_CONFIG_FILE=/dev/null` and `NPM_CONFIG_USERCONFIG=/dev/null`. | The global settings on the workstation point at corporate package mirrors. | C2 |
| D12 | `bundle/sources.json` and its hash tests are deleted. The install snapshot records paths only. | The file records an import from a private Cursor directory that the public repository does not have. | C2, C3, C7 |
| D13 | `uv.lock` stays git-ignored. The corporate work package folders are not carried over. | The lock file points at corporate indexes. The old work packages hold corporate decisions. | C0, C4 |
| D14 | This work package folder names no corporate host, address, login or product. It is the only path the leak gate exempts. | The folder holds the plan, so it must pass the gate that the plan describes. | C2 |

## Open

| ID | Question | Owner | Blocks | Default if unanswered |
| --- | --- | --- | --- | --- |
| O1 | Do you hold the rights, or written approval, to publish code written in the corporate repository under the MIT license? The corporate license claims employer copyright. | you | C10 | C10 does not push. The chief stops before the push. |
| O2 | Which GitHub plan does the account use? Rulesets and secret scanning on private repositories need a paid plan. | you | C10 | Skip the ruleset. Rely on the pre-push leak gate and branch conventions. |
| O3 | Does `UV_NO_CONFIG=1` stop uv from reading the corporate configuration completely? | implementer, C2 | C2 | Also set the public index in `UV_DEFAULT_INDEX`. |
| O4 | Do the toolchain tests in `tests/ci` (rust, node, cmake) run on the hosted runner? | implementer, C7 | C7 | The remote unit matrix covers only the Python unit tests. |
| O5 | Which terms apply to third-party text in a public release? The text covers ASD-STE100, the Google documentation style, a data-systems book and a refactoring catalogue. | you | C8 | The README says that third-party text keeps its own terms. |
| O6 | Which orchestrator runs this work package? The hand-installed skill asks for a pull request and remote CI for each chapter. That conflicts with D3 and D8. | you | none | The bundled skill, which integrates chapters locally. |
| O7 | Which repository is upstream for the shared generic content after release? | you | none | Decide after the release. |
| O8 | The repository root has no `ci.sh` and no `tox.ini` until C0. The checker flags this. | chief of staff | C0 | Accept the flag until C0 completes. |
