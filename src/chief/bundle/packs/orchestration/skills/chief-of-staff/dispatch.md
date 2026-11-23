# Dispatch

The argument selects exactly one row below. Each row runs its own steps in order and writes nothing before the gate it names.

| Argument | Steps |
| --- | --- |
| `@<work-package>` | Check the package with `work-package-check`, then execute its chapters. |
| `@<plan-file>` | Convert the plan with `work-package-create`, show a summary, and stop for confirmation. Conversion writes the work package files only, and no chapter runs before confirmation. |
| No argument | Start plan-first mode. Interview the user for the feature description, draft a plan with `CreatePlan`, and let the user refine it in plan mode until it is accepted. The user may exit at any point. The skill writes nothing before the plan is accepted. |
| Unknown argument | The argument is neither a work package nor a plan file. Ask the user to clarify, and write nothing. |
