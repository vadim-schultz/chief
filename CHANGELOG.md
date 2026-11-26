## Changelog

### 0.2.0 (not yet released)

#### Added

- The private, GitHub-only distribution of the `chief` package.
- The `list`, `install`, `uninstall`, `doctor` and `export` commands.
- GitHub host handling for pull requests and checks in the chief-of-staff workflow.
- Remote CI runs once, on the pull request into `main`. A tag starts only the release workflow.
- The `vscode` install target. It installs skills and agents into `~/.copilot`. It installs no rules, because the VS Code documentation names no personal folder for rules. `--target all` installs into four targets.
- The stack packs. Each pack adds skills for the services that a project uses. Each skill names the server or documentation index for its service:
  - `stack-docs`: `docs-lookup`, `mcp-setup`.
  - `stack-cloud`: `cloudflare`, `github-actions`, `render`, `uptimerobot`.
  - `stack-data-services`: `azure-translator`, `supabase`.
  - `stack-python`: `litestar`, `pydantic`, `sqlalchemy-alembic`.
  - `stack-web`: `chakra-ui`, `vite-react`.
