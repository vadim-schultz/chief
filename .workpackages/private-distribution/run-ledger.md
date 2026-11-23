# Private distribution - run ledger

Every chapter starts as `pending`. The chief moves a row to `running` when the implementer starts. Then the chief moves it to `done` or `blocked`. A `done` row records the local commit and the local merge. Nothing is pushed before C10.

**Loop branch:** `feat/private-distribution`
**Release branch:** `main`
**Rollout:** [01-rollout.md](01-rollout.md) · **Decisions:** [gaps-and-decisions.md](gaps-and-decisions.md) · **Chapters:** [chapters/README.md](chapters/README.md)

## Chapter status

| Chapter | Status | Commit | Pull request |
| --- | --- | --- | --- |
| C0 seed | done | a69e9bd, merged 6e7fd0f | not opened (local only) |
| C1 rename | done | 2e9bc71, 55d0259, merged 6fdd78c | not opened (local only) |
| C2 guards | done | ee4cdbe, e36f8ee, 0905685, 3dcd274, 18d0993, merged 5d349d2 | not opened (local only) |
| C3 corporate-code | done | 8f32b07, b7c1188, merged 24067a2 | not opened (local only) |
| C4 packaging | done | 7b1e34d, 3ebef16, 572a722, merged ec43c96 | not opened (local only) |
| C5 bundle-scrub | done | 1d497e0, 7216494, 5e10788, merged 847619e | not opened (local only) |
| C6 github-host | done | df92c20, 8fb9ac8, merged 203040e | not opened (local only) |
| C7 ci-policy | done | 9c5d4e7, 2c9a611, 362ad0b, fd22c07, f3f9011, merged 14d1b4d | not opened (local only) |
| C8 docs | done | d7da723, 37d2f13, f6c38b3, merged 992ffc5 | not opened (local only) |
| C9 final-sweep | done | 8a9a0ac, eb7736f, 40aaeee, 34f5ed5, ef6a636, 17ec8c0, merged 07f64f2 | not opened (local only) |
| C10 release-pr | running | - | not opened (opens at C10) |
| Final gate | running | - | not opened (opens at C10) |

**Notes**

