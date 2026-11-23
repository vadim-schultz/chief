---
name: ci-harness
description: Detects a repository's language profile (python, typescript, rust or c-cpp) from its marker files and provides a ci.sh template for each profile that runs the five harness stages in order.
---

# CI harness

Use this skill to find the language profile of a repository and to get the `ci.sh` template for that profile. Each template runs five stages in this order: format, lint, types, unit, build.

## Profiles

| Profile | Marker files (every file of one set must exist in the repository root) | Template |
| --- | --- | --- |
| `python` | `pyproject.toml` | [python](templates/python/ci.sh) |
| `typescript` | `package.json` and `tsconfig.json` | [typescript](templates/typescript/ci.sh) |
| `rust` | `Cargo.toml` | [rust](templates/rust/ci.sh) |
| `c-cpp` | `CMakeLists.txt`, or else `Makefile` | [c-cpp](templates/c-cpp/ci.sh) |

Go is not a profile in version 1.

Detection reads only the files in the root directory. Run [scripts/detect_profile.py](scripts/detect_profile.py) with the repository root. The script uses the standard library only.

- One profile matches: the script prints its name and exits 0.
- No profile matches: the script prints `no profile` and exits 1.
- Several profiles match: the script prints `ambiguous profile` with the names and exits 1. Stop and ask the user which profile to use. Do not pick one.

A profile is a default. A repository can override a profile. This skill does not define the override.

## Stages

Each template runs the stages in this order and stops at the first failing stage.

1. **format**: checks formatting and changes no file.
2. **lint**: runs static analysis.
3. **types**: compiles or type checks, with warnings treated as errors.
4. **unit**: runs the unit tests.
5. **build**: builds a release or a package.

The template prints `ci: stage <name>` before each stage. When a stage fails, it prints `ci: stage <name> failed` and exits nonzero. It exits 0 only when all five stages pass.

Before each stage, the template checks that the stage tool is on `PATH`. When the tool is found, it prints `ci: tool <name> found`. When the tool is missing, it prints `ci: missing tool <name>` and exits nonzero. A stage never passes by skipping.

The templates read mirror settings from the environment. They name no host.

## Red rule

Write each failing test before the code that it covers.

- In interpreted languages, a red test fails an assertion. Create each missing unit as a stub that returns a placeholder value, such as an empty list, `None` or an empty string. A stub that raises an exception does not qualify, because the test stops before its assertion.
- In compiled languages, a red test must compile before it fails. A compile or link error is not a red for the right reason. A stub that returns a placeholder value is the accepted red state.

## Blocked toolchain

When a stage tool is missing, the work package is blocked. Report the exact `ci: missing tool <name>` line. Do not mark a test as skipped, and do not make a stage pass without its tool.
