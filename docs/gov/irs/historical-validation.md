# Historical federal tax validation

The federal tax reference tests compare PolicyEngine with Tax-Calculator 6.9.1 for six hypothetical filing units in every year from 2017 through 2026. All 60 cases agree within $0.01 on eight outputs: adjusted gross income, standard deduction, personal exemptions, taxable income, income tax before credits, EITC, income tax after credits, and employee payroll tax. The [integration file](../../../policyengine_us/tests/policy/baseline/gov/irs/tax/federal_income/integration.yaml) contains these cases alongside two existing tests.

## Household coverage and assumptions

Each year uses the same wages, ages and family composition. These examples do not age a cohort or use survey records.

| Filing status | Annual wages, by adult | Children's ages |
| --- | --- | --- |
| Single | $40,000 | None |
| Head of household | $20,000 | 8 |
| Married filing jointly | $40,000; $0 | 8, 12 |
| Married filing jointly | $120,001; $0 | 8, 12 |
| Single | $300,001 | None |
| Married filing jointly | $35,000; $35,000 | 8, 12 |

The head is 35 and the spouse, where present, is 33. The cases assume full receipt of eligible credits, wages as the only income source, and no itemized expenses. PolicyEngine uses Texas and explicitly sets ACA premium tax credits and state sales tax to zero. The comparison covers federal taxes only.

Tax-Calculator uses the policy year as the records' start year, with no growth factors, weights or adjustment ratios. Its `exact_calculations=True` option preserves statutory steps rather than smoothing them. It does not reproduce every IRS Tax Table, EITC table or filing-rounding convention. The income-tax mapping uses `soi_iitax=False`; employee payroll tax equals `ptax_was / 2 + ptax_amc`, because ordinary wage FICA includes both shares while Additional Medicare Tax falls on the employee. The [generator](../../../policyengine_us/tools/taxsim/generate_federal_tax_history_reference.py) enforces these assumptions against the pinned [Tax-Calculator source](https://github.com/PSLmodels/Tax-Calculator/releases/tag/6.9.1).

For 2020 and 2021, income tax includes annual Recovery Rebate Credit entitlement. These examples do not subtract advance payments and therefore do not represent the balance due or refund on a filed return.

## Reproducing the independent reference

From the repository root, run the standalone generator in a separate environment:

```sh
uv run --no-project --isolated --with taxcalc==6.9.1 python \
  policyengine_us/tools/taxsim/generate_federal_tax_history_reference.py \
  --output federal-tax-history-reference.json
```

This command keeps Tax-Calculator out of the model's environment. The generator imports no PolicyEngine runtime, requires a new JSON output path, checks the Tax-Calculator version and five source-file hashes, and records all synthetic inputs, outputs and dependency versions. It also rejects gaps in 2017–2026 coverage. [Tooling tests](../../../policyengine_us/tests/code_health/test_federal_tax_history_reference.py) check these guards.

## Disposition of the 35 date flags

A frozen 2017 parameter trace identified 35 IRS parameter paths whose available histories began after 2017. A later first date alone does not establish an incorrect tax calculation: a constant can remain valid, a later provision can have an effective-date gate, and a parent node can overlap its leaf. The table accounts for all 35 paths. It does not count distinct laws or estimate the share of tax law that the model implements.

Every path below has the prefix `gov.irs.`. “Explicit 2017” means the parameter now has a source-linked 2017 entry; it does not necessarily mean its calculated value changed.

