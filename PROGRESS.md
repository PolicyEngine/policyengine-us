# PROGRESS — unified SPM candidate (max/spm-unified-candidate-20260914)

## State
Base: `upstream/main` @ `2cc6f045ab1f389bc781ffd9f5e874055b3c0a3d` (version 2.1.0).
Worktree: `/Users/maxghenis/spm-rebuild-20260908/worktrees/policyengine-us-spm-unified-20260914`.

Verified PR heads (2026-09-14):
| PR | head | base merge-base |
|---|---|---|
| #9466 | `9f9510b735b3b9b2e375854d66fd315202e31d35` | 2cc6f045ab |
| #9463 | `d8cbd4b7a0b292beafad37cfc72813e1d710fc3e` (lane 20260914-144927 still RUNNING — re-verify) | 2cc6f045ab |
| #9448 | `8f74a5152d1e52c33bd7a7cba6340346bd7fe004` | 2ba7daa30e |
| #9464 | `cafcd9443df7f638a5ad547a92c6e0bcfd784fbb` | 4d34e3d1ab |
| #9462 | `47e94fa491bbf65ae4b6bd5667f054445b26de36` | deliberately excluded |

## Done
- [x] Read reconciliation memo, FINAL-REPORT, EXPANDED-REVIEW, FINDINGS-RECOVERY
- [x] Worktree + branch from `upstream/main`
- [x] Step 2a: #9466 cherry-picked as-is (`c5d8abfb44`)

## Next
- [ ] Poll lane 20260914-144927-spm-fix-isolation-202 until not RUNNING; re-verify #9463 head
- [ ] Step 2b: #9463 isolation mechanism + county FIPS + docs + 16 regression tests (drop PROGRESS.md, lane-bookkeeping pinned_tbs.py)
- [ ] Step 2c: #9448 reduced (CPUC exclusion, general/CBO/Tlaib housing switch, release tooling, policy-family + source-input contract tests)
- [ ] Step 2d: #9464 reduced (alias guard, dataset digest, batch exit shim, citations)
- [ ] Step 3: EXPANDED-REVIEW R1/R2 fixes; R8 FERA note
- [ ] Step 4: verification suites + exit codes
- [ ] Step 5: push, draft PR, CI
- [ ] REMOVE PROGRESS.md before final push
