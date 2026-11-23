---
name: work-package-check
description: Check a work package with the check script and report every finding.
---

# Work package check

The skill always reports the findings and never stops on a normalised finding. Follow the `technical-writing` skill as the prose standard for every message.

## Run the script

Run the check script with the work package folder and the repository root:

```bash
python3 {{skill_dir:work-package-check}}/scripts/check_work_package.py <work-package-folder> --repo-root <repository-root>
```

The script uses only the Python standard library.
Do not install any package before the run.

## Show findings

Read the JSON report from stdout. The `findings` list holds one object for each finding.
Show every finding with its severity, rule, path and message.
Return the full report to the chief-of-staff dispatch, which decides the next step.

## Show normalisations

The script fixes some findings in place and marks each fix as `normalised`.
Show each `normalised` finding as a change that the script made.
Leave each normalised change in place.

## Ask about flag findings

Ask the user one question for each `flag` finding, in the same reply as the report.
Ask no question for a `normalised` finding.

## Handle tool failure

If stdout holds no JSON report, report the tool failure with its error output.
Do not mark the work package as checked.
Do not treat a tool failure as a finding or as a pass.