| Parameter path | Disposition for 2017 | Primary evidence |
| --- | --- | --- |
| `capital_gains.other_cg_rate` | Explicit 2017 rate of 28%; the previous backfilled value matched. | [Schedule D instructions, p. 16][schedule-d] |
| `capital_gains.unrecaptured_s_1250_rate` | Explicit 2017 rate of 25%; the previous value matched. | [Schedule D instructions, p. 16][schedule-d] |
| `credits.ctc.adult_ssn_requirement_applies` | Explicit false; no special SSN-only requirement in 2017. This does not remove the filer's TIN requirement. | [Publication 972, p. 3][ctc] |
| `credits.ctc.child_ssn_requirement_applies` | Corrected to false in 2017; the formula requires a valid TIN. The restricted SSN branch begins in 2018. | [IRC 24(e), (h)][section-24]; [Publication 972][ctc] |
| `credits.ctc.eligible_ssn_card_type` | No change; the restricted list does not govern the 2017 child-TIN branch. | [IRC 24(e), (h)][section-24] |
| `credits.ctc.refundable.social_security.add` | Explicit 2017 payroll-component list; the previous components matched. | [Schedule 8812, p. 2][actc] |
| `credits.ctc.refundable.social_security.subtract` | Explicit 2017 excess-withholding list; the formula subtracts EITC separately. | [Schedule 8812, p. 2][actc] |
| `credits.retirement_saving.age_threshold` | Explicit age 18; the previous value matched. | [Form 8880][saver] |
| `credits.retirement_saving.contributions_cap` | Explicit $2,000; the previous value matched. | [Form 8880, line 6][saver] |
| `credits.retirement_saving.distributions` | Corrected 2017 list excludes ABLE distributions; the 2018 list remains. | [Form 8880][saver]; [P.L. 115-97, §11024][tcja] |
| `credits.retirement_saving.qualified_retirement_savings_contributions` | Corrected 2017 list excludes ABLE contributions; the 2018 list remains. | [Form 8880][saver]; [P.L. 115-97, §11024][tcja] |
| `credits.retirement_saving.rate.joint` | Corrected 2017 joint band tops: $37,000, $40,000 and $62,000. | [Form 8880, line 9][saver] |
| `credits.retirement_saving.rate.threshold_adjustment` | Explicit multipliers: joint 1, head of household 0.75, other statuses 0.5. The previous values matched. | [Form 8880, line 9][saver] |
| `deductions.deductions_if_itemizing` | Explicit 2017 composition; QBI, tips and overtime retain their own effective-date gates. | [Form 1040, line 40][form-1040] |
| `deductions.deductions_if_not_itemizing` | Removed a second tuition deduction after AGI; the existing adjustment already deducts tuition before AGI. | [Form 1040, lines 34, 37, 40][form-1040]; [IRC 62(a)(18)][section-62] |
| `deductions.itemized.charity.non_itemizers_amount` | Explicit zero for every filing status; the previous values matched. | [Form 1040, line 40][form-1040] |
| `deductions.itemized_deductions` | Explicit 2017 modeled component list; no component change. | [Schedule A instructions][schedule-a] |
| `deductions.overtime_income.eligible_ssn_card_type` | No list change; the deduction's effective-date gate excludes 2017 and begins in 2025. | [P.L. 119-21, §70202][obbba] |
| `deductions.qbi.deduction_definition` | No change; the existing maximum rate makes the final deduction zero in 2017. Section 199A begins in 2018. | [P.L. 115-97, §11011(e)][tcja] |
| `deductions.qbi.income_definition` | Same effective-date disposition; reading components does not create a 2017 deduction. | [P.L. 115-97, §11011(e)][tcja] |
| `deductions.standard.dependent.amount` | Explicit $1,050; the previous value matched. The earned-income addition remains $350, subject to the ordinary cap. | [Form 1040 instructions, p. 39][instructions-1040] |
| `deductions.tip_income.eligible_ssn_card_type` | No list change; the deduction's effective-date gate excludes 2017 and begins in 2025. | [P.L. 119-21, §70201][obbba] |
| `dependent.ineligible_age.non_student` | No change; current history already supplies the under-19 boundary from 1954. Added a 2017 boundary test. | [Form 1040 instructions, p. 17][instructions-1040] |
| `dependent.ineligible_age.student` | No change; current history already supplies the under-24 boundary from 1989. Added a 2017 boundary test. | [Form 1040 instructions, p. 17][instructions-1040] |
| `gross_income.dependent_care_assistance_programs.reduction_amount` | Explicit 2017 caps: $5,000, or $2,500 for married filing separately. The previous values matched. | [Form 2441, line 21][dcap] |
| `gross_income.dependent_care_assistance_programs.reduction_amount.SINGLE` | Same $5,000 cap; this leaf overlaps the preceding parent node. | [Form 2441, line 21][dcap] |
| `gross_income.retirement_contributions.catch_up.age_threshold` | Explicit age 50; the previous value matched. | [Notice 2016-62][retirement-limits] |
| `gross_income.retirement_contributions.catch_up.limit.ira` | Explicit $1,000; the previous value matched. | [Notice 2016-62][retirement-limits] |
| `gross_income.retirement_contributions.catch_up.limit.k401` | Explicit $6,000 for age 50 and older; the previous values matched. | [Notice 2016-62][retirement-limits] |
| `gross_income.retirement_contributions.limit.401k` | Corrected 2017 elective-deferral limit to $18,000. | [Notice 2016-62][retirement-limits] |
| `gross_income.retirement_contributions.limit.annual_additions` | Corrected 2017 annual-additions limit to $54,000. | [Notice 2016-62][retirement-limits] |
| `gross_income.retirement_contributions.limit.ira` | Explicit $5,500; the previous value matched. | [Notice 2016-62][retirement-limits] |
| `income.amt.capital_gains.capital_gain_excess_tax_rate` | Explicit 25%; the previous value matched. | [Form 6251, line 61][amt] |
| `income.amt.deductions_add_back` | Explicit empty general list; separate itemized addbacks still apply. | [Form 6251, Part I][amt] |
| `income.exemption.traditional_distribution.age_threshold` | No change to 59.5. Only state retirement-deduction formulas call this parameter; federal validation does not cover those callers. | [Publication 590-B, p. 24][ira-distributions] |