- C0: the user waived the denylist review check for the seed. 25 seed files carry denylist terms and are scrubbed in C3 to C8.
- C1: the implementer added `tests/test_package_name.py`, although the chapter named no new files. The negative test checks only the `package:` lines of the local denylist. tox does not pass `CHIEF_LEAK_DENYLIST`, so the test falls back to the default path.
- C2: the leak baseline lives outside the repo at `~/.config/chief/leak-baseline.json`. It was written once, after the C2 green commit. Later chapters must not regenerate it. The implementer added `tests/test_hermetic_env.py` and removed a `sources.json` check from `tests/test_okf_reference.py`, which the chapter did not list.
- Open for C4 or C9: strict mode and the path variables do not reach the tox tests. `tox.ini` needs passenv for them. Until then, `CHIEF_LEAK_STRICT=1 ./ci.sh` runs in ratchet mode.
- C3: the corporate build-environment file and its references in the orchestration skill and the implementer agent are removed (D7). Architecture invariant I8 reserves skill text changes for C5 and C6. The chapter names these removals, so the chief accepted them. `README.md` and `CHANGELOG.md` still describe the removed `mcp-snippet` command, and C8 owns them. Two out-of-scope tests use `mcp` as a fixture name, and they pass.
- C4: `LICENSE` is now the MIT text, with copyright holder Vadim Schultz and year 2026. The chief set these values per D5. O1 still gates the C10 push. `tox.ini` passenv now passes the three leak variables, which closes the C2 open item for passenv. Strict mode is available to the tox tests from C4 on.
- C5: the examples are neutral and the front matter names the public author. The example test checks both the denylist and the repository-layer product names, so it is red before the scrub. Third-party rule headings are unchanged. The observed leak hits for C6 are the host text in the git, orchestration and work-package packs. One repository-layer term sits in five of those files, and C6 must remove it. Outside the bundle, the root CI config, README.md and 11 test or fixture files are left for C7 to C9.
- C6: the bundle has GitHub-only host text, and no forge term remains in `src/chief/bundle`. Three test names are reworded so they do not add hits to frozen-baseline test files; the baseline is not refreshed. The SKILL.md description no longer names an internal product, which was not a denylist term. Owner decision pending: add that term to the local denylist.
- C7: one remote workflow runs on the pull request into `main` and on tags. Actions are pinned to commit SHAs, and actionlint is clean. The git rule's local-first wording was changed under the chief's scope extension. O4 is answered: `tests/ci` needs only uv and tox, and it runs once, in the gate job. The unit matrix runs the Python unit tests, which is the O4 default.
- Expected hosted failures until C8 and C9: `tests/test_no_leaks.py::test_tree_stays_within_baseline` fails in the gate job, both unit jobs, and the release job. The runner has no denylist and no baseline, and one repository-layer hit remains in `README.md`, which C8 owns. Not verified remotely at C7: setup-uv on the PATH, the Python 3.10 and 3.14 installs, and setuptools-scm on a shallow tag checkout. C10 must check these on the first remote run.
- Each clone needs `git config core.hooksPath .githooks` before the pre-push leak gate runs. C8 documents it.
- C8: the README and the changelog describe the private, GitHub-only distribution. The README holds no repository-layer hit, so the ratchet passes at 0. The baseline still records 9 for README.md, and it is frozen, so the chief does not regenerate it. The docs build passes in strict mode. The changelog heading reads "0.1.0 (not yet released)". C10 sets the date and cuts the tag.
- C9: the strict leak gate passes over the tree (179 files), the history (53 commits), the sdist (133 files) and the wheel (101 files), with no hit. Ratchet: 287 passed, 1 skipped (the strict-only test). Release default: `CI_RELEASE_RUN=1` selects strict mode, and the release workflow leaves it unset. The final strict gate therefore runs locally at C10.
- C9 identity check: the rollout gate, `git log main..HEAD`, shows only the personal identity. The chapter's literal whole-history check fails, because two commits inherited from `main` carry a GitHub committer and an alternate author name on the personal address. No corporate address appears. `main` is not rewritten. The chief accepts this, and it is recorded here.
- Open for C7 (and the scope it takes on): per-chapter pull-request wording still conflicts with D3 and D8 in `git-model.md`, `host-workflow.md`, `chapter-implementer.md`, `SKILL.md`, the chapter and run-ledger templates, and `packs/git/rules/git-workflow.md`. The git rule is not in C7's touch list. The chief extends C7's scope to it, so the bundle reads consistently.
- Hosted CI: the first remote run is at C10. It is expected to pass after the C8 and C9 scrub, and that is not verified. The local denylist layer passes unchecked on the runner, since the runner has no denylist.

## Release gate (C10)

- **O1, answered in writing by the user:** the code is privately developed and distributed to colleagues as a service, and the user can publish it under MIT.
- **O2, answered by the user:** the account is on a free GitHub plan. The ruleset is skipped: "skipped: plan".
- **C4 license values, confirmed by the user:** holder Vadim Schultz, year 2026.
- **Identity (C9), acknowledged by the user:** the rollout gate `main..HEAD` passes. Two commits on `main` keep their inherited identities.
- **Strict run, acknowledged by the user:** the strict leak gate runs locally at C10. The release workflow leaves strict mode unset.
- **"Redtape":** the user says the term is public and not internal. It is not added to the denylist. The word is restored in the orchestration skill description.
- **Tag run:** the release workflow builds and attaches the distributions only. It runs no CI gate, as the user chose and as C10 describes. The gate runs locally before the release pull request merges.
- **Push and pull request:** the user authorized the push of the squashed branch and the pull request into `main`. The merge and the tag each need a separate go-ahead.
- **History:** the loop branch is squashed onto `main` with `git reset --soft main`, from `06f7b4a`. The pre-squash head is recoverable from the reflog.
- **Gate on the final squashed tree:** `./ci.sh all` exits 0 with 288 passed and 1 skipped. `CHIEF_LEAK_STRICT=1 tox -e test-pytest -- tests/test_no_leaks.py` exits 0 with 289 passed. The final commit SHA is in the pull request.
