# State credit income-definition audit: batch C
Code read at `upstream/main` 06c0dcbc54 (no checkout, nothing run). Sources are under `C:/tmp/sci-audit/src/` unless a path is given. Finished: New York household gross income, New Jersey property tax relief income, Pennsylvania property tax/rent rebate income, Pennsylvania tax forgiveness eligibility income, Rhode Island property tax relief household income, Vermont renter credit income. All six definitions are written.

## Findings

| State | Credit | Finding | Class | Dollar direction |
|---|---|---|---|---|
| NY | Real property tax credit (IT-214), through 2024 | Only the claimant's tax unit is summed; the law pools every household member (unrelated tenants, roomers and boarders excepted) | CONFIRMED | Income too low; credit too high or wrongly allowed |
| NY | Real property tax credit, through 2024 | Workers' compensation not counted | CONFIRMED | Income too low; credit too high |
| NY | Real property tax credit, through 2024 | Child support ("support money") not counted | CONFIRMED | Income too low; credit too high |
| NY | Real property tax credit, through 2024 | Veterans' disability pensions (`veterans_benefits`) not counted | CONFIRMED | Income too low; credit too high |
| NY | Real property tax credit, through 2024 | Pensions and annuities outside federal AGI (`tax_exempt_pension_income`) not counted | CONFIRMED | Income too low; credit too high |
| NY | Real property tax credit, through 2024 | Cash public assistance (TANF, Safety Net Assistance, State Supplement Program) not counted | CONFIRMED | Income too low; credit too high |
| NY | Real property tax credit, through 2024 | Tax-exempt disability ("loss-of-time") insurance benefits not counted | CONFIRMED | Income too low; credit too high |
| NY | Real property tax credit, through 2024 | Section 911 excluded foreign earned income not added back | CONFIRMED | Income too low; credit too high |
| NY | Real property tax credit, through 2024 | Nontaxable strike benefits not counted | CONFIRMED | Income too low; credit too high (small) |
| NY | Real property tax credit, through 2024 | New York 612(b) additions entered in `ny_other_additions` (414(h), IRC 125) not added | CONFIRMED | Income too low; credit too high |
| NY | Real property tax credit, through 2024 | Roth and other nontaxable retirement account distributions: "pension or annuity benefits" or not | TWO-READINGS | If counted, income too low on main |
| NY | Real property tax credit, through 2024 | Alimony outside AGI (post-2018 divorces): "support money" or not | TWO-READINGS | If counted, income too low on main |
| NY | Real property tax credit, through 2024 | Railroad retirement benefits outside AGI | COVERED (#10722) | Income too low on main |
| NY | Real property tax credit, through 2024 | Gambling winnings missing from federal AGI | COVERED (#10070) | Income too low on main |
| NY | Real property tax credit, through 2024 | Excluded gain on sale of property (IRC 121); part-year household members | NOT-MODELABLE | Income too low where it applies |
| NJ | Stay NJ | The benefit paid in a calendar year is set by income two tax years earlier (2025 income for 2027 payments); PolicyEngine tests same-year income against payment-year limits and tiers | CONFIRMED (timing) | Either way; follows income growth between the two years |
| NJ | Stay NJ / Senior Freeze income | Dependents' income is summed with the claimant's | CONFIRMED | Income too high; lower Stay NJ tier or lost eligibility |
| NJ | Stay NJ / Senior Freeze income | A disability pension entered as wages (as `total_disability_payments` documents) counts twice | CONFIRMED | Income too high |
| NJ | ANCHOR | Income is the sum of `nj_gross_income`, not NJ-1040 line 29: U.S. obligation interest is counted | CONFIRMED | Income too high; $1,000 instead of $1,500, or renter excluded |
| NJ | ANCHOR | 401(k) elective deferrals counted as wages (54A:6-21 excludes them) | CONFIRMED | Income too high; benefit too low or lost |
| NJ | ANCHOR | Dependents' income counted | CONFIRMED | Income too high; benefit too low or lost |
| NJ | ANCHOR | Pension and other retirement exclusions (line 28c) not subtracted | CONFIRMED | Income figure too high; no effect on the benefit at current limits |
| NJ | Stay NJ / Senior Freeze income | Wages: W-2 box 16 (agency, line 27) or gross of 401(k) deferrals (broad reading of "before ... any authorized exclusion") | TWO-READINGS | PolicyEngine is above the agency's figure |
| NJ | Stay NJ / Senior Freeze income | Return of pension contributions excluded by 54A:6-10(a): the statute's words count it, the agency's line 27 does not | TWO-READINGS | If counted, income too low on main |
| NJ | Stay NJ / Senior Freeze income | Disability pension before conversion age: not in the statute's list, added by PAS-1 line d | TWO-READINGS | PolicyEngine follows the form |
| NJ | Stay NJ / Senior Freeze income | Unemployment, railroad retirement, military pensions, workers' compensation: counted under a broad reading, left out by the agency | TWO-READINGS | If counted, income too low on main |
| NJ | Stay NJ / Senior Freeze income | Roth IRA basis cannot be separated from earnings | NOT-MODELABLE | Income too high by the basis withdrawn |
| PA | Property Tax/Rent Rebate | Alimony from a pre-2019 divorce is counted twice (in federal AGI and again on the line 11 list) | CONFIRMED | Income too high; rebate too low or lost |
| PA | Property Tax/Rent Rebate | Wages enter net of 401(k)/403(b) deferrals and other pre-tax payroll deductions; the law counts gross salaries | CONFIRMED | Income too low; rebate too high |
| PA | Property Tax/Rent Rebate | Cash public assistance (TANF, general assistance) not counted | CONFIRMED | Income too low; rebate too high |
| PA | Property Tax/Rent Rebate | Cash gifts from outside the household (`financial_assistance`) not counted | CONFIRMED | Income too low; rebate too high |
| PA | Property Tax/Rent Rebate | Section 911 excluded foreign earned income not added back | CONFIRMED | Income too low (rare) |
| PA | Property Tax/Rent Rebate | A person's farm or pass-through loss cannot offset the same person's business profit (line 10 nets them) | CONFIRMED | Income too high (small) |
| PA | Property Tax/Rent Rebate | Railroad retirement: statute counts 50% of all benefits (main); booklet counts Tier 1 at 50% and Tier 2 in full (open PRs #10696, #10722) | TWO-READINGS | Under the booklet, main is too low by half of Tier 2 |
| PA | Property Tax/Rent Rebate | Child support: "support money" in the statute, excluded by the booklet | TWO-READINGS | If counted, income too low on main |
| PA | Property Tax/Rent Rebate | State tax refunds: no statutory exclusion, excluded by the booklet; PolicyEngine counts the taxable refund | TWO-READINGS | Under the booklet, income too high |
| PA | Property Tax/Rent Rebate | Civil Service Retirement System offset (line 12) has no basis in the act's text that I could find | UNVERIFIED | PolicyEngine follows the booklet |
| PA | Property Tax/Rent Rebate | Excluded gain on the sale of a principal residence | NOT-MODELABLE | Income too low where it applies |
| PA | Tax forgiveness (Schedule SP) | Interest on U.S. obligations is removed from Pennsylvania taxable income and never added back, though the statute names it | CONFIRMED | Income too low; forgiveness too high |
| PA | Tax forgiveness | Alimony from a pre-2019 divorce is counted twice (left in Pennsylvania taxable income, then added on line 3) | CONFIRMED | Income too high; forgiveness too low (and Pennsylvania tax too high) |
| PA | Tax forgiveness | 401(k)/403(b) employee contributions missing from Pennsylvania taxable compensation | CONFIRMED | Income too low; forgiveness too high (and Pennsylvania tax too low) |
| PA | Tax forgiveness | Life insurance proceeds (`life_insurance_benefits`) not counted | CONFIRMED | Income too low; forgiveness too high |
| PA | Tax forgiveness | Nontaxable scholarships and education grants (`educational_assistance`) not counted | CONFIRMED | Income too low; forgiveness too high |
| PA | Tax forgiveness | Cash from persons outside the household (`financial_assistance`) not counted | CONFIRMED | Income too low; forgiveness too high |
| PA | Tax forgiveness | Employee pre-tax cafeteria plan payments: counted by Schedule SP line 10, arguably excluded by 7301(o.2)(vi) | TWO-READINGS | Following the agency, income too low on main |
| PA | Tax forgiveness | Child support: no statutory exclusion; the agency assigns it to the child | TWO-READINGS | On the statute's words, the parent's income is too low on main |
| PA | Tax forgiveness | Gambling and lottery winnings missing from Pennsylvania taxable income | COVERED (#10070) | Income too low on main |
| PA | Tax forgiveness | Foster care payments; excluded home-sale gain; inheritances | NOT-MODELABLE | Income too low where they apply |
| RI | Property tax relief (RI-1040H) | Business, rental, capital and pass-through losses reduce income through federal AGI; the statute bars those deductions and the form adds them back | CONFIRMED | Income too low; credit too high or wrongly allowed |
| RI | Property tax relief | Pre-2019 alimony counted twice (in AGI and as `alimony_income`) | CONFIRMED | Income too high; credit too low or lost |
| RI | Property tax relief | Only one tax unit is summed, and a dependent's non-benefit income drops out; the law counts all persons of the household | CONFIRMED | Income too low |
| RI | Property tax relief | SSI, general assistance and the state supplement not counted (only TANF is) | CONFIRMED | Income too low |
| RI | Property tax relief | Veterans' disability pensions not counted | CONFIRMED | Income too low |
| RI | Property tax relief | Nontaxable IRA/401(k) distributions not counted (form takes gross lines 4a and 5a) | CONFIRMED | Income too low |
| RI | Property tax relief | Tax-exempt disability ("loss of time") insurance benefits not counted | CONFIRMED | Income too low |
| RI | Property tax relief | Section 911 excluded foreign earned income not added back | CONFIRMED | Income too low (rare) |
| RI | Property tax relief | Nontaxable strike benefits not counted | CONFIRMED | Income too low (small) |
| RI | Property tax relief | Unnamed nontaxable income (scholarships, life insurance proceeds): "all non-taxable income" or only the kinds listed | TWO-READINGS | If counted, income too low on main |
| RI | Property tax relief | Railroad retirement benefits | COVERED (#10722) | Income too low on main |
| RI | Property tax relief | Gambling winnings missing from federal AGI | COVERED (#10070) | Income too low on main |
| RI | Property tax relief | Capital gains excluded from AGI | NOT-MODELABLE | Income too low where it applies |
| VT | Renter credit (RCC-146) | Above-the-line deductions are not added back to AGI (6061(18)(D); form line 10 is federal total income) | CONFIRMED | Income too low; credit too high or wrongly allowed |
| VT | Renter credit | Business, farm, rental, capital, pass-through and trust losses are not added back (6061(18)(A); form line 13) | CONFIRMED | Income too low; credit too high or wrongly allowed |
| VT | Renter credit | 75% of a dependent's Social Security is counted as the claimant's income | CONFIRMED | Income too high; credit too low or lost |
| VT | Renter credit | SSI: outside the statute's 86(d) benefits, but the booklet has non-filers count 75% of it | TWO-READINGS | Under the booklet, a non-filer's income is too low on main |
| VT | Renter credit | Tier 1 railroad retirement benefits outside AGI | COVERED (#10722) | Income too low on main |
| VT | Renter credit | Gambling winnings missing from federal AGI | COVERED (#10070) | Income too low on main |

Class: CONFIRMED (law is clear, PolicyEngine differs), TWO-READINGS, COVERED (an open PR fixes it), NOT-MODELABLE (no input), UNVERIFIED. Dollar direction is the effect of the gap on the income figure and on the credit.

## 1. New York household gross income (real property tax credit, IT-214)

### What PolicyEngine does

- `policyengine_us/variables/gov/states/ny/tax/income/credits/ny_household_gross_income.py` (TaxUnit, year). No parameter list; the formula is
  `ny_recomputed_federal_agi + tax_unit.sum(max_(social_security - taxable_social_security, 0) + ssi + tax_exempt_interest_income)`.
- `ny_recomputed_federal_agi` is `adjusted_gross_income + charitable_contributions_ald` (IT-201 line 19a). Losses net as they do in federal AGI. The credit floors the total at zero and rounds it.
- Only reader: `ny_real_property_tax_credit`, and only while `gov.states.ny.tax.income.credits.real_property_tax.uses_household_gross_income` is true (2000 to 2024). From 2025 the credit reads `ny_recomputed_federal_agi`.
- The variable's own documentation lists what it leaves out: other household members, pensions and annuities not in AGI, cash public assistance, workers' compensation, child support and veterans' disability pensions.

### What the law says

- N.Y. Tax Law 606(e)(1)(C) (read at newyork.public.law, saved as `src/ny_tax_606_publiclaw.txt`; nysenate.gov returned 403 to curl):
  "\"Household gross income\" means the aggregate adjusted gross income of all members of the household for the taxable year as reported for federal income tax purposes ... with the modifications in subsection (b) of section six hundred twelve but without the modifications in subsection (c) of such section, plus any portion of the gain from the sale or exchange of property otherwise excluded from such amount; earned income from sources without the United States excludable from federal gross income by section nine hundred eleven of the internal revenue code; support money not included in adjusted gross income; nontaxable strike benefits; supplemental security income payments; the gross amount of any pension or annuity benefits to the extent not included in such adjusted gross income (including, but not limited to, railroad retirement benefits and all payments received under the federal social security act and veterans' disability pensions); nontaxable interest received from the state of New York ...; workers' compensation; the gross amount of \"loss-of-time\" insurance; and the amount of cash public assistance and relief, other than medical assistance for the needy, paid to or for the benefit of the qualified taxpayer or members of his household. Household gross income shall not include surplus foods or other relief in kind ... household gross income shall only include all such income received by all members of the household while members of such household."
- 606(e)(1)(B): "\"Household\" or \"members of the household\" means a qualified taxpayer and all other persons, not necessarily related, who have the same residence and share its furnishings, facilities and accommodations. Such terms shall not include a tenant, subtenant, roomer or boarder who is not related to the qualified taxpayer ..."
- 2024 Form IT-214, Step 3 (`src/ny_it214_2024.pdf`, file p. 2): "Enter the total of all amounts, even if not taxable, that you, your spouse (if married), and all other household members received during 2024." Lines 9 (FAGI), 10 (New York additions), 11 (Social Security not on line 9), 12 (SSI), 13 ("Pensions and annuities (including railroad retirement benefits) not included on lines 9 through 12"), 14 (cash public assistance and relief), 15 (other income), 16 (total).
- 2024 IT-214-I (`src/ny_it214i_2024.pdf`, file p. 2), line 15: "Other income may include: nontaxable interest received from New York State ...; workers' compensation; support money, including foster care support payments; income earned abroad exempted by section 911 of the IRC; nontaxable strike benefits; and the gross amount of loss-of-time insurance". Also: "Do not include food stamps, Medicare, Medicaid, scholarships, grants, surplus food, or other relief in kind."
- From 2025 (L. 2025 ch. 59, Part RR; bill text `src/ny_s3009c_2025.pdf`, file p. 134-141): 606(e)(7)(A)(ii) denies the credit "if the taxpayer's federal adjusted gross income exceeds eighteen thousand dollars", and the 2025 IT-214-I (file p. 2) says "Enter the total FAGI from your federal or New York returns" and "Married filed joint taxpayers must calculate a combined FAGI." PolicyEngine's switch to federal AGI in 2025 matches.

### Differences

| Category | Law | PolicyEngine | Class |
|---|---|---|---|
| Other household members | All who share the residence, except unrelated tenants, roomers, boarders | One tax unit | CONFIRMED, undercount |
| Workers' compensation | Counted | Not read (`workers_compensation`) | CONFIRMED, undercount |
| Support money | Counted when not in AGI | `child_support_received` not read | CONFIRMED, undercount |
| Veterans' disability pensions | Counted | `veterans_benefits` not read | CONFIRMED, undercount |
| Pensions and annuities outside AGI | Gross amount counted | `tax_exempt_pension_income` not read | CONFIRMED, undercount |
| Cash public assistance and relief | Counted | `tanf`, `general_assistance`, `ny_ssp` not read | CONFIRMED, undercount |
| Loss-of-time insurance | Gross amount | Only `taxable_disability_benefits` (through AGI) | CONFIRMED, undercount |
| Section 911 income | Counted | `foreign_earned_income_exclusion` not added back | CONFIRMED, undercount |
| Nontaxable strike benefits | Counted | `strike_benefits` not read | CONFIRMED, undercount |
| 612(b) additions | Counted | Tax-exempt interest yes; `ny_other_additions` no | CONFIRMED, undercount |
| Railroad retirement | Counted | Not read on main | COVERED (#10722) |
| Gambling winnings | In AGI | Not in federal gross income on main | COVERED (#10070) |
| Excluded gain on property sales | Counted | No input | NOT-MODELABLE |

Everything the statute names and PolicyEngine counts (federal AGI items, Social Security outside AGI, SSI, tax-exempt interest) matches for the claimant's own tax unit.

### Two readings

- **Roth and other nontaxable retirement account distributions.** The statute counts "the gross amount of any pension or annuity benefits to the extent not included in such adjusted gross income (including, but not limited to ...". Reading A treats a nontaxable IRA or 401(k) distribution as such a benefit. Reading B limits the phrase to pensions and annuities, as line 13 of the form does. The instructions don't mention IRAs. PolicyEngine follows B by omission.
- **Alimony outside AGI.** "Support money not included in adjusted gross income" reaches post-2018 alimony on its words. The instructions give only "support money, including foster care support payments", and the phrase predates the 2019 federal change. No agency statement found. PolicyEngine leaves it out.
- **Statute against form, already resolved the statute's way.** The 2024 instructions for line 11 reduce Social Security "by any Medicare premiums deducted from your benefit". The statute counts "the gross amount" of "all payments received under the federal social security act". PolicyEngine counts gross Social Security, which is the statute's rule. If the form's net amount is ever adopted, it needs a source-conflict register entry.

### Open PRs checked

- #10722 (railroad benefits): adds the untaxed part of every railroad tier to this variable. Covers the railroad row.
- #10070 (gambling winnings in federal gross income): covers gambling winnings through AGI.
- #10727 (strike benefits other than gifts in federal gross income): would bring taxable strike benefits in through AGI; the nontaxable strike benefits the statute names stay uncounted.
- Searches for "New York real property tax credit", "IT-214" and "household gross income" found no other open PR or issue on this definition.

### Tests

`tests-C/ny_household_gross_income.yaml`: 8 cases for 2024 (workers' compensation, child support, veterans' benefits, tax-exempt pension, cash assistance, tax-exempt disability benefits, section 911 income, second tax unit in the household).

### Not verified

- nysenate.gov (the official statute host) refused the fetch; the statute text comes from newyork.public.law's copy headed "N.Y. Tax Law Section 606 - Credits against tax (2026)", checked against the 2025 budget bill text for the amended paragraphs. Paragraph (C) itself was not in the bill (it was not amended).
- Section 612(b) was not opened; the list of additions comes from the 2024 IT-214-I line 10 text.

## 2. New Jersey property tax relief income (Stay NJ, Senior Freeze) and ANCHOR gross income

### What PolicyEngine does

- `parameters/gov/states/nj/tax/income/credits/property_tax_relief/income/additional_sources.yaml` (from 2026): `tax_exempt_interest_income`, `tax_exempt_ira_distributions`, `social_security`.
- `variables/gov/states/nj/tax/income/credits/property_tax_relief/nj_property_tax_relief_income.py` (TaxUnit, `formula_2026`): sum of person-level `nj_gross_income` over every tax unit member, plus the list above, plus `total_disability_payments` of members younger than their Social Security full retirement age.
- `nj_gross_income` (Person) is not NJ-1040 line 29. It is the sum of `gov.states.nj.tax.income.gross_income.non_negative_sources` (gross `employment_income`, taxable interest, dividends, taxable pensions and retirement distributions, gambling winnings, all alimony, miscellaneous income) and five loss-eligible categories (business and farm; capital gains; rents; estates and trusts; partnership and S corporation), each floored at zero per person, less a claim-of-right offset. `nj_total_income` (line 27) then adds `nj_additions` and subtracts U.S. obligation interest and `nj_other_subtractions`; `nj_agi` (line 29) sums it over head and spouse only and subtracts the retirement exclusions.
- Readers of `nj_property_tax_relief_income`: `nj_staynj_eligible` (income below `staynj.income_limit`) and `nj_staynj` (income-tiered `staynj.max_benefit` from 2027). `nj_senior_freeze` is an input, so the Senior Freeze income test is not modelled; `nj_capped_senior_freeze` has no income test.
- ANCHOR does not read that variable. `nj_anchor` and `nj_anchor_eligible` compute `add(tax_unit, period, ["nj_gross_income"])` inline.
- The property tax deduction/credit (`nj_property_tax_deduction_eligible`) reads `nj_agi` against the filing threshold; it has no income definition of its own and is not audited here.

### What the law says

- Stay NJ and Senior Freeze share one definition (P.L. 2024, c. 88, s. 1 amending N.J.S.A. 54:4-8.75b, file p. 2; s. 16 amending 54:4-8.67, file p. 16; `src/nj_pl2024_c88.pdf`): "\"Income\" means all New Jersey gross income required to be reported pursuant to the \"New Jersey Gross Income Tax Act,\" N.J.S.54A:1-1 et seq., before the application of any authorized exclusion or deduction, except also including: interest income excluded from taxation pursuant to N.J.S.54A:6-14; pension and annuity income excluded from taxation pursuant to N.J.S.54A:6-10; income derived from distributions from or roll overs to a Roth IRA excluded from taxation pursuant to N.J.S.54A:6-28; other retirement income excluded from taxation pursuant to N.J.S.54A:6-15; and Social Security income excluded from taxation pursuant to N.J.S.54A:6-2, as self-reported by the homeowner."
- Same act, s. 1 (file p. 1): an eligible claimant "has income for the prior tax year that is less than $500,000".
- 2025 PAS-1 instructions (`src/nj_pas1_inst_2025.pdf`, file p. 9): "Line a. Enter the amount from line 27, Form NJ-1040." "Line b. Enter the amount from line 16b, Form NJ-1040. This is your tax-exempt interest". "Line c. Enter the amount of any qualified distribution from a Roth IRA ... Do not include any previously taxed contributions that represent your basis." "Line d. Enter any amounts received as a total and permanent disability pension before you reached the age at which it is converted to a regular pension. (This amount is not reported on Form NJ-1040.)" "Line e. Enter the total amount of Social Security benefits (including Medicare Part B premiums) from Box 5 of Form SSA-1099." Also: "Spouses who filed separately but maintained the same main home must enter combined income."
- Division relief page (`src/nj_relief.txt`): "Do not report VA disability/military disability pension amounts, as it is not includable."
- Division Stay NJ page (`src/nj_staynj_index.txt`): "2026 Stay NJ Program (2024 Tax Year)", "2027 Stay NJ Program (2025 Tax Year)", "Income is to be calculated the same as it is for the Senior Freeze program; Income must be combined if you were married or in a civil union and lived in the same home", "The 2025 benefit will be paid in February and May of 2027."
- FY2027 Appropriations Act, P.L. 2026, c. 27 (`src/nj_pl2026_c27_fy2027_approp.pdf`, file p. 261): "eligible claimants with (a) income not in excess of $100,000 for tax year 2025 are eligible for a benefit, paid out each quarter for the first two quarters in calendar year 2027 ... (d) eligible claimants with income in excess of $200,000 for tax year 2025 are ineligible".
- ANCHOR. Same act, file p. 260: "homestead owner residents with (a) gross income in excess of $150,000 but not in excess of $250,000 for tax year 2025 ... (b) gross income not in excess of $150,000 for tax year 2025 ...". N.J.S.A. 54:4-8.58 as amended (c. 88, file p. 12): "\"Gross income\" means all New Jersey gross income required to be reported pursuant to the \"New Jersey Gross Income Tax Act,\" ... other than income excludable from the gross income tax return, but before reduction thereof by any applicable exemptions, deductions and credits". Division ANCHOR page (`src/nj_anchor_calculated.txt`): "The benefit is calculated using income on line 29 of your 2025 NJ-1040".
- Gross Income Tax Act exclusions read at law.justia.com (2025 edition; `src/nj_54a_6-*.txt`): 6-2 Social Security, 6-3 railroad retirement, 6-6 workers' compensation and injury pensions, 6-10 pensions and annuities (return of contributions in (a), the age 62 exclusion in (b), allowed only with gross income of $150,000 or less), 6-13 unemployment, 6-14 exempt interest, 6-15 other retirement income, 6-21 401(k) deferrals, 6-26 military pensions, 6-28 Roth IRA.

### Differences

**Timing (Stay NJ).** The law fixes the benefit paid in calendar year N by the income of tax year N-2 (the application for tax year N-2 is filed in N-1). PolicyEngine's Stay NJ parameters are keyed to the payment year (2026: $500,000 limit; 2027: $200,000 limit and the three tiers), and the formulas read income for that same year. So the 2027 rules are tested against 2027 income instead of 2025 income. ANCHOR parameters are keyed to the tax year instead, so `nj_staynj` nets an ANCHOR amount from a different cycle.

**Stay NJ / Senior Freeze income.**

| Category | Law | PolicyEngine | Class |
|---|---|---|---|
| Dependents' income | Not the claimant's income | Summed in | CONFIRMED, overcount |
| Disability pension entered as wages | Counted once (line d) | Counted in `employment_income` and again in `total_disability_payments` | CONFIRMED, overcount |
| Interest, dividends, business, gains, rents, pass-through, estates, pensions, IRA, alimony, gambling, Social Security | Counted | Counted | match |
| Retirement exclusions (line 28) | Not subtracted | Not subtracted | match |
| Roth IRA | Earnings only | Whole distribution | NOT-MODELABLE (no basis input) |

**ANCHOR gross income.** The law's measure is line 29; PolicyEngine's is the raw category sum. `nj_agi` already computes line 29 for head and spouse.

| Category | Line 29 | PolicyEngine | Class |
|---|---|---|---|
| U.S. obligation interest | Out | In | CONFIRMED, overcount |
| 401(k) elective deferrals | Out | In (gross wages) | CONFIRMED, overcount |
| Dependents' income | Out | In | CONFIRMED, overcount |
| Retirement exclusions | Out | In | CONFIRMED, overcount without benefit effect |

### Two readings

- **How far "before the application of any authorized exclusion or deduction" reaches.** Reading A: every exclusion in the Gross Income Tax Act is undone, so unemployment compensation, railroad retirement, military pensions, workers' compensation and 401(k) deferrals all count. Reading B: only the five listed exclusions are added to reported gross income. The agency follows B (line 27 plus lines b to e) with one addition, the disability pension on line d, which is in neither the list nor line 27. PolicyEngine follows the agency on the excluded items and on the disability pension, but counts gross wages (reading A) for 401(k) deferrals.
- **Return of pension contributions.** "pension and annuity income excluded from taxation pursuant to N.J.S.54A:6-10" reaches the 6-10(a) return-of-contributions amount on its words; the agency's line 27 leaves it out. PolicyEngine follows the agency.

### Open PRs checked

Searches for ANCHOR, Stay NJ, Senior Freeze, PAS-1 and New Jersey gross income found no open PR on these definitions. #10722 and #10764 (railroad benefits) and #10654 (property tax deduction election) do not touch them. Issue #8740 asks to model the Senior Freeze benefit itself.

### Tests

- `tests-C/nj_anchor.yaml`: 4 cases (Treasury interest for a homeowner and a renter, 401(k) deferrals, dependent's wages).
- `tests-C/nj_property_tax_relief_income.yaml`: 2 cases (dependent's income; disability pension counted once).
- No test for the Stay NJ timing gap: it needs a prior-period read and a choice of output year.

### Not verified

- N.J.S.A. 54:4-8.59 (the homestead benefit section the ANCHOR appropriation modifies) and N.J.S.A. 54A:5-1 were not opened.
- The age at which a New Jersey disability pension converts to a regular pension is not stated in the PAS-1 instructions; the NJ-1040 instructions were not opened.
- The Gross Income Tax Act sections come from law.justia.com's 2025 edition, not the Legislature's site.

## 3. Pennsylvania Property Tax/Rent Rebate income

### What PolicyEngine does

- `variables/gov/states/pa/tax/property/property_tax_or_rent_rebate/pa_property_tax_or_rent_rebate_income.py` (TaxUnit, year). There is no source-list parameter; the lists are in the formula. Parameters read: `benefit_income_rate` (0.5), `death_benefit_exclusion` (5,000), `csrs_income_exclusion` (11,432), all from 2025.
- Formula: `max_(0, adjusted_gross_income + above_the_line_deductions - tax_unit_taxable_social_security + 0.5 x (social_security + ssi + pa_ssp + railroad_benefits) + tax_exempt_interest_income + tax_exempt_pension_income + tax_exempt_retirement_distributions + gambling_winnings + alimony_income + workers_compensation + tax_exempt_disability_benefits + max_(0, life_insurance_benefits - 5,000) + csrs_retirement_pay - min_(csrs_retirement_pay, 11,432))`. Every person-level term is masked to the head and spouse.
- `adjusted_gross_income + above_the_line_deductions` is federal gross income of the head and spouse. `irs_gross_income` adds each source's positive values only ("losses are deducted later", through `loss_ald`), so adding the deductions back leaves every source floored at zero per person.
- Readers: `pa_property_tax_or_rent_rebate_eligible` (income at or under `income_limit`, 48,110 for 2025) and `pa_property_tax_or_rent_rebate` (the amount schedule).

### What the law says

- 53 P.S. 6926.1303 (Act 1 of Special Session 1 of 2006, consolidated text at legis.state.pa.us, `src/pa_tra_2006_act1_sp.txt`, definition last amended by Act 117 of 2016):
  "\"Household income.\" All income received by a claimant and the claimant's spouse while residing in the homestead during the calendar year for which a rebate is claimed."
  "\"Income.\" All income from whatever source derived, including, but not limited to: (1) Salaries, wages, bonuses, commissions, income from self-employment, alimony, support money, cash public assistance and relief. (2) The gross amount of any pensions or annuities, including railroad retirement benefits for calendar years prior to 1999 and 50% of railroad retirement benefits for calendar years 1999 and thereafter. (3) (i) ... 50% of all benefits received under the Social Security Act, except Medicare benefits, for calendar years 1999 and thereafter. ... (4) All benefits received under State unemployment insurance laws. (5) All interest received from the Federal or any state government or any instrumentality or political subdivision thereof. (6) Realized capital gains and rentals. (7) Workers' compensation. (8) The gross amount of loss of time insurance benefits, life insurance benefits and proceeds, except the first $5,000 of the total of death benefit payments. (9) Gifts of cash or property, other than transfers by gift between members of a household, in excess of a total value of $300. The term does not include surplus food or other relief in kind supplied by a governmental agency, property tax or rent rebate, inflation dividend, Federal veterans' disability payments or State veterans' benefits."
- Act 7 of 2023 (`src/pa_act7_2023.txt`) raises and indexes the household income limits and rebate amounts; it does not touch the income definition.
- 2025 PA-1000 booklet (`src/pa_1000_inst_2025.pdf`), file p. 7-9: line 4 (half of Social Security, SSI, SSDI and the State Supplementary Payment), line 5 (half of Railroad Retirement Tier 1), line 6 (gross pensions, annuities, IRA distributions, Tier 2 Railroad Retirement, Civil Service Disability), line 7 (interest and dividends, including tax-exempt interest), line 8 (gains or losses on property; losses only against gains), line 9 (net rents and royalties; losses only against rental income), line 10 (net business, profession or farm income; losses only against business income), lines 11a-11g (gross salaries and wages; gambling and prizes; inheritance, alimony and spousal support; cash public assistance, unemployment and workers' compensation; loss-of-time, disability and life insurance; gifts over $300; miscellaneous), line 12 (CSRS offset), line 13 ("Add the positive income figures reported on Lines 4 through 11g ... Do not include losses reported on Lines 8, 9, and/or 10"). "Spouses may not offset each other's income and losses." The "Do not report" list (file p. 8-9) includes child support, federal or state tax refunds, children's public assistance and disability income, federal veterans' disability payments and state veterans' benefits.

### Differences

| Category | Law | PolicyEngine | Class |
|---|---|---|---|
| Alimony, pre-2019 divorce | Once | Twice: `taxable_alimony_income` in AGI plus `alimony_income` | CONFIRMED, overcount |
| Wages | Gross salaries and wages | `irs_employment_income`, net of pre-tax payroll deductions | CONFIRMED, undercount |
| Cash public assistance | Counted | `tanf`, `general_assistance` not read | CONFIRMED, undercount |
| Cash gifts over $300 | Counted | `financial_assistance` not read | CONFIRMED, undercount |
| Section 911 income | "All income from whatever source derived" | Not added back | CONFIRMED, undercount (rare) |
| Business and farm netting | One line per person | Each source floored separately | CONFIRMED, overcount (small) |

Matches: Social Security, SSI and the State Supplementary Payment at 50%; gross pensions and retirement distributions including military retired pay; taxable and tax-exempt interest; dividends; capital gains and rentals with losses confined to their own line; unemployment; workers' compensation; disability insurance; life insurance above $5,000; gambling winnings (once on main); veterans' benefits excluded; only the claimant's and spouse's income.

### Two readings

- **Railroad retirement (statute against form).** The statute counts "50% of railroad retirement benefits". The booklet halves only Tier 1 and puts Tier 2 on line 6 in full. Main halves everything, which is the statute. Open PRs #10696 and #10722 rewrite the variable to the booklet's split. The project rule puts the statute first, so the change needs a ruling and a source-conflict register entry before it merges.
- **Child support.** "Support money" is in the statute's list. The booklet counts "spousal support money" and says not to report child support. PolicyEngine follows the booklet.
- **State tax refunds.** No exclusion in the statute; the booklet excludes "Federal or state tax refunds". PolicyEngine counts a taxable state refund through AGI.
- **State Supplementary Payment.** The booklet counts half. The statute does not name it, and it could be "cash public assistance and relief" at 100%. PolicyEngine follows the booklet (not a separate row; noted on the SSP row).

### Open PRs checked

- #10696 and #10722 (railroad benefits): both edit this variable; see the railroad row.
- #10070 (gambling winnings in federal gross income): edits this variable so winnings still count once, net of losses up to winnings.
- #10727 (strike benefits in federal gross income): does not edit this variable; taxable strike benefits would then count through AGI.
- No open issue found for "rent rebate".

### Tests

`tests-C/pa_property_tax_or_rent_rebate_income.yaml`: 4 cases (alimony once; gross wages with a 401(k) deferral; general assistance; farm loss against business profit). No test for gifts: the statute and the booklet word the $300 rule differently.

### Not verified

- The statutory basis of the line 12 CSRS offset. The consolidated act has no reference to the Civil Service Retirement System.
- Whether pre-tax health premiums are part of "gross salaries" for the booklet; the test uses a 401(k) deferral only.
- 61 Pa. Code (Department of Revenue regulations on the rebate program) was not opened.

## 4. Pennsylvania tax forgiveness eligibility income (poverty income)

### What PolicyEngine does

- `parameters/gov/states/pa/tax/income/forgiveness/eligibility_income_sources.yaml` (from 2004): `pa_total_taxable_income`, `alimony_income`, `tax_exempt_interest_income`, `military_retirement_pay_survivors`. Comments in the file name the Schedule SP lines it leaves out (nontaxable dividends and gains, insurance proceeds and inheritances, gifts and prizes, non-PA income, nontaxable military income, excluded home-sale gain, nontaxable education assistance, cash received from outside the home).
- `variables/gov/states/pa/tax/income/forgiveness/pa_eligibility_income.py` (TaxUnit): `tax_unit_non_dep_add` over that list, so head and spouse only.
- `pa_total_taxable_income` (TaxUnit) = `irs_gross_income` of head and spouse (each federal source floored at zero per person) + the `pa_other_additions` input - `gov.states.pa.tax.income.nontaxable_income_sources` (`pa_nontaxable_pension_income`, `pa_nontaxable_retirement_distributions`, `pa_nontaxable_roth_conversions`, `taxable_unemployment_compensation`, `taxable_social_security`, `us_govt_interest`, `salt_refund_income`, `military_retirement_income`, `taxable_disability_benefits`).
- Reader: `pa_tax_forgiveness_rate` (and through it `pa_tax_forgiveness_amount`). For a married claimant filing separately and not living apart, the rate variable adds the other spouse's unit through the marital unit.

### What the law says

- 72 P.S. 7301(o.2) (Tax Reform Code of 1971, consolidated text at legis.state.pa.us, `src/pa_tax_reform_code_1971.txt`): "\"Poverty income\" means for the purpose of determining eligibility for special tax provisions all moneys or property (including interest, gains or income derived from obligations which are statutorily free from State or local taxation under any other act of the General Assembly of the Commonwealth of Pennsylvania or under the laws of the United States) received of whatever nature and from whatever source derived, but not including (i) periodic payments for sickness and disability other than regular wages received during a period of sickness or disability; or (ii) disability, retirement or other payments arising under workmen's compensation acts, occupational disease acts and similar legislation by any government; or (iii) payments commonly recognized as old age or retirement benefits paid to persons retired from service after reaching a specific age or after a stated period of employment; or (iv) payments commonly known as public assistance or unemployment compensation payments by any governmental agency; or (v) payments to reimburse actual expenses; or (vi) payments made by employers or labor unions for programs covering hospitalization, sickness, disability or death, supplemental unemployment benefits, strike benefits, Social Security and retirement; or (vii) any compensation received by United States servicemen serving in a combat zone."
- 72 P.S. 7304(d)(1): "If the poverty income of the claimant during an entire taxable year is six thousand five hundred dollars ($6,500) or less, or, in the case of a married claimant, if the joint poverty income of the claimant and the claimant's spouse during an entire taxable year is thirteen thousand dollars ($13,000) or less ... with an additional income allowance of nine thousand five hundred dollars ($9,500) for each dependent".
- 2025 PA-40 Schedule SP and its instructions (`src/pa_40sp_2025.pdf`, file p. 2 and 6-8): line 1 "Enter the total PA Taxable Income amount from Line 9 of the PA-40"; line 2 tax-exempt interest, exempt-interest dividends and "exempt income and gains from investments in direct obligations of the federal government, Pennsylvania, and political subdivisions of Pennsylvania"; line 3 alimony; line 4 "total proceeds received from life or other insurance policies", inheritances and Form 1099-R code 4 amounts; line 5 gifts, awards and noncash lottery prizes; line 6 income earned while residing outside Pennsylvania; line 7 nontaxable military income other than combat zone pay; line 8 nontaxable gain on a principal residence; line 9 nontaxable scholarships, fellowships, stipends and education grants; line 10 foster care payments, spousal support, "payments received from other persons outside the household", and "Nontaxable payments to an employer's cafeteria plan". The line 10 "Do not include" list: Social Security and railroad retirement, retirement benefits after retiring, United Mineworkers pensions, child support, military pension benefits, civil service annuities, workers' compensation, sick pay and disability benefits, personal injury damages.
- 2025 PA-40 instructions (`src/pa_40in_2025.pdf`): file p. 8 lists "Alimony" among items that are not taxable income; file p. 12: "The contributions you make to your employer's sponsored retirement plan are PA-taxable compensation, even if your contributions are not taxable for federal purposes or included in the state wages shown on your W-2."

### Differences

| Category | Law | PolicyEngine | Class |
|---|---|---|---|
| U.S. obligation interest | Counted (statute names it; line 2) | Subtracted in `pa_total_taxable_income`, not added back | CONFIRMED, undercount |
| Alimony, pre-2019 divorce | Once (line 3) | In `pa_total_taxable_income` and again as `alimony_income` | CONFIRMED, overcount |
| Employee retirement plan contributions | Pennsylvania-taxable compensation (line 1) | Federal taxable wages | CONFIRMED, undercount |
| Life insurance proceeds | Counted (line 4) | `life_insurance_benefits` not read | CONFIRMED, undercount |
| Scholarships and education grants | Counted (line 9) | `educational_assistance` not read | CONFIRMED, undercount |
| Cash from outside the household | Counted (line 10) | `financial_assistance` not read | CONFIRMED, undercount |
| Gambling winnings | Counted (line 1) | Not in the tax base on main | COVERED (#10070) |

Matches: the exclusions for Social Security, railroad retirement, retirement benefits after retirement, military and civil service pensions, unemployment compensation, public assistance, workers' compensation and sick pay; federally exempt interest; head and spouse only; the joint income of married claimants.

Two of the gaps (alimony, retirement plan contributions) sit in the Pennsylvania tax base, `pa_total_taxable_income`, and so also misstate Pennsylvania tax.

### Two readings

- **Cafeteria plan payments.** Clause (vi) excludes "payments made by employers or labor unions for programs covering hospitalization, sickness, disability or death". Schedule SP line 10 counts the employee's own "Nontaxable payments to an employer's cafeteria plan". PolicyEngine leaves pre-tax premiums out.
- **Child support.** No clause of (o.2) excludes it. The instructions take it out of the parent's income and put it in the child's ("The child must also include any child support paid to his/her parent on his/her behalf in his/her Eligibility Income"). PolicyEngine counts it for no one.
- **Military survivor annuities.** PolicyEngine counts `military_retirement_pay_survivors` as a line 4 death distribution; the same instructions exclude "Military pension benefits". Noted on the insurance row; not a separate row.

### Open PRs checked

- #10070: gambling winnings into federal gross income, with `pa_gambling_loss_offset` added to the nontaxable list. Covers the gambling row.
- #10727: adds `taxable_strike_benefits` to Pennsylvania's nontaxable list (strike benefits are excluded by clause (vi)); no gap results.
- #10696 / #10722: keep railroad benefits out of Pennsylvania taxable income; consistent with the "Do not include" list.
- #10043: changes `pa_tax_forgiveness_*` for filers who can be claimed as dependents; it does not change the income list.
- No open issue found for Pennsylvania tax forgiveness, alimony or retirement contributions.

### Tests

`tests-C/pa_eligibility_income.yaml`: 6 cases (Treasury interest; alimony once; life insurance; scholarships; cash from relatives; 401(k) contribution, which also asserts `pa_total_taxable_income`).

### Not verified

- 61 Pa. Code regulations on poverty income were not opened.
- The PA Personal Income Tax Guide chapter on tax forgiveness was downloaded (`src/pa_pitguide_taxforgiveness.pdf`) but not read beyond confirming the file; the rows rest on the statute and the 2025 Schedule SP instructions.

## 5. Rhode Island property tax relief household income

### What PolicyEngine does

- `parameters/gov/states/ri/tax/income/credits/property_tax/income_sources.yaml` (from 2021): `adjusted_gross_income`, `tax_exempt_pension_income`, `tax_exempt_interest_income`, `tax_exempt_social_security`, `tax_exempt_unemployment_compensation`, `alimony_income`, `tanf`, `child_support_received`, `workers_compensation`.
- `variables/gov/states/ri/tax/income/credits/property_tax/ri_property_tax_household_income.py` (TaxUnit): `adds` over that list. Person-level sources are summed over all tax unit members, dependents included. `tanf` is an SPM unit amount mapped to the tax unit. `adjusted_gross_income` is the head's and spouse's, net of losses (`loss_ald`) and other above-the-line deductions.
- Readers: `ri_property_tax_credit_eligible` (income at or under the top threshold) and `ri_property_tax_credit` (the percentage-of-income threshold).

### What the law says

- R.I. Gen. Laws 44-33-3 (webserver.rilegislature.gov, `src/ri_gl_44-33-3.txt`):
  - (5) "\"Household\" means one or more persons occupying a dwelling unit and living as a single nonprofit housekeeping unit. \"Household\" shall not include bona fide lessees, tenants, or roomers, and boarders on contract."
  - (6) "\"Household income\" means all income received by all persons of a household in a calendar year while members of the household."
  - (7) "\"Income\" means the sum of federal adjusted gross income as defined in the Internal Revenue Code of the United States, 26 U.S.C. § 1 et seq., and all non-taxable income including, but not limited to, the amount of capital gains excluded from adjusted gross income, alimony, support money, non-taxable strike benefits, cash public assistance and relief (not including relief granted under this chapter), the gross amount of any pension or annuity (including Railroad Retirement Act ... benefits, all payments received under the federal Social Security Act, ... state unemployment insurance laws, and veterans' disability pensions ...), non-taxable interest received from the federal government or any of its instrumentalities, workers' compensation, and the gross amount of \"loss of time\" insurance. It shall not include gifts from nongovernmental sources, or surplus foods or other relief in kind supplied by a public or private agency. For the purpose of this chapter, the calculation of \"income\" shall not include any deductions for rental losses, business losses, capital losses, exclusion for foreign income, and any losses received from pass-through entities."
- 2025 Form RI-1040H (`src/ri_1040h_2025.pdf`, file p. 2), Part 5 "ENTER ALL INCOME RECEIVED BY YOU AND ALL OTHER PERSONS LIVING IN YOUR HOUSEHOLD": lines 14-25 follow the federal return (line 15 "Interest and dividends (taxable and nontaxable)", line 17 alimony from Schedule 1 line 2a, line 20 "IRA distributions, and pensions and annuities from Federal Form 1040 or 1040-SR, line 4a and 5a", line 24 "Social security benefits (including Medicare premiums) taxable and nontaxable, and Railroad Retirement Benefits"), line 27 "Deductions from Federal Form 1040 or 1040-SR, line 10", line 29 "Cash public assistance received", line 30 "Other non-taxable income including child support, worker's compensation and monetary gifts", line 31 "Addback of rental losses, etc. from lines 18, 19, 21, 22 or 25 above", line 32 total. The income limit on the 2025 form is $40,730.

### Differences

| Category | Law | PolicyEngine | Class |
|---|---|---|---|
| Business, rental, capital, pass-through losses | No deduction; added back on line 31 | Deducted through federal AGI | CONFIRMED, undercount |
| Section 911 exclusion | No "exclusion for foreign income" | Not added back | CONFIRMED, undercount |
| Alimony, pre-2019 divorce | Once | In AGI and again as `alimony_income` | CONFIRMED, overcount |
| Other household members | All persons of the household | One tax unit; dependents' non-benefit income dropped | CONFIRMED, undercount |
| SSI, general assistance, state supplement | Counted | Only `tanf` | CONFIRMED, undercount |
| Veterans' disability pensions | Counted | `veterans_benefits` not listed | CONFIRMED, undercount |
| Nontaxable retirement account distributions | Gross amount (lines 4a, 5a) | `tax_exempt_retirement_distributions` not listed | CONFIRMED, undercount |
| Loss-of-time insurance | Gross amount | `tax_exempt_disability_benefits` not listed | CONFIRMED, undercount |
| Nontaxable strike benefits | Counted | Not listed | CONFIRMED, undercount |
| Railroad retirement | Counted | Not listed on main | COVERED (#10722) |
| Gambling winnings | In AGI | Not in federal gross income on main | COVERED (#10070) |

Matches: federal AGI items with federal adjustments; Social Security in full, dependents' included; nontaxable pensions; tax-exempt interest; unemployment; child support; workers' compensation; TANF.

### Two readings

- **Reach of "all non-taxable income including, but not limited to".** Read broadly, scholarships, grants and life insurance proceeds count. Read by the company the phrase keeps, only recurring cash support and benefits count. The form's catch-all (line 30) names child support, workers' compensation and gifts. PolicyEngine counts none of the unnamed items.
- **Statute against form, resolved the statute's way.** The statute excludes "gifts from nongovernmental sources"; form line 30 asks for "monetary gifts". PolicyEngine counts no gifts, which is the statute's rule. Following the form would need a source-conflict register entry.

### Open PRs checked

- #10722: adds the tax-exempt railroad tiers to the source list. Covers railroad benefits.
- #10647: adds `ri_property_tax_household_income.yaml` with a case that keeps a dependent's Social Security in household income; no change to the list.
- #10070 (gambling winnings in AGI) and #10727 (strike benefits other than gifts in AGI) change what federal AGI holds.
- No open issue found for the RI-1040H income definition.

### Tests

`tests-C/ri_property_tax_household_income.yaml`: 9 cases (business loss; capital loss; alimony once; veterans' benefits; Roth IRA distribution; general assistance; tax-exempt disability benefits; section 911 income; second tax unit in the household). No SSI case: `ssi` is a monthly computed variable.

### Not verified

- The Division of Taxation regulation on property tax relief (280-RICR-20-55-?) was not looked for.
- The 2025 Form RI-1040H has no separate instruction booklet in the file I read; its page 3 definitions are the only agency text used.

## 6. Vermont renter credit income

### What PolicyEngine does

- `variables/gov/states/vt/tax/income/credits/renter/vt_renter_credit_income.py` (TaxUnit): `adds = ["adjusted_gross_income", "vt_renter_credit_countable_tax_exempt_ss", "tax_exempt_interest_income"]`. No source-list parameter.
- `vt_renter_credit_countable_tax_exempt_ss` = `tax_exempt_social_security` x `gov.states.vt.tax.income.credits.renter.countable_tax_exempt_ss_fraction` (0.75 from 2021). `tax_exempt_social_security` is every tax unit member's Social Security, dependents included, less the taxable part.
- `adjusted_gross_income` is after above-the-line deductions, including `loss_ald` (business losses and up to $3,000 of net capital loss).
- Reader: `vt_renter_credit` (full credit under the extremely low income limit, phase-out to the very low income limit). `vt_renter_credit_eligible` has no income test.

### What the law says

- 32 V.S.A. 6061(18) (legislature.vermont.gov, `src/vt_32vsa_6061.txt`): "Notwithstanding subdivisions (4) and (5) of this section, for the purposes of the renter credit, \"income\" means federal adjusted gross income increased by the following: (A) trade or business loss from a sole proprietorship, loss from a partnership, loss from a limited liability company or \"subchapter S\" corporation, loss from a rental property, capital loss, loss from an estate or trust, loss from a real estate mortgage investment conduit, farm rental loss, any loss associated with the sale of business property, and farm losses included in adjusted gross income; (B) exempt interest received or accrued during the taxable year; (C) 75 percent of the portion of Social Security benefits as defined under 26 U.S.C. § 86(d) that is excluded from gross income under 26 U.S.C. § 86 for the taxable year; and (D) to the extent excluded from federal adjusted gross income, educator expenses; certain business expenses of reservists, performing artists, and fee-basis government officials; health savings account deductions; moving expenses for members of the U.S. Armed Forces; the deductible part of self-employment tax; self-employed SEP, SIMPLE, and qualified plan deductions; self-employed health insurance deductions; the penalty for early withdrawal of savings; alimony paid; certain IRA retirement savings deductions; student loan interest deductions; and tuition and fees deductions."
- 32 V.S.A. 6066(b)(1) (`src/vt_32vsa_6066.txt`): the credit depends on "the claimant's income" against the extremely low and very low income limits.
- 2025 Form RCC-146 (`src/vt_rcc146_2025.pdf`, file p. 1): "10. Total Income (from federal Form 1040, Line 9)"; "11. 75% of nontaxable Social Security benefits (from federal Form 1040, Line 6a minus Line 6b. Multiply result by 0.75)"; "12. Tax-exempt interest (from federal Form 1040, Line 2a)"; "13. Add back any negative amounts from federal Form 1040, Line 7 and Schedule 1, Lines 3, 4, 5, 6, and 8a"; "14. Total (ADD Lines 10 through 13)".
- 2025 Income Tax Return Booklet (`src/vt_income_booklet_2025.pdf`, file p. 38), line 13: "Loss would include business loss, capital loss, net operating losses including carryforward NOL, trust and estate loss, sale of business personal property loss and farm losses."

The household income and modified adjusted gross income definitions in 6061(4) and (5), with their long list of nontaxable add-backs, apply to the homestead property tax credit (Schedule HI-144), not to the renter credit: (18) opens with "Notwithstanding subdivisions (4) and (5)".

### Differences

| Category | Law | PolicyEngine | Class |
|---|---|---|---|
| Above-the-line deductions | Added back (start from federal total income) | Left out (starts from AGI) | CONFIRMED, undercount |
| Losses | Added back | Left in AGI | CONFIRMED, undercount |
| Dependent's Social Security | Not the claimant's income | 75% counted | CONFIRMED, overcount |
| Tier 1 railroad benefits | 75% of the excluded part | Not counted on main | COVERED (#10722) |
| Gambling winnings | In AGI | Not in federal gross income on main | COVERED (#10070) |

Matches: positive federal income items, tax-exempt interest, 75% of the filers' nontaxable Social Security, the claimant's return as the unit.

Both undercounts have one fix: start from federal gross income (PolicyEngine's `adjusted_gross_income + above_the_line_deductions`, which already floors each source at zero) for the adjustments subdivision (D) lists.

### Two readings

- **SSI (statute against form).** The statute counts Social Security benefits "as defined under 26 U.S.C. § 86(d)", which leaves SSI out. The booklet's line 11 instruction for claimants who did not file a federal return counts 75% of "all payments received under the federal Social Security Act, including ... supplemental security income". PolicyEngine counts no SSI, which is the statute's rule.
- **Adjustments not named in (D).** The form's line 10 (federal total income) is before every Schedule 1 adjustment; the statute lists specific ones. For the adjustments PolicyEngine models, the two agree except for amounts that are exclusions rather than deductions (`us_bonds_for_higher_ed`, `qualified_adoption_assistance_expense`, possession and Puerto Rico income), which are in PolicyEngine's deduction list but in neither the statute's list nor Form 1040 line 9. Not a separate row.

### Open PRs checked

- #10722: adds the tax-exempt tier 1 railroad benefit to the 75% base. Covers railroad benefits.
- #10647: its body names the Vermont renter credit among readers of `tax_exempt_social_security` to review, but the diff does not touch Vermont, so the dependent's-benefits overcount is not covered.
- #10070: gambling winnings enter federal AGI.
- #10116 (county lookup guard) does not touch income.

### Tests

`tests-C/vt_renter_credit_income.yaml`: 4 cases (early withdrawal penalty added back; business loss; capital loss; dependent child's Social Security).

### Not verified

- The Schedule HI-144 household income definition (6061(4), (5)) was read but not audited against PolicyEngine: no PolicyEngine variable in this batch reads it.
- Whether spouses filing separately and living together must combine income for the renter credit was not found in the text read.