## Additional rule tests and limits

Focused tests also cover the [personal-exemption phaseout](../../../policyengine_us/tests/policy/baseline/gov/irs/income/taxable_income/exemptions/exemptions.yaml): a partial step triggers the full 2% reduction, as the [2017 worksheet, p. 41][instructions-1040] requires. [Dependent-care tests](../../../policyengine_us/tests/policy/baseline/gov/irs/credits/cdcc/dependent_care_assistance_exclusion.yaml) cover the actual qualified-expense ceiling and prevent reuse of excluded employer benefits for the child and dependent care credit, following [Form 2441, Part III][dcap]. [Traditional IRA tests](../../../policyengine_us/tests/policy/baseline/household/expense/retirement/traditional_ira_contributions.yaml) cover the age-70.5 restriction through 2019 and its removal from 2020, following [Publication 590-A][ira-contributions] and [P.L. 116-94, Division O, §107][secure].

[Saver's Credit examples](../../../policyengine_us/tests/policy/baseline/gov/irs/credits/retirement_saving/savers_credit_person.yaml) check the published inclusive AGI ceilings and fractional income above them. [Generated populations](../../../policyengine_us/tests/core/test_federal_2017_tax_history_properties.py) repeat these checks for all five filing statuses in every year from 2017 through 2026.

The 60 wage cases do not exercise every flagged provision. They do not establish complete coverage of itemized deductions, AMT preferences, capital gains, retirement transactions, identification compliance or special filing situations. The TIN input does not encode issuance dates or every identification requirement; aggregate childcare spending cannot distinguish each child's eligible expense share in mixed-age families. Fractional age inputs can express the former IRA age boundary, but integer survey ages do not reconstruct birthdays.

This validation covers selected federal household calculations. It does not establish historical accuracy for state taxes, benefit programs, household net resources or national 2017 population estimates. Those uses require their own policy-date, input and population checks.

[schedule-d]: https://www.irs.gov/pub/irs-prior/i1040sd--2017.pdf#page=16
[ctc]: https://www.irs.gov/pub/irs-prior/p972--2017.pdf#page=3
[section-24]: https://www.govinfo.gov/content/pkg/USCODE-2017-title26/pdf/USCODE-2017-title26-subtitleA-chap1-subchapA-partIV-subpartA-sec24.pdf#page=2
[actc]: https://www.irs.gov/pub/irs-prior/f1040s8--2017.pdf#page=2
[saver]: https://www.irs.gov/pub/irs-prior/f8880--2017.pdf#page=1
[tcja]: https://www.govinfo.gov/content/pkg/PLAW-115publ97/pdf/PLAW-115publ97.pdf
[form-1040]: https://www.irs.gov/pub/irs-prior/f1040--2017.pdf
[section-62]: https://www.govinfo.gov/content/pkg/USCODE-2017-title26/pdf/USCODE-2017-title26-subtitleA-chap1-subchapB-partI-sec62.pdf#page=3
[schedule-a]: https://www.irs.gov/pub/irs-prior/i1040sca--2017.pdf
[instructions-1040]: https://www.irs.gov/pub/irs-prior/i1040gi--2017.pdf
[obbba]: https://www.congress.gov/119/bills/hr1/BILLS-119hr1enr.pdf#page=100
[dcap]: https://www.irs.gov/pub/irs-prior/f2441--2017.pdf#page=2
[retirement-limits]: https://www.irs.gov/pub/irs-drop/n-16-62.pdf
[amt]: https://www.irs.gov/pub/irs-prior/f6251--2017.pdf
[ira-distributions]: https://www.irs.gov/pub/irs-prior/p590b--2017.pdf#page=24
[ira-contributions]: https://www.irs.gov/pub/irs-prior/p590a--2017.pdf#page=5
[secure]: https://www.govinfo.gov/content/pkg/PLAW-116publ94/pdf/PLAW-116publ94.pdf
