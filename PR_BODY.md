## Summary

Three state income-tax accuracy issues. Two are fixed here with dated, page-anchored parameters and tests; one is already correct on `main` and is documented below with evidence for closing.

| Issue | State | Verdict |
|---|---|---|
| #8848 | PA | **Fixed** — employer-plan (401(k), 403(b), SEP, Keogh) distributions now exempt post-retirement, like IRAs |
| #8849 | NJ | **Fixed** — 529 deduction moved from gross-income subtractions to taxable-income deductions |
| #8830 | OK | **Already correct on `main`** (PR #8911) — close with evidence |

---

## #8848 — PA post-retirement employer-plan distributions

**Law.** 61 Pa. Code § 101.6 defines "Old Age or Retirement Benefit Plans" to include "Individual Retirement plans (IRA), Simplified Employee Pension Plans (SEP), Keogh plans, Federally qualified employe pension plans and similar old age or retirement benefit plans," and makes their distributions non-taxable when "made upon or after retirement from service after reaching a specific age or after a stated period of employment." The PA PIT Guide (Gross Compensation) and the PA DOR 1099-R FAQ (a_id 1470, Code 7 normal distribution) say the same: a distribution from an eligible PA plan is not taxable once the plan's age/service requirements for retirement are met.

**Bug.** `taxable_401k_distributions`, `taxable_403b_distributions`, `taxable_sep_distributions`, and `keogh_distributions` all sit in `taxable_retirement_distributions` — separate from `taxable_pension_income` (which the pension path already exempts via `pa_nontaxable_pension_income`). `pa_nontaxable_retirement_distributions` only excluded `taxable_ira_distributions`, so post-retirement 401(k)/403(b)/SEP/Keogh distributions stayed in `pa_total_taxable_income` and were taxed at 3.07%.

**Fix.** New parameter `gov/states/pa/tax/income/nontaxable_retirement_distribution_sources` lists all five eligible distribution sources; `pa_nontaxable_retirement_distributions` sums them and applies the existing `retirement_age_threshold` (59½) proxy, mirroring the IRA treatment the issue asks for. The previously-passing "Case 3" test that pinned the old behavior (401(k) at 67 → taxed) is corrected to the exempt result, and cases for 403(b)/SEP/Keogh plus the issue's reported household (PolicyBench scenario_085: PA single, age 67, $1,560 401(k)) are added.

---

## #8849 — NJ 529 deduction shifts the filing threshold

**Law.** NJ's filing-threshold zero-tax floor (N.J.S.A. 54A:2-4) tests **gross income** — Form NJ-1040 line 29 ("more than $20,000 … $10,000 if single/MFS"). The NJBEST 529 contribution deduction (N.J.S.A. 54A:3-13; P.L. 2021 c.419) is a New Jersey College Affordability Act deduction on **line 37a**, in the deductions block (lines 30–37c) between gross income (line 29) and taxable income (line 39) — the same 54A:3 family as the medical-expense deduction PE already models in `nj_total_deductions`.

**Bug.** `nj_529_deduction` was listed in `subtractions.yaml`, which feeds `nj_total_income` → `nj_agi` (PE's gross-income line). Away from the threshold this is harmless (the deduction lands either way), but at the boundary it netted into `nj_agi` and wrongly pulled 529 contributors just above $10k/$20k below the threshold, zeroing their tax and flipping `nj_property_tax_deduction_eligible`.

**Fix.** Remove `nj_529_deduction` from `subtractions.yaml` (collapsing the now-redundant 2022 breakpoint) and add it to `nj_total_deductions` alongside `nj_medical_expense_deduction`. Its income-limit test reads federal `adjusted_gross_income`, not `nj_agi`, so this creates no circular dependency. A boundary test confirms a single filer with $10,500 gross income and $10,000 of 529 contributions keeps `nj_agi = 10,500` (above the threshold, unmoved by the deduction) with the deduction landing in `nj_total_deductions`.

---

## #8830 — OK §401 employer pensions in TY2021 (already fixed)

Fixed on `main` by PR #8911 (commit `1f61736c69`). `ok_pension_subtraction` now excludes private-employer (IRC §401) pension income before 2022 via the dated boolean parameter `private_pension_qualifies` (2021 → `false`, 2022 → `true`), page-anchored to Form 511 Schedule 511-A line 6 for both years. The reported-household case is already covered by baseline tests: age 66 with `taxable_private_pension_income: 20_000` yields `ok_pension_subtraction: 0` in 2021 and `10,000` in 2022, with a companion case confirming government pensions still qualify in 2021. No code change needed; recommend closing #8830 with reference to #8911.

---

## Tests

All baseline state trees pass on this branch:

- PA: 360 (was 356; +4 net from expanded employer-plan and reported-household cases)
- NJ: 550 (was 549; +1 filing-threshold boundary test)
- OK: 187 (unchanged; already covers the #8830 year-boundary cases)

Run:
```
python -m policyengine_core.scripts.policyengine_command test \
  policyengine_us/tests/policy/baseline/gov/states/{pa,nj,ok}/ -c policyengine_us
```

Closes #8848, closes #8849, closes #8830.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
