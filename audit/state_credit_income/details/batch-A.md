# Batch A — state credit income definitions (MI, MN, WI)

Audited against upstream/main 06c0dcbc54 (2026-11-11). Read-only; no tests run.

## Findings

| State | Credit | Finding | Class | Dollar direction |
|---|---|---|---|---|
| MI | Homestead property tax credit; home heating credit | IRA, 401(k), 403(b), SEP and Keogh distributions (`taxable_retirement_distributions`) are not in total household resources; MI-1040CR line 18 counts "all annuity, retirement, pension and individual retirement account (IRA) benefits" | CONFIRMED | Resources too low, credits too high |
| MI | Homestead property tax credit; home heating credit | Military retired pay and survivor annuities (`military_retirement_income`) are not counted; "Veterans receiving retirement benefits should enter the benefits on line 18" (same failure as #10769) | CONFIRMED | Resources too low, credits too high |
| MI | Homestead property tax credit; home heating credit | Taxable Roth conversions (`taxable_roth_conversions`) are in federal AGI but not counted | CONFIRMED | Resources too low, credits too high |
| MI | Homestead property tax credit; home heating credit | Forgiven debt (`debt_relief`) is in federal AGI and on lines 20 and 25, but not counted | CONFIRMED | Resources too low, credits too high |
| MI | Homestead property tax credit; home heating credit | Employer dependent care benefits are subtracted from wages (`irs_employment_income`) and never added back, though "Reimbursement from dependent care and/or medical care spending accounts" counts | CONFIRMED | Resources too low, credits too high |
| MI | Homestead property tax credit; home heating credit | Non-Social Security survivor benefits (`survivor_benefits`) are not counted (check the data mapping before fixing) | CONFIRMED | Resources too low, credits too high |
| MI | Homestead property tax credit; home heating credit | `illicit_income`, a federal AGI source, is not counted (immaterial) | CONFIRMED | Resources too low, credits too high |
| MI | Homestead property tax credit; home heating credit | Foreign earned income excluded under IRC 911 (`section_911_excluded_income`) is not added, though RAB 2015-18 counts it (rare) | CONFIRMED | Resources too low, credits too high |
| MI | Homestead property tax credit; home heating credit | The premium deduction (MCL 206.510(1), line 31) reads only the direct `health_insurance_premiums` input; premiums in `health_insurance_premiums_without_medicare_part_b` are never subtracted | CONFIRMED | Resources too high, credits too low |
| MI | Homestead property tax credit; home heating credit | Medicare premiums withheld from Social Security (excluded by MCL 206.510(1)(h)) come off only if supplied in `health_insurance_premiums`; the modeled Part B premium is never subtracted | CONFIRMED | Resources too high, credits too low |
| MI | Homestead property tax credit; home heating credit | Nontaxable pension amounts: PE counts all of `tax_exempt_pension_income`; the form and RAB 2015-18 count pensions only "to the extent they are included in AGI", Treasury's web page says "include nontaxable pensions" | TWO-READINGS | Under the form's reading, resources too high |
| MI | Homestead property tax credit; home heating credit | Alimony: PE counts all `alimony_income`; the form counts it only "if due to a divorce granted prior to 2019" | TWO-READINGS | Under the form's reading, resources too high |
| MI | Homestead property tax credit; home heating credit | Social Security and SSI received for minor children or dependent adults: the form and RAB count them, PE follows MCL 206.508(3) ("a claimant and spouse") and leaves them out (#10325) | TWO-READINGS | Under the agency's reading, resources too low |
| MI | Homestead property tax credit; home heating credit | Taxable state and city income tax refunds: in federal AGI where the statute starts, excluded by the agency; PE excludes | TWO-READINGS | Under the statute-only reading, resources too low |
| MI | Homestead property tax credit; home heating credit | No input: excluded home-sale gain, Roth earnings above contributions, foster parent payments, inheritances and non-spouse life insurance, nongovernmental scholarships | NOT-MODELABLE | Resources too low |
| MN | Renter's credit | Household income sums the AGI of every non-dependent adult in the SPM unit; the statute counts only the claimant and spouse ("The income of each renter shall be each renter's household income") | CONFIRMED | Income too high, credit too low for renters living with other adults |
| MN | Homestead credit refund | SSI is not added (290A.03, subd. 3(a)(2)(v); M1PR line 4) | CONFIRMED | Income too low, refund too high |
| MN | Homestead credit refund | Cash public assistance (`tanf`, `general_assistance`) is not added (subd. 3(a)(2)(iv); line 4) | CONFIRMED | Income too low, refund too high |
| MN | Homestead credit refund | Workers' compensation is not added (subd. 3(a)(2)(vii)) | CONFIRMED | Income too low, refund too high |
| MN | Homestead credit refund | Tax-exempt interest is not added (subd. 3(a)(2)(vi)) | CONFIRMED | Income too low, refund too high |
| MN | Homestead credit refund | Nontaxable pension and annuity payments (`tax_exempt_pension_income`) are not added (subd. 3(a)(2)(v)); the countable share depends on who funded the plan | CONFIRMED | Income too low, refund too high |
| MN | Homestead credit refund | Retirement distributions outside AGI, Roth included (`tax_exempt_retirement_distributions`), are not added (subd. 3(a)(2)(xii)) | CONFIRMED | Income too low, refund too high |
| MN | Homestead credit refund | Alimony outside AGI is not added (subd. 3(a)(2)(xiv)) | CONFIRMED | Income too low, refund too high |
| MN | Homestead credit refund | Nontaxable disability income (`tax_exempt_disability_benefits`) and strike benefits are not added (subd. 3(a)(2)(viii)-(ix)) | CONFIRMED | Income too low, refund too high |
| MN | Homestead credit refund | Nontaxable scholarships (`educational_assistance`) are not added (subd. 3(a)(2)(xiii)); check the input | CONFIRMED | Income too low, refund too high |
| MN | Homestead credit refund | The HSA deduction and the educator expense deduction are not added back (subd. 3(a)(2)(xv), (xvii)) | CONFIRMED | Income too low, refund too high |
| MN | Homestead credit refund | Excluded employer dependent care benefits and the foreign earned income exclusion are not added (subd. 3(a)(2)(i); line 6) | CONFIRMED | Income too low, refund too high |
| MN | Homestead credit refund | Co-occupants' income is not counted (290A.05(a); line 5); documented in the variable | CONFIRMED | Income too low, refund too high |
| MN | Homestead credit refund | The retirement base amount stays at $7,000 / $14,000 in 2026; section 219(b)(5)(A) is $7,500 for 2026 (Notice 2025-67) | CONFIRMED | Income too high by up to $500 ($1,000 joint), refund too low, 2026 on |
| MN | Homestead credit refund | Nontaxable railroad retirement benefits are not added | COVERED (#10722) | Income too low, refund too high |
| MN | Both | Gambling winnings are missing from federal AGI on main, so from both definitions | COVERED (#10070) | Income too low, credits too high |
| MN | Homestead credit refund | Survivor benefits: the M1PR's "Do not include" list names them; the statute counts nontaxable pensions and annuities. PE counts none | TWO-READINGS | Under the statute's reading, income too low |
| MN | Both | No input: veterans' pension apart from disability compensation, excluded home-sale gain, foster care payments, housing allowances, loss carryforwards, SEIU stipends, part-year residency | NOT-MODELABLE | Mixed |
| WI | Homestead credit | Household income starts from federal AGI, not Wisconsin AGI, so the medical care and long-term care insurance subtraction (Schedule H line 8c), the state tax refund subtraction and other Schedule SB subtractions the statute does not add back are never taken off; the instructions' Example 1 gives 10,765 where PE gives 12,500 | CONFIRMED | Income too high, credit too low (mostly Medicare-age claimants) |
| WI | Homestead credit | Child support is not counted (71.52(6) "support money"; line 9i) | CONFIRMED | Income too low, credit too high |
| WI | Homestead credit | Maintenance outside federal AGI is not counted (line 9i) | CONFIRMED | Income too low, credit too high |
| WI | Homestead credit | Workers' compensation and nontaxable loss-of-time insurance are not counted (71.52(6); line 11b) | CONFIRMED | Income too low, credit too high |
| WI | Homestead credit | Veterans' benefits are not counted (71.52(6); lines 9d, 9h) | CONFIRMED | Income too low, credit too high |
| WI | Homestead credit | Pre-tax 401(k)/403(b) deferrals and deductible IRA, SEP and Keogh contributions are not added back (71.52(6); lines 9e, 9f) | CONFIRMED | Income too low, credit too high |
| WI | Homestead credit | Nontaxable IRA and plan distributions (`tax_exempt_retirement_distributions`) are not counted (line 9d) | CONFIRMED | Income too low, credit too high |
| WI | Homestead credit | County relief and other cash assistance (`general_assistance`), nontaxable scholarships (`educational_assistance`) and non-Social Security survivor benefits are not counted; check the last two inputs | CONFIRMED | Income too low, credit too high |
| WI | Homestead credit | Earned income test counts S corporation income (`partnership_s_corp_income`); 71.52(1g) counts wages and net earnings from self-employment | CONFIRMED | Eligibility too wide (narrow case) |
| WI | Homestead credit | Railroad retirement benefits are not counted | COVERED (#10722) | Income too low, credit too high |
| WI | Homestead credit | Gambling winnings are missing from federal AGI on main (also affects both Minnesota definitions) | COVERED (#10070) | Income too low, credit too high |
| WI | Homestead credit | No input: the 71.55(10) small-farmer exception to the loss add-back, depreciation add-backs, excluded home-sale gain, nontaxable military pay, loss carryforwards, repayments other than Social Security | NOT-MODELABLE | Mixed |

## 1. Michigan — total household resources (`mi_household_resources`)

### What PolicyEngine does

- **Files.** `parameters/gov/states/mi/tax/income/household_resources.yaml` (income list), `household_resources_all_members.yaml` (sources summed over every member), `household_resources_adjustments.yaml` (Schedule 1 adjustments), `household_resources_gambling_exclusion.yaml` and `household_resources_gift_exclusion.yaml` ($300 each), and `variables/gov/states/mi/tax/income/mi_household_resources.py`.
- **Entity and members.** Tax unit. Each source is summed over the head and spouse (`tax_unit_non_dep_add`); `child_support_received`, `tanf` and `general_assistance` are summed over every member.
- **Income list (2021 on).** `irs_employment_income`, `strike_benefits`, `dividend_income`, `interest_income`, `farm_operations_income`, `total_self_employment_income`, `partnership_s_corp_income`, `estate_income`, `other_net_gain`, `rental_income`, `farm_rent_income`, `pension_income`, `retirement_benefits_from_ss_exempt_employment`, `filer_loss_limited_net_capital_gains`, `alimony_income`, `gambling_winnings`, `miscellaneous_income`, `social_security`, `ssi`, `railroad_benefits`, `child_support_received`, `total_unemployment_compensation`, `financial_assistance`, `veterans_benefits`, `workers_compensation`, `disability_benefits`, `gi_cash_assistance`, `tanf`, `general_assistance`.
- **Loss floors.** Business sources (self-employment, Form 4797 gain, partnership/S corp, estate, farm) are netted and floored at zero as a group; so are rental and farm rent. Capital losses are limited to $3,000 ($1,500 separate). Gambling winnings and gifts each lose the first $300.
- **Subtractions.** Nine federal above-the-line deductions (line 30) and `health_insurance_premiums` of the head and spouse (line 31), less premiums already in the self-employed health insurance deduction. The result is floored at zero.
- **What the names hold.** `pension_income` = taxable + tax-exempt pension income; it does not include `taxable_retirement_distributions` (IRA, 401(k), 403(b), SEP, Keogh), `taxable_roth_conversions` or `military_retirement_income`, all of which are separate federal gross income sources (`gov.irs.gross_income.sources`). `irs_employment_income` = `employment_income` less pre-tax 401(k)/403(b) deferrals, pre-tax health premiums, HSA payroll contributions and `dependent_care_employer_benefits`. `interest_income` includes tax-exempt interest. `social_security` is gross.
- **Readers.** Home heating credit: `mi_standard_home_heating_credit`, `mi_standard_home_heating_credit_eligible`, `mi_alternate_home_heating_credit`, `mi_alternate_home_heating_credit_eligible`. Homestead property tax credit: `mi_homestead_property_tax_credit_eligible`, `mi_allowable_homestead_property_tax_credit`, `mi_homestead_property_tax_credit_household_resource_exemption`, `mi_homestead_property_tax_credit_pre_alternate_senior_amount`, `mi_homestead_property_tax_credit_alternate_senior_amount`.

### What the law says

- **MCL 206.508(3)-(4)** ([legislature.mi.gov](https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-206-508)): "'Household' means a claimant and spouse." "'Total household resources' means all income received by all persons of a household in a tax year while members of a household, ... and increased by the following deductions from federal gross income: (a) Any net business loss after netting all business income and loss. (b) Any net rental or royalty loss. (c) Any carryback or carryforward of a net operating loss".
- **MCL 206.510(1)** ([legislature.mi.gov](https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-206-510)): "'Income' means the sum of federal adjusted gross income as defined in the internal revenue code plus all income specifically excluded or exempt from the computations of the federal adjusted gross income. Also, a person who is enrolled in an accident or health insurance plan may deduct from income the amount that person paid in premiums in the tax year for that insurance plan for the person's family." Income does not include "(a) The first $300.00 of gifts in cash or kind from nongovernmental sources", "(b) The first $300.00 received from awards, prizes, lottery, bingo, or other gambling winnings", "(c) Surplus foods", "(d) Relief in kind supplied by a governmental agency", "(e) Payments or credits under this part", "(h) Amounts deducted from monthly social security or railroad retirement benefits for medicare premiums", "(i) Contributions by an employer to life, accident, or health insurance plans", "(j) Energy assistance grants and energy assistance tax credits".
- **2025 MI-1040 book** ([PDF](https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf#page=26), file pages 26-27 and 31-33):
  - p. 26: "They are AGI, excluding net business and farm losses, net rent and royalty losses, and any carryover of a net operating loss, plus all income exempt or excluded from AGI." Items not on the form include "Forgiveness of debt, even if excluded from AGI" and "Reimbursement from dependent care and/or medical care spending accounts".
  - p. 27 (not included): "State and city income tax refunds and homestead property tax credits", "Surplus food or food assistance program benefits", "Amounts deducted from Social Security or Railroad Retirement benefits for Medicare premiums".
  - p. 32, line 18: "Enter all annuity, retirement, pension and individual retirement account (IRA) benefits. This should be the taxable amount shown on your U.S. Form 1099-R. ... Do not include recoveries of after-tax contributions or amounts rolled over into another plan (amounts rolled over into a Roth IRA must be included to the extent included in AGI). You must include any part of a distribution from a Roth IRA that exceeds your total contributions".
  - p. 32, line 20: "Only include alimony received if due to a divorce granted prior to 2019. Other taxable income includes: ... forgiveness of debt to the extent included in federal AGI".
  - p. 32, line 21: "Include death benefits and amounts received for minor children or other dependent adults who live with you. ... Medicare premiums reported on your Social Security or Railroad Retirement statement should be deducted."
  - p. 32, line 26: "Veterans receiving retirement benefits should enter the benefits on line 18."
  - p. 32-33, line 31: premiums "you paid for yourself and your family"; "Do not include ... amounts paid by an employer with pre-tax payroll contributions."
- **2025 MI-1040CR-7 book** (file pages 4, 8-9): the home heating credit uses the same definition on its lines 17 to 33, with the same wording on the points above (line 21 for pensions, 23 for alimony, 24 for Social Security, 29 for veterans, 33 for premiums).
- **Revenue Administrative Bulletin 2015-18** ([michigan.gov](https://www.michigan.gov/taxes/rep-legal/rab/2015-revenue-administrative-bulletins/revenue-administrative-bulletin-2015-18)): included income lists "Retirement pension income, annuity benefits, and IRA and deferred compensation distributions to the extent they are included in AGI", "Rollovers from a traditional IRA to a Roth IRA in the year the income is included in AGI", "Forgiveness of debt, even if excluded from AGI", "Reimbursement from dependent care and/or medical care spending accounts", "Foreign earned income excluded from federal gross income". Its worked example subtracts a $600 state tax refund from AGI.
- **Treasury's Total Household Resources page** ([michigan.gov](https://www.michigan.gov/taxes/iit/tax-guidance/total-household-resources)): "Pension (include nontaxable pensions)", "Cancelled debt income", "Foster care payments", "Adoption subsidy payments".

### Differences

| Category | Law | PE | Status |
|---|---|---|---|
| IRA/401(k)/403(b)/SEP/Keogh distributions (taxable) | counted (line 18; in AGI) | not counted | CONFIRMED undercount |
| Military retired pay, survivor annuities | counted (line 18 via line 26 note) | not counted | CONFIRMED undercount |
| Taxable Roth conversions | counted (line 18; in AGI) | not counted | CONFIRMED undercount |
| Forgiven debt | counted (lines 20 and 25) | not counted | CONFIRMED undercount |
| Employer dependent care benefits | counted (p. 26; taxable part in AGI) | subtracted from wages, never added back | CONFIRMED undercount |
| Non-Social Security survivor benefits | counted (lines 18, 25) | not counted | CONFIRMED undercount (check what the data put in `survivor_benefits`) |
| `illicit_income` | in AGI | not counted | CONFIRMED undercount, immaterial |
| Foreign earned income excluded under IRC 911 | counted (RAB 2015-18, citing DeKoning) | not counted: PE income inputs are net of the exclusion and `section_911_excluded_income` is not added | CONFIRMED undercount, rare |
| Premiums paid (line 31) | deductible | only the direct `health_insurance_premiums` input | CONFIRMED overcount |
| Medicare premiums withheld | excluded (510(1)(h)) | subtracted only when supplied directly | CONFIRMED overcount |
| Nontaxable pension amounts | form: taxable amount only; web page: include nontaxable pensions | all counted | TWO-READINGS |
| Alimony | form: pre-2019 divorces only | all counted | TWO-READINGS |
| Social Security/SSI for dependents | agency counts; statute's household is claimant and spouse | not counted (#10325) | TWO-READINGS |
| Taxable state tax refunds | in AGI; agency excludes | not counted | TWO-READINGS |

Everything else in the CSV matches: wages, business and rental netting, interest (taxable and exempt), dividends, capital gains, Social Security, SSI, railroad retirement, veterans' benefits, unemployment, workers' compensation, FIP and other public assistance, child support, the two $300 exclusions, the SNAP and energy-assistance exclusions, the Schedule 1 adjustments, the claimant-and-spouse rule and the tax-year period. Michigan has no receipt-timing rule for refundable credits: its own credits are excluded by 510(1)(e), and no source lists federal credits.

**The premium finding in detail.** `mi_household_resources` subtracts `health_insurance_premiums`. That input's source comment says survey data fill it "only for self-employed people under 65 without employer-sponsored coverage"; reported after-tax premiums sit in `health_insurance_premiums_without_medicare_part_b`, and a Medicare enrollee's Part B premium is modeled in `medicare_part_b_premium`. `medical_expense_health_insurance_premiums` combines the channels (the direct input if nonzero, otherwise the decomposed amounts) and excludes pre-tax payroll premiums, which is what line 31 asks for. The existing YAML case "Medicare premiums withheld from Social Security are subtracted once" passes only because it supplies the premium in the direct input. I wrote a test for the after-tax premium channel but none for the modeled Part B premium, because I could not verify its default enrollment and amount without running the model.

### Tests written

`C:/tmp/sci-audit/tests-A/mi_household_resources.yaml`: seven cases (IRA and 401(k) distributions, military retired pay, Roth conversion, forgiven debt, dependent care benefits, survivor benefits, after-tax premiums).

### Open PRs and issues checked

Searched open PRs for "Michigan household resources", "mi_household_resources", "Michigan homestead", "Michigan home heating", "Michigan pension household", "Michigan military retirement", and open issues for the first two. None touches the household resources files. #10722 (railroad benefits), #10070 (gambling winnings), #10714 (veteran exemption) and #10769 (NM/OK) touch other Michigan files or no Michigan file. Merged: #9790, #9795, #9796, #9840, #10325.

### Two-reading notes

- **Nontaxable pensions.** The line 18 instruction and RAB 2015-18 limit pensions to the amount in AGI; Treasury's web page and the statute's "all income specifically excluded or exempt" point the other way for pension income that is exempt rather than a return of contributions. PE's `tax_exempt_pension_income` does not separate the two, and PE counts all of it.
- **Alimony.** The statute counts income excluded from AGI; the 2025 form counts alimony only for pre-2019 divorces. The agency follows the form. PE counts all `alimony_income`; `taxable_alimony_income` would match the form.
- **Dependents' Social Security and SSI.** The agency counts amounts received for minor children and dependent adults; PE reads the statute's household definition as controlling and says so in the formula.
- **State tax refunds.** The statute starts from federal AGI, which includes a taxable refund; the agency excludes refunds (RAB cites Rule 206.4(1)(n)). PE follows the agency.

### Not verified

- Mich Admin Code R 206.4 (cited by RAB 2015-18) was not opened; I relied on the RAB's description of it.
- The MI-1040CR and MI-1040CR-7 form pages themselves were not in the instruction books I read; line wording comes from the instructions and the RAB.
- What the microdata put in `survivor_benefits` and whether any of it is also in `taxable_pension_income`.
- The default value of the modeled Medicare Part B premium and enrollment.

## 2. Minnesota — household income (`mn_renters_credit_household_income`, `mn_homestead_credit_refund_household_income`)

Minnesota now has two definitions. From tax year 2024 the renter's credit is an income tax credit under Minn. Stat. 290.0693, with income equal to adjusted gross income less subtractions. The homeowner refund stays under chapter 290A, whose "income" is AGI plus a long list of nontaxable items.

### What PolicyEngine does

**Renter's credit.** `variables/gov/states/mn/tax/income/credits/mn_renters_credit_household_income.py` (tax unit) reads `mn_renters_credit_household_agi` (SPM unit).
- `mn_renters_credit_household_agi` sums `adjusted_gross_income_person` over every person in the SPM unit who is not a tax unit dependent and not claimed on another return. That reaches across tax units, so an unmarried partner, adult child or parent in the same SPM unit is included.
- A separate filer adds `spouse_separate_adjusted_gross_income`, a proxy equal to the filer's own AGI.
- Subtractions: the exemption amount if the head or spouse is 65 or disabled, and the exemption amount times 1.4 / 2.7 / 3.9 / 5 / 6 for one to five dependents. Floor at zero.
- No nontaxable income is added. Losses follow federal AGI.
- Readers: `mn_renters_credit`, `mn_renters_credit_eligible`.

**Homestead credit refund.** `variables/gov/states/mn/tax/property/homestead_credit_refund/mn_homestead_credit_refund_household_income.py` (tax unit), with `parameters/gov/states/mn/tax/property/homestead_credit_refund/retirement_subtraction/limit.yaml`.
- `adjusted_gross_income` (plus the same separate-filer proxy);
- plus nontaxable Social Security of non-dependents (`social_security` less `taxable_social_security`);
- plus `traditional_401k_contributions`, `traditional_403b_contributions`, `traditional_ira_deduction` and `self_employed_pension_contributions` of the head and spouse;
- less the age-or-disability and dependent subtractions, and a retirement subtraction of min(all traditional and Roth contributions, compensation, $7,000 or $14,000 joint).
- Its documentation says "Co-occupant income and other nontaxable additions or subtractions are not separately modeled."
- Readers: `mn_homestead_credit_refund`, `mn_homestead_credit_refund_eligible`.

### What the law says

**Renter's credit — Minn. Stat. 290.0693** ([revisor.mn.gov](https://www.revisor.mn.gov/statutes/cite/290.0693)):
- Subd. 1(g): "'Household' has the meaning given in section 290A.03, subdivision 4", which is "a claimant and an individual related to the claimant as the claimant's spouse who are domiciled in the same homestead."
- Subd. 1(h): "'Household income' means all income received by all persons of a household in a taxable year while members of the household, other than income of a dependent."
- Subd. 1(i): "'Income' means adjusted gross income, minus" the dependent amounts and, "if the taxpayer or taxpayer's spouse had a disability or attained the age of 65 on or before the close of the taxable year, the exemption amount."
- Subd. 7: "If a homestead is occupied by two or more renters who are not married to each other, the rent shall be deemed to be paid equally by each renter, and separate claims shall be filed by each renter. The income of each renter shall be each renter's household income for purposes of computing the amount of credit to be allowed."
- [2025 Schedule M1RENT](https://www.revenue.state.mn.us/sites/default/files/2026-07/m1rent-25.pdf#page=3), file p. 3: "Lived with a roommate ... Include only your income when filing for the credit." P. 4, line 1: "Do not include your nontaxable income on line 1."

**Homestead credit refund — Minn. Stat. 290A.03, subd. 3 to 5, and 290A.05** ([290A.03](https://www.revisor.mn.gov/statutes/cite/290A.03), [290A.05](https://www.revisor.mn.gov/statutes/cite/290A.05)):
- Subd. 3(a): "'Income' means the sum of the following: (1) federal adjusted gross income ...; and (2) the sum of the following amounts to the extent not included in clause (1): (i) all nontaxable income; ... (iv) cash public assistance and relief; (v) any pension or annuity (including railroad retirement benefits, all payments received under the federal Social Security Act, Supplemental Security Income, and veterans benefits), which was not exclusively funded by the claimant or spouse ...; (vi) interest received from the federal or a state government ...; (vii) workers' compensation; (viii) nontaxable strike benefits; (ix) the gross amounts of payments received in the nature of disability income or sick pay ...; (xi) contributions made by the claimant to an individual retirement account ... to the extent the sum of amounts exceeds the retirement base amount ...; (xii) to the extent not included in federal adjusted gross income, distributions received by the claimant or spouse from a traditional or Roth style retirement account or plan; (xiii) nontaxable scholarship or fellowship grants; (xiv) alimony received to the extent not included in the recipient's income; (xv) the amount of deduction allowed under section 220 or 223 ...; (xvii) the amount deducted for certain expenses of elementary and secondary school teachers".
- Subd. 3(b): income does not include "(1) amounts excluded pursuant to the Internal Revenue Code, sections 101(a) and 102; (2) amounts of any pension or annuity which was exclusively funded by the claimant or spouse and which funding payments were not excluded from federal adjusted gross income ...; (4) surplus food or other relief in kind supplied by a governmental agency; (5) relief granted under this chapter; (6) child support payments ...; (9) veterans disability compensation paid under title 38".
- Subd. 3(d)(2): "'retirement base amount' means the deductible amount for the taxable year for the claimant and spouse under section 219(b)(5)(A) of the Internal Revenue Code, adjusted for inflation as provided in section 219(b)(5)(C)".
- Subd. 5: "'Household income' means all income received by all persons of a household in a calendar year while members of the household, other than income of a dependent."
- 290A.05(a): if a person "occupies a homestead with another person not related to the person as the person's spouse, excluding dependents, roomers or boarders on contract, and has property tax payable with respect to the homestead, the household income of the claimant ... shall include the total income received by the other persons residing in the homestead."
- [2025 Form M1PR instructions](https://www.revenue.state.mn.us/sites/default/files/2026-06/m1pr-inst-25.pdf#page=7), file pp. 7-9: line 2 (nontaxable Social Security and railroad retirement, "Do not include Social Security income for dependents"), line 4 ("Include nontaxable payments you received from the Minnesota Family Investment Program (MFIP), Minnesota Supplemental Aid (MSA), Supplemental Security Income (SSI), General Assistance (GA) ..."), line 5 (co-occupant income), line 6 (additional nontaxable income: workers' compensation, federally nontaxed interest, nontaxable pensions, Roth and IRA distributions, HSA and educator deductions, foreign earned income exclusion, strike benefits and more). P. 8 "Do not include": child support, gifts and inheritances, "Federal or state tax refunds not included on line 1", "IRS stimulus/rebate", "Minnesota property tax refunds", "Premium tax credit", veterans' disability compensation.
- [IRS Notice 2025-67](https://www.irs.gov/pub/irs-drop/n-25-67.pdf#page=4), file p. 4: "The deductible amount under section 219(b)(5)(A) ... is increased from $7,000 to $7,500."

### Differences

**Renter's credit**

| Category | Law | PE | Status |
|---|---|---|---|
| Other non-dependent adults in the home | not counted (subd. 1(g)-(h), 7) | counted through the SPM-unit sum | CONFIRMED overcount |
| AGI items, nontaxable income, dependents, subtractions | — | — | match |
| SEIU stipend subtraction, part-year residency | counted on the schedule | no input | NOT-MODELABLE |

The existing test "Case 3, other adult household income counts" expects a $10,000 earner and a $60,000 earner in separate tax units to each have $70,000 of household AGI. Under subd. 7 each has only their own.

**Homestead credit refund**

| Category | Law | PE | Status |
|---|---|---|---|
| SSI | counted | not counted | CONFIRMED undercount |
| MFIP, GA and other cash assistance | counted | not counted | CONFIRMED undercount |
| Workers' compensation | counted | not counted | CONFIRMED undercount |
| Tax-exempt interest | counted | not counted | CONFIRMED undercount |
| Nontaxable pensions and annuities | counted unless self-funded with after-tax money | not counted | CONFIRMED undercount (share depends on funding) |
| Retirement distributions outside AGI (Roth) | counted | not counted | CONFIRMED undercount |
| Alimony outside AGI | counted | not counted | CONFIRMED undercount |
| Nontaxable disability income; strike benefits | counted | not counted | CONFIRMED undercount |
| Nontaxable scholarships | counted | not counted | CONFIRMED undercount (check the input) |
| HSA and educator expense deductions | added back | not added back | CONFIRMED undercount |
| Excluded dependent care benefits; foreign earned income exclusion | counted | not counted | CONFIRMED undercount |
| Co-occupant income | counted (290A.05) | not counted | CONFIRMED undercount, documented |
| Retirement base amount, 2026 | $7,500 / $15,000 | $7,000 / $14,000 | CONFIRMED overcount, 2026 on |
| Nontaxable railroad retirement | counted | not counted | COVERED by #10722 |
| Veterans' pension | counted; disability compensation excluded | none counted | NOT-MODELABLE |

AGI, nontaxable Social Security (gross of Medicare premiums), the retirement contribution add-back and subtraction, the age, disability and dependent subtractions, the exclusions for child support, gifts and in-kind aid, and the exclusion of dependents' income all match. Neither definition counts refundable credits or tax refunds beyond what is in AGI, so there is no receipt-timing rule.

One pattern is worth noting: the co-occupant rule is a homeowner rule (290A.05, "has property tax payable with respect to the homestead"). PE applies an other-adults rule to renters, where the law has none, and leaves it out for homeowners, where the law has one.

### Tests written

- `C:/tmp/sci-audit/tests-A/mn_renters_credit_household_income.yaml`: the corrected Case 3.
- `C:/tmp/sci-audit/tests-A/mn_homestead_credit_refund_household_income.yaml`: eight cases (SSI, General Assistance, workers' compensation, tax-exempt interest, Roth IRA distributions, alimony outside AGI, HSA deduction, 2026 retirement base amount).

No test for co-occupant income (it needs a design choice on which household members count), nontaxable pensions (funding is not recorded), the educator deduction (needs eligibility inputs I did not trace) or scholarships.

### Open PRs and issues checked

Searched open PRs for "Minnesota renter", "Minnesota homestead credit refund", "mn_renters_credit", "mn_homestead_credit_refund", "M1PR", "Minnesota household income", and open issues for three of them. Only #10722 touches these files: it adds nontaxable tier 1 railroad benefits and the tax-free part of the tier 2 annuity to the homestead refund's household income. #10070 adds `gambling_winnings` to federal gross income; on main gambling winnings are missing from AGI and so from both Minnesota definitions. Nothing open covers the other gaps.

### Two-reading notes

- **Survivor benefits (homestead credit refund).** The M1PR's "Do not include" list (file p. 8) has the bare entry "Survivor benefits". The statute counts "(i) all nontaxable income" and "(v) any pension or annuity" not funded only by the claimant, which reaches a survivor pension or annuity; subd. 3(b) excludes only life insurance (IRC 101(a)) and veterans' disability compensation among survivor-type payments. PE counts none of `survivor_benefits`: that matches the instruction and undercounts under the statute.

Two further points the sources leave open, without changing a classification:
- **Nontaxable pensions.** Subd. 3(a)(2)(v) counts a pension "not exclusively funded by the claimant or spouse" in full, while the M1PR's do-not-include list has "Annuity payments that are a return of after-tax contributions". For an employer plan with employee after-tax contributions the two differ; PE counts neither, so it undercounts under both.
- **Workers' compensation.** The statute counts it without limit; the M1PR counts it "to the extent not used for medical expenses".

### Not verified

- Whether a separately filing spouse modeled as a second tax unit in the same SPM unit is double counted in the renter's household AGI (SPM-unit sum plus the proxy). I could not run the model.
- The 2026 M1PR and M1RENT are not published; the 2026 retirement base amount rests on the statute and Notice 2025-67.
- The source of the M1RENT line 8 SEIU stipend subtraction; it is not in the 290.0693 text I read.
- What the microdata put in `educational_assistance`.

## 3. Wisconsin — homestead credit household income (`wi_homestead_income`)

Audited as main stands after #10191 (merged 2026-11-10), which limited the household to the claimant and spouse, switched the Social Security source to `filer_tax_exempt_social_security`, kept negative net Social Security as a repayment, and added `wi_ssp`. #9848 (merged 2026-10-08) added the disqualified-loss add-back.

### What PolicyEngine does

- **Files.** `parameters/gov/states/wi/tax/income/credits/homestead/income/sources.yaml`, `income/disqualified_loss_sources.yaml`, `income/exemption.yaml` ($500), `eligible/earnings_sources.yaml`; `variables/gov/states/wi/tax/income/credits/homestead/wi_homestead_income.py`, `wi_homestead_disqualified_losses.py`, `wi_homestead_eligible.py`.
- **Income list (2021 on).** `adjusted_gross_income` (federal), `tax_exempt_interest_income`, `filer_tax_exempt_social_security`, `tax_exempt_pension_income`, `tax_exempt_unemployment_compensation`, `ssi`, `wi_ssp`, `tanf`.
- **Entity and members.** Tax unit; person-level sources are summed over the head and spouse (`tax_unit_non_dep_add`). `tanf` is the SPM unit's.
- **Losses.** `wi_homestead_disqualified_losses` adds back the negative part of each of `self_employment_income`, `sstb_self_employment_income`, `rental_income`, `farm_rent_income`, `estate_income` and `farm_operations_income` for the head and spouse, partnership and S corporation losses separately, a Form 4797 loss (`other_net_gain`) and the filer's net capital loss. So no loss reduces household income.
- **Subtractions.** $500 per tax unit dependent; negative net Social Security (treated as a repayment).
- **Earned income test** (`wi_homestead_eligible`): `irs_employment_income`, `self_employment_income`, `sstb_self_employment_income`, `partnership_s_corp_income`, `farm_operations_income`, summed per person and tested above zero.
- **Readers.** `wi_homestead_credit` and `wi_homestead_eligible` (the $24,680 limit).

### What the law says

- **Wis. Stat. 71.52(4)-(6)** ([docs.legis.wisconsin.gov](https://docs.legis.wisconsin.gov/statutes/statutes/71/viii/52)):
  - (4): "'Household' means a claimant and an individual related to the claimant as husband or wife."
  - (5): "'Household income' means all income received by all persons of a household in a calendar year while members of the household, less $500 for each of the claimant's dependents ... who have the same principal abode as the claimant for more than 6 months".
  - (6): "'Income' means the sum of Wisconsin adjusted gross income and the following amounts, to the extent not included in Wisconsin adjusted gross income: maintenance payments (except foster care maintenance ...), support money, cash public assistance (not including credit granted under this subchapter ...), cash benefits paid by counties under s. 59.53 (21), the gross amount of any pension or annuity (including railroad retirement benefits, all payments received under the federal social security act and veterans disability pensions), nontaxable interest received from the federal government or any of its instrumentalities, nontaxable interest received on state or municipal bonds, worker's compensation, unemployment insurance, the gross amount of 'loss of time' insurance, compensation and other cash benefits received from the United States for past or present service in the armed forces, scholarship and fellowship gifts or income, capital gains, gain on the sale of a personal residence excluded under section 121 ..., dividends, ... nontaxable deferred compensation. Intangible drilling costs, depletion allowances and depreciation, ... amortization, contributions to individual retirement accounts under section 219 ..., contributions to Keogh plans, net operating loss carry-backs and carry-forwards, capital loss carry-forwards, and disqualified losses deducted in determining Wisconsin adjusted gross income shall be added to 'income'. 'Income' does not include gifts from natural persons, cash reimbursement payments made under title XX ..., surplus food or other relief in kind supplied by a governmental agency".
  - (1g): "'Earned income' means wages, salaries, tips, and other employee compensation that may be included in federal adjusted gross income for the taxable year, plus the amount of the claimant's net earnings from self-employment".
- **Wis. Stat. 71.55(10)** ([docs.legis.wisconsin.gov](https://docs.legis.wisconsin.gov/statutes/statutes/71/viii/55)): the disqualified-loss addition "may not be made by a claimant who is a farmer whose primary income is from farming and whose farming generates less than $250,000 in gross receipts".
- **2025 Schedule H** ([form](https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleH.pdf), file pp. 1-2 and 4) and **instructions** ([PDF](https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleH-inst.pdf#page=11), file pp. 8, 11-17):
  - Line 7: "Wisconsin income from your 2025 income tax return"; the instructions say "Fill in the income from line 7 of Form 1".
  - Line 8c, for claimants who file no return: "Medical and long-term care insurance subtraction. Enter as a negative number". Example 1 (p. 12) enters 500, 1,235, -1,735, 10,000 and 765.
  - Line 9b (p. 13): "Include the premium amounts deducted for Medicare Parts A through D"; "do not include your children's social security or SSI benefits".
  - Line 9d (p. 13): "Fill in the GROSS amount of ALL pensions and annuities ... Include veterans' pensions, disability payments, any amounts you contributed to a pension fund, and nontaxable IRA, SEP, SIMPLE, and qualified plan distributions."
  - Lines 9e and 9f (p. 13): contributions to deferred compensation plans "excluded from income" and IRA, SEP, SIMPLE and qualified plan contributions "deducted from income".
  - Line 9h (p. 14): nontaxable scholarships, educational grants, military compensation, "G.I. Bill benefits".
  - Line 9i (p. 14): "any court ordered support payments received in 2025, including child support and family maintenance"; and "Even though these payments are no longer taxable, they must be included in household income on line 9i".
  - Line 9j (p. 14): "Wisconsin Works (W2), county relief, kinship care, and other cash public assistance"; "Do not include the following: a prior year's homestead credit; nontaxable foster care; gifts; food stamps; ... fuel or energy assistance".
  - Line 11b (form p. 2): "Workers' compensation, income continuation, and loss of time insurance (e.g., sick pay)".
- **Publication 127** ([PDF](https://www.revenue.wi.gov/DOR%20Publications/pb127.pdf)): searched for refundable credits, rebates and stimulus; it has no entry for them.

### Differences

| Category | Law | PE | Status |
|---|---|---|---|
| Base income | Wisconsin AGI (net of the medical care insurance subtraction, the state tax refund subtraction and other subtractions not added back) | federal AGI | CONFIRMED overcount |
| Child support | counted | not counted | CONFIRMED undercount |
| Maintenance outside AGI | counted | not counted | CONFIRMED undercount |
| Workers' compensation; nontaxable loss-of-time insurance | counted | not counted | CONFIRMED undercount |
| Veterans' benefits | counted | not counted | CONFIRMED undercount |
| 401(k)/403(b) deferrals | counted | not counted | CONFIRMED undercount |
| Deductible IRA, SEP, Keogh contributions | added back | not added back | CONFIRMED undercount |
| Nontaxable IRA and plan distributions | counted | not counted | CONFIRMED undercount |
| County relief and other cash assistance | counted | not counted | CONFIRMED undercount |
| Nontaxable scholarships and grants | counted | not counted | CONFIRMED undercount (check the input) |
| Non-Social Security survivor benefits | counted (all pensions and annuities) | not counted | CONFIRMED undercount (check the data mapping) |
| Earned income test: S corporation income | not earned income | counted | CONFIRMED overcount, narrow |
| Railroad retirement | counted | not counted | COVERED by #10722 |
| Gambling winnings | in Wisconsin income | not in federal AGI on main | COVERED by #10070 |
| Small-farmer exception (71.55(10)) | losses not added back | always added back | NOT-MODELABLE (no farm gross receipts) |
| Depreciation and similar add-backs; excluded home-sale gain; nontaxable military pay; loss carryforwards | counted | no input | NOT-MODELABLE |

Matches: wages and other AGI items, the loss add-backs, tax-exempt and U.S. interest, capital gains (federal AGI holds the full gain, so Wisconsin's 30 percent exclusion needs no add-back), gross pensions, military retired pay, gross Social Security for the claimant and spouse, SSI with the state supplements, unemployment, W-2 payments, the exclusion of gifts, SNAP, energy assistance and foster care, the $500 dependent deduction, the claimant-and-spouse household and the calendar-year period. No source counts refundable credits, and "a prior year's homestead credit" is excluded, so there is no receipt-timing rule.

**The base-income finding in detail.** For items Wisconsin subtracts and the statute adds back (Social Security, unemployment, U.S. interest, the capital gain exclusion, the retirement and military subtractions), federal AGI plus the nontaxable part gives the right total. The statute does not add back the medical care insurance subtraction, the long-term care insurance subtraction, the taxable state refund subtraction, college savings contributions or the other Schedule SB subtractions. Wisconsin income (Form 1 line 7) is already net of them, and Schedule H gives non-filers line 8c to take the insurance subtraction. In the instructions' Example 1 a claimant with $500 of interest, $10,000 of Social Security, a $2,000 pension and $1,735 of Medicare Part B premiums has household income of $10,765; PE gives $12,500. PE's Wisconsin income tax has no medical care insurance subtraction at all (`gov.states.wi.tax.income.subtractions.sources` has no such entry; only the `wi_other_subtractions` input could carry it), so a fix needs that subtraction first. The subtraction is limited to taxable income (worksheet line 4 on p. 12), so it does not reach nontaxable Social Security.

### Tests written

- `C:/tmp/sci-audit/tests-A/wi_homestead_income.yaml`: nine cases (child support, nontaxable maintenance, workers' compensation, veterans' benefits, IRA deduction, 401(k) deferral, nontaxable IRA distribution, county relief, and the instructions' Example 1 for the insurance subtraction).
- `C:/tmp/sci-audit/tests-A/wi_homestead_eligible.yaml`: S corporation income alone does not meet the earned income test.

No tests for scholarships or survivor benefits (input contents unverified) or for the not-modelable items.

### Open PRs and issues checked

Searched open PRs for "Wisconsin homestead", "wi_homestead", "Schedule H Wisconsin", "Wisconsin household income", and open issues for the first two. #10722 edits `sources.yaml` to add the tax-exempt railroad amounts (its diff predates #10191's rename of the Social Security source). #10070 adds `gambling_winnings` to federal gross income. #10647, #10175 and #10764 do not touch the homestead files. #10191's body says the S corporation treatment in the earned income test was left for a follow-up; I found no open PR or issue for it.

### Two-reading notes

None. One point where the form is narrower than the statute, without changing a classification: line 9i counts "court ordered" support and says "Do not include ... voluntary support", while the statute says "support money" without that limit. `child_support_received` does not separate the two.

### Not verified

- Wis. Adm. Code ch. Tax 14 (cited in the statute's cross-reference and in #10191) was not opened.
- What the microdata put in `educational_assistance` and `survivor_benefits`.
- Publication 127 was searched by keyword, not read in full.
