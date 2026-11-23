---
name: work-package-create
description: Convert a plan file into work package files, or hand a missing plan to plan-first mode of chief-of-staff.
---

# Work package create

Convert a plan file into a work package. Follow the `technical-writing` skill as the prose standard for every file.

## Convert a plan file

Read the plan file at the path that the dispatch gives. Plan files can live at any path.

Draft the chapter files in the parallel phases below. Draft every other file from its template:

- [architecture.md](templates/architecture.md) becomes `00-architecture.md`.
- [rollout.md](templates/rollout.md) becomes `01-rollout.md`.
- [gaps-and-decisions.md](templates/gaps-and-decisions.md) becomes `gaps-and-decisions.md`.
- [chapters-readme.md](templates/chapters-readme.md) becomes `chapters/README.md`.
- [run-ledger.md](templates/run-ledger.md) becomes `run-ledger.md`.
- [chapter.md](templates/chapter.md) becomes one file in `chapters/` for each chapter.
- [release-chapter.md](templates/release-chapter.md) becomes the release chapter, once, when the plan ends in a release pull request. It runs under `execution: chief-of-staff`.

Keep every section heading that a template lists.
Write only work package files into the work package folder.
Return a summary of the written files to the dispatch.
Do not run any chapter.
Do not wait for confirmation. The dispatch asks the user for it.

## No plan file

If no plan file exists, ask the user for a feature description.
Write no file in this branch.
Hand the feature description to the plan-first mode of the `chief-of-staff` skill.
Do not draft the plan in this skill.

## Parallel phases

Phase A drafts the chapter files in parallel, with one sub-agent for each chapter.
Each Phase A sub-agent uses the `generalPurpose` sub-agent type.
Each Phase A sub-agent owns one chapter draft file and writes no other file.
Start Phase B after every Phase A sub-agent finishes.
Phase B reviews the chapter drafts with one `generalPurpose` sub-agent.
Phase B owns no file and must not edit a draft.
Phase B returns its review notes, and this skill applies them to the drafts.
