# chief

> Chief of Staff Agent Skills

- [**Repository**](https://github.com/vadim-schultz/chief)
- [**Issues**](https://github.com/vadim-schultz/chief/issues)

chief installs agent skills, agents and rules into the folders of your AI coding tools.

## Supported IDEs

The installer writes files for these tools:

| Tool | Target name | Installs into | Installs |
| --- | --- | --- | --- |
| Cursor | `cursor` | `~/.cursor` | skills, agents, and rules |
| Claude Code | `claude` | `~/.claude` | skills, agents, and rules |
| OpenCode | `opencode` | `$XDG_CONFIG_HOME/opencode`, or `~/.config/opencode` | skills and agents |

The bundled `ci-harness` skill detects these language profiles: `python`, `typescript`, `rust`, and `c-cpp`.
Go is not in this release.

## Installation

You need Python 3.10 or later, and uv.
The repository is private. Your git setup must sign in to GitHub with an account that can read it.
If you use the GitHub CLI, run `gh auth setup-git` once.

If your uv settings name another index, set `UV_DEFAULT_INDEX` to `https://pypi.org/simple` before you install.

### Install the command

Install the tagged release with uv:

```sh
uv tool install git+https://github.com/vadim-schultz/chief@v0.1.0
```

The tag `v0.1.0` is created at the release. Until then, this command fails.

## Quick start

The examples use `cursor`. For Claude Code, use `claude`. For OpenCode, use `opencode`.

1. Install the command. See the Installation section.
2. Run `chief list`. The output shows the packs and the folder of each target.
3. Run `chief install --target cursor --dry-run`. Nothing is written.
4. Run `chief install --target cursor`.
5. Run `chief doctor`. It reports any file that differs from its install record.

To install for every tool, run `chief install --target all`.

## Usage

Run `chief --help` to display the help message.
Run `chief -V` to display the version number. The long form is `--version`.

### Commands

| Command | Purpose | Options |
| --- | --- | --- |
| `chief list [PACK]` | Show the packs and the folder of each target. | `PACK` shows one pack. |
| `chief install` | Install the packs for one target, or for every target. | `--target` (required): `cursor`, `claude`, `opencode` or `all`. `--dry-run`: print the plan and write nothing. `--force`: overwrite edited files that the manifest tracks. |
| `chief uninstall` | Remove the files that the manifest tracks for one target. | `--target` (required): `cursor`, `claude`, `opencode` or `all`. |
| `chief doctor` | Report installed files that differ from their install record. It reports only. | `--target`: `cursor`, `claude`, `opencode` or `all`. The default is `all`. |
| `chief export` | Write the rendered files of one target into a folder. | `--target` (required): `cursor`, `claude`, `opencode` or `all`. `--output` (required): the folder to write. |

Each `-v` flag increases the log level, and each `-q` flag reduces it.
The long forms are `--verbose` and `--quiet`. The default level is `WARNING`.
For example, `chief -vv` sets the level to `DEBUG`.
The command `chief -qq` sets the level to `CRITICAL`.

### Remove the files

To remove the files of one target, run `chief uninstall --target <name>`.
The command removes only the files and the managed block that the installer wrote for that target.
It keeps each file that you edited after the install.

### Export

To install on a machine without Python, export the files on a machine with Python.
On a machine with Python, run `chief export --target <name> --output <dir>`.
Use an output folder that does not exist yet, or an empty folder.
Copy each exported file to the same relative path under the target folder on the destination machine.
The `list` command shows the target folder for each target.
The OpenCode folder is under `XDG_CONFIG_HOME`, or under `~/.config` when that variable is unset.

The export command never overwrites a file.
It refuses an output path that is a file, and it refuses a folder that holds any entry.
With `--target all`, the check applies to the subfolder of each target.
A refusal writes nothing, and the command exits with code 1.
A missing or empty folder is accepted.

### Exit codes

| Code | Meaning |
| --- | --- |
| 0 | The command finished, or it printed the help or the version. |
| 1 | An `install` or `uninstall` step was refused. `doctor` found drift. `export` refused its output folder. The user aborted the run, or a runtime error occurred. |
| 2 | A usage error occurred. Causes: an unknown option or value, an unknown pack name, or no command. |

### Install state

The installer keeps one manifest file for each target.
The manifest records each file that the installer wrote, so that `uninstall` and `doctor` can check it.
The manifest files are in `$XDG_STATE_HOME/chief/`, or in `~/.local/state/chief/` when `XDG_STATE_HOME` is unset.
Each manifest file is named `<target>.manifest.json`.

Do not change `XDG_STATE_HOME` after an install.
A missing manifest counts as empty.
After a change, `uninstall` and `doctor` cannot see the files of the earlier install.
To move the state, move the `chief` folder, then set `XDG_STATE_HOME` to its new parent folder.

Do not run two install or uninstall commands at the same time.
The tool does not guard against concurrent runs.

### API

The package exposes a Python API. Import it with `import chief`.

## Normal workflow

The loop branch holds the integrated chapters of one work package.
Give the chief-of-staff skill one of these arguments:

| Argument | What happens |
| --- | --- |
| A work package folder | The skill checks the package with `work-package-check`, then runs its chapters. |
| A plan file | The skill converts the plan into a work package and shows a summary. It runs no chapter until you confirm. |
| No argument | The skill interviews you, drafts a plan, and waits until you accept it. It writes nothing before that. |

For a plan file, the normal workflow has these steps:

1. Give the chief-of-staff skill the plan file.
2. Read the summary.
3. Confirm the work package when it is correct.
4. Give the work package folder to the chief-of-staff skill.
5. The skill runs each ready chapter in its own worktree.
6. Chapters run in parallel when their dependencies allow.
7. The skill merges each chapter that passes the local gate into the loop branch on your machine.
8. Confirm the release. The skill does not open the pull request before you confirm.
9. The skill opens one pull request into `main`.
10. Remote CI runs once, on that pull request.

## Security

The repository is private. Only users with read access can see it.
To report a security problem, contact the repository owner, Vadim Schultz, through GitHub.

## Contributing

1. Create a feature branch from `main`.
2. Add a test for each behavior change.
3. Make the change. Keep the tests green.
4. Update the README and the docs when behavior changes.
5. Run `./ci.sh all`. Fix each failure.
6. Commit with a [Conventional Commits](https://www.conventionalcommits.org/) message.
7. Open a pull request into `main`.

## Local gates, remote CI at the release pull request

Every chapter passes the local gate on its own branch before it merges into the loop branch.
The local gate is `./ci.sh all`. Run it from the repository root.
Remote CI does not run for each chapter.
Remote CI runs once. It runs on the pull request into `main`.
A tag starts only the release workflow.
The release is the tag `v0.1.0`. The tag is created after the pull request into `main` merges.

Each clone enables the pre-push leak gate once. Run this command in the clone:

```sh
git config core.hooksPath .githooks
```

The pre-push hook runs the leak gate before each push. The hook needs `tox`.

## License

The chief is released under the [MIT license](https://github.com/vadim-schultz/chief/blob/main/LICENSE).
Bundled third-party text keeps its own terms.
