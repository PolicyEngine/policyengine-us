# Accuracy lane: state-tax (PA #8848, NJ #8849, OK #8830)

## Status: COMPLETE — PR #8922 open as DRAFT, CI running. DO NOT MERGE.

Branch: codex/state-tax-accuracy (pushed to origin = MaxGhenis fork)
PR: https://github.com/PolicyEngine/policyengine-us/pull/8922 (base PolicyEngine/policyengine-us:main)
Commit: 36b381387f

## Per-issue verdicts

### #8848 PA post-retirement employer-plan distributions — FIXED
- Bug: pa_nontaxable_retirement_distributions excluded only taxable_ira_distributions.
  401(k)/403(b)/SEP/Keogh distributions (all in taxable_retirement_distributions, disjoint
  from taxable_pension_income which the pension path already handles) stayed taxable at 3.07%.
- Law: 61 Pa. Code 101.6 groups IRA/SEP/Keogh/qualified employer plans; non-taxable when
  distributed on/after retirement after reaching plan age or service. PIT Guide + DOR 1099-R
  FAQ a_id 1470 (Code 7) concur.
- Fix: new param gov/states/pa/tax/income/nontaxable_retirement_distribution_sources lists all 5
  sources; variable sums them, keeps 59.5 retirement_age_threshold proxy (mirrors IRA path, matches
  issue's "same treatment as IRA after 59.5"). Corrected the old Case 3 test that pinned the bug.
- Tests: PA 356 -> 360. Cases for each plan type + reported household (scenario_085: age 67, $1,560 401k).

### #8849 NJ 529 deduction ordering — FIXED
- Bug: nj_529_deduction was in subtractions.yaml -> nj_total_income -> nj_agi (gross-income line).
  Netted into nj_agi before the filing-threshold test, wrongly zeroing 529 contributors just above
  $10k/$20k gross income AND flipping nj_property_tax_deduction_eligible.
- Law: NJ-1040 line 29 = gross income (filing threshold, 54A:2-4). 529 = line 37a College
  Affordability deduction (54A:3-13), applied between gross income and taxable income (line 39).
- Fix: removed from subtractions.yaml (collapsed redundant 2022 breakpoint); added to
  nj_total_deductions alongside nj_medical_expense_deduction (its 54A:3 sibling). Income limit reads
  federal AGI not nj_agi, so no cycle.
- Tests: NJ 549 -> 550. Boundary test: emp $10,500 + $10k 529 -> nj_agi stays 10,500, deduction lands
  in nj_total_deductions. Verified property-tax eligibility now True.

### #8830 OK IRC 401 pensions in TY2021 — ALREADY FIXED on main (PR #8911, commit 1f61736c69)
- ok_pension_subtraction already excludes private (IRC 401) pensions before 2022 via dated bool param
  private_pension_qualifies (2021 false / 2022 true), page-anchored to Form 511 Schedule 511-A line 6.
- Reported household verified: age 66, taxable_private_pension_income 20000, state_fips 40 ->
  ok_pension_subtraction 0 in 2021, 10000 in 2022. Baseline tests already cover this + govt-pension-still-
  qualifies-2021 case. Recommend closing #8830 with reference to #8911. No code change.

## Verification done
- Local trees pass: PA 360, NJ 550, OK 187. Structural (6) + metadata (3) + NJ deductions/bond (20) pass.
- CI (PR #8922): changelog, 6 smoke-imports (3.9-3.14), Lint, bundle metadata, Quick Feedback selective,
  both codecov = SUCCESS. 23 full-suite shards were in progress at last check, 0 failures.

## Follow-up flagged (out of scope, separate task task_4fc62107)
- Kentucky pension exclusion (ky_pension_income_exclusion) may over-apply to working-age pension income
  without retiree-status gating (taxsim record 30551). Needs KRS 141.019 + Schedule P verification.
