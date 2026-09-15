# PROGRESS — unified SPM candidate (max/spm-unified-candidate-20260914)

## State
Base: `upstream/main` @ `2cc6f045ab1f389bc781ffd9f5e874055b3c0a3d` (version 2.1.0).
Worktree: `/Users/maxghenis/spm-rebuild-20260908/worktrees/policyengine-us-spm-unified-20260914`.

Verified PR heads (`gh pr view <n> --json headRefOid`, 2026-09-14):
| PR | head | merge-base with main |
|---|---|---|
| #9466 | `9f9510b735b3b9b2e375854d66fd315202e31d35` | 2cc6f045ab |
| #9463 | `d8cbd4b7a0b292beafad37cfc72813e1d710fc3e` (lane 20260914-144927 still RUNNING — re-verify before push) | 2cc6f045ab |
| #9448 | `8f74a5152d1e52c33bd7a7cba6340346bd7fe004` | 2ba7daa30e |
| #9464 | `cafcd9443df7f638a5ad547a92c6e0bcfd784fbb` | 4d34e3d1ab |
| #9462 | `47e94fa491bbf65ae4b6bd5667f054445b26de36` | deliberately excluded (Microcosm #925) |

## Done
- [x] Read reconciliation memo, FINAL-REPORT, EXPANDED-REVIEW, FINDINGS-RECOVERY
- [x] Worktree + branch from `upstream/main`
- [x] Step 2a: #9466 cherry-picked as-is (`c5d8abfb44`)
- [x] Step 2b: #9463 applied (`a6f1e8da14`)
- [x] Step 2c: #9448 reduced (`d1251c47cb`)
- [x] Step 2d: #9464 reduced (`c4209228d7`)
- [x] Step 3: R1/R2 already satisfied by #9448's head; R8 + citations (`28e7ac9422`);
      R9 satisfied by #9448's CPUC Cases 4/5 + `test_cpuc_housing_exclusion_effective_date`
- [x] Lane 20260914-144927-spm-fix-isolation-202 finished; #9463 head re-verified UNCHANGED at d8cbd4b7

## Verified so far (exit codes)
| Suite | Result | Exit |
|---|---|---|
| `ruff format --check .` / `ruff check .` | 6444 files formatted, all checks passed | 0 / 0 |
| CPUC YAML (`policy/baseline/gov/states/ca/cpuc`) | 36 passed | 0 |
| Tlaib YAML (`policy/contrib/congress/tlaib`) | 22 passed | 0 |
| Reform YAML (`policy/reform`) | 51 passed | 0 |
| `test_spm_integration_contract` + `test_cpuc_spm_independence` + `test_spm_source_input_contract` | 46 passed | 0 |
| `.github/release_lock.py --committed` | resolved 149 packages | 0 |
| `.github/tests/test_release_*.py` | 33 tests, 1 skipped | 0 |

## Open
- [ ] #9448's `test_spm_policy_family.py` is NOT carryable as-is: 16 of its 27 cases fail against
      #9463's mechanism (they assert a child branch's reform propagates to parent and siblings;
      #9463 deliberately isolates it). Adjudication workflow running.
- [ ] Full `tests/core` + `tests/unit` + `tests/code_health` run
- [ ] Push, draft PR, CI
- [ ] REMOVE PROGRESS.md before final push
