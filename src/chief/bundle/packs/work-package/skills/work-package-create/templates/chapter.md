---
name: Chapter <CHAPTER ID> - <CHAPTER TITLE>
overview: "<ONE SENTENCE: WHAT THE CHAPTER DELIVERS>"
id: <CHAPTER ID>
depends_on: [<DEPENDENCY CHAPTER IDS>]
touches: [<PATH OF EACH FILE THE CHAPTER MAY CHANGE>]
execution: <EXECUTION MODE>
isProject: false
---

# <CHAPTER ID> - <CHAPTER TITLE>

**Depends on:** <DEPENDENCY CHAPTER IDS> · **Architecture:** <ARCHITECTURE FILE> · **Rollout:** <ROLLOUT FILE>

## Goal

<STATE WHAT IS TRUE AFTER THE CHAPTER IS DONE, IN ONE OR TWO SENTENCES>

## Read first

- <ARCHITECTURE FILE>: <SECTIONS TO READ>. If this chapter and the architecture disagree, the architecture wins.
- <ROLLOUT FILE>: <SECTIONS TO READ>.

## Coordination scope

**Add:**

- <PATH OF EACH NEW FILE>

**Edit:**

- <PATH OF EACH EDITED FILE, OR None>

**Do not edit:**

- <PATH OF EACH FILE OWNED BY ANOTHER CHAPTER, AND THE CHAPTER THAT OWNS IT>

## Work items

<ORDERED STEPS. EACH STEP STATES ITS RED TEST, ITS GREEN CHANGE AND ITS REFACTOR CANDIDATES.>

## Tests or document checks

| Check | Happy path | Negative path |
| --- | --- | --- |
| <CHECK NAME> | <HAPPY PATH TEST NAME> | <NEGATIVE PATH TEST NAME> |

## Review gate

<CHECKS THAT A REVIEWER RUNS BEFORE THE CHAPTER IS MERGED>

## Out of scope

- <WORK THAT ANOTHER CHAPTER OWNS, AND THE CHAPTER THAT OWNS IT>

## Verification

```bash
# Run from the repository root.
<VERIFICATION COMMAND>
```

Expected: <EXPECTED RESULT OF EACH COMMAND>.

## Refactor report

_<WHAT THE REFACTOR PASS CHANGED, OR "no refactor needed" WITH THE REASON>_

## Git workflow

- Check out the loop branch with `git checkout <LOOP BRANCH>`. Pull it only when it tracks an upstream.
- Create the chapter branch with `git checkout -b <CHAPTER BRANCH>`.
- Commit the red tests first, then the green change.
- Run the local gate on the chapter branch. It passes when it exits 0. The chief-of-staff git model defines it.
- Do not push, and do not open a pull request. Remote CI runs once, on the release pull request.
- The chief merges the chapter branch into the loop branch locally, with `git merge --no-ff`.
