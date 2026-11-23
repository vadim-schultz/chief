# <WORK PACKAGE TITLE> - rollout

<ONE SENTENCE: HOW THE CHAPTERS IN THIS WORK PACKAGE ARE SCHEDULED AND INTEGRATED>

## Scheduling matrix

| ID | Chapter | Depends on | Batch | Touches |
| --- | --- | --- | ---: | --- |
| <CHAPTER ID> | <CHAPTER TITLE> | <DEPENDENCY CHAPTER IDS> | <BATCH NUMBER> | <PATHS THE CHAPTER MAY CHANGE> |

Each batch holds chapters whose `Touches` paths do not overlap. <STATE THE DISJOINTNESS CHECK FOR EACH BATCH>.

## Parallel batches

- Batch <BATCH NUMBER>: <CHAPTER IDS>. <WHY THE PATHS IN THIS BATCH DO NOT OVERLAP>.

## Integration order

1. <CHAPTER ID> - <CHAPTER TITLE>

## Critical path

<CHAPTER ID> -> <CHAPTER ID> -> <CHAPTER ID>

## Per-chapter gate

A chapter passes the gate when all of the following are true:

1. <GATE ITEM: RED TESTS COMMITTED AND FAILING FOR THE RIGHT REASON>
2. <GATE ITEM: VERIFICATION COMMANDS PASS ON THE CHAPTER BRANCH>
3. <GATE ITEM: LOCAL GATE PASSES ON THE CHAPTER BRANCH, WITH THE LOOP BRANCH MERGED IN>
4. <GATE ITEM: REFACTOR REPORT IS FILLED IN>
5. <GATE ITEM: THE CHIEF OF STAFF MERGES THE CHAPTER BRANCH INTO THE LOOP BRANCH WITH --no-ff, AND THE LOCAL GATE PASSES ON THE LOOP BRANCH>

Chapters do not push and get no remote CI. The release chapter, <RELEASE CHAPTER ID>, runs remote CI once, on the pull request into <RELEASE BRANCH>.

## Final gate

<STATE WHAT MUST BE TRUE OF THE LOOP BRANCH BEFORE THE RELEASE PULL REQUEST IS OPENED>

The release chapter, <RELEASE CHAPTER ID>, runs this gate once. The chief of staff executes it and no implementer does. It runs the local gate on the loop branch head, opens one pull request from the loop branch into <RELEASE BRANCH>, watches the remote checks and tags the release only after they pass.
