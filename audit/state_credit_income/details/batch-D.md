# Batch D — state credit income definitions (AZ, CO, UT, OR, NE)

Audited against upstream/main 06c0dcbc54 (2026-11-11). Read-only; no tests run.

## Findings

| State | Credit | Finding | Class | Dollar direction |
|---|---|---|---|---|
| AZ | Property tax credit (140PTC) | Tax-exempt retirement account distributions (`tax_exempt_retirement_distributions`: Roth IRA, Roth 401(k)/403(b), SEP) are not in household income; the statute counts "the gross amount of any pension or annuity" and line E says "any IRA distributions". PE already adds the tax-exempt part of pensions but not of account distributions | CONFIRMED | Income too low, credit too high |
| AZ | Property tax credit (140PTC) | Gambling winnings are missing from federal AGI on main, so from line I | COVERED (#10070) | Income too low, credit too high |
| AZ | Property tax credit (140PTC) | Employer-paid disability insurance benefits: PE counts the taxable part through federal AGI; ARS 43-1072(I) excludes "the gross amount of 'loss of time' insurance" | TWO-READINGS | Under the exclusion reading, income too high |
| AZ | Property tax credit (140PTC) | Child support received: not in the excluded list, and the rule counts "all income not specifically excluded"; no Arizona source names it. PE leaves it out | TWO-READINGS | Under the broad reading, income too low |
| AZ | Property tax credit (140PTC) | Pre-tax payroll deferrals and foreign earned income excluded under IRC 911: the rule counts income "whether or not subject to Arizona income tax"; PE starts from federal wages | TWO-READINGS | Under the broad reading, income too low (small) |
| AZ | Property tax credit (140PTC) | Capital gains excluded from federal AGI (home sale), ARS 43-1072(H)(6)(b): no input | NOT-MODELABLE | Income too low |
| AZ | Property tax credit (140PTC) | VA benefits other than disability pensions would count, but `veterans_benefits` is one input and none of it is counted | NOT-MODELABLE | Income too low |
| CO | TABOR sales tax refund | A tax unit dependent's Social Security is in modified AGI (`tax_exempt_social_security` sums every member); line 35 is the filers' Form 1040 line 6a less 6b | COVERED (#10647) | Modified AGI too high, refund tier too high (higher tiers pay more) |
| CO | TABOR sales tax refund | Tier 1 railroad benefits outside AGI are "social security benefits excluded from federal adjusted gross income" but not counted | COVERED (#10722) | Modified AGI too low |
| CO | TABOR sales tax refund | Gambling winnings are missing from federal AGI on main | COVERED (#10070) | Modified AGI too low |
| CO | TABOR sales tax refund | Non-Colorado state and local bond interest (C.R.S. 39-22-2003(1.5)(b)(IV), DR 0104 line 36) is not counted; no input separates it from Colorado bond interest, and the line 9 addition itself is unmodeled | NOT-MODELABLE | Modified AGI too low |
| CO | Property tax/rent/heat (PTC) rebate | Not modeled on main (no variable, parameter or programs.yaml entry cites C.R.S. 39-31-101 or DR 0104PTC), so there is no income definition to audit | n/a | n/a |
| UT | Circuit breaker (renter's and homeowner's credit) | Federally taxable alimony is counted twice: once in federal AGI (`taxable_alimony_income`) and again through `alimony_income` in the nontaxable list. `divorce_year` defaults to 2010, so by default all alimony is doubled | CONFIRMED | Income too high, credit too low or denied |
| UT | Circuit breaker | An adult (18+) tax unit dependent's wages and other AGI-type income count as zero (`adjusted_gross_income_person` is zero for dependents); the statute leaves out only under-18s and parents/grandparents | CONFIRMED | Income too low, credit too high |
| UT | Circuit breaker | SSI is not counted; 59-2a-101(20)(a)(vii) counts "payments received under the Social Security Act" other than SSDI, and the defined term "public assistance" does not list SSI (no Tax Commission text names SSI) | CONFIRMED (statute text; agency silent) | Income too low, credit too high |
| UT | Circuit breaker | Nontaxable disability insurance benefits (`tax_exempt_disability_benefits`) are not counted; (20)(a)(xi) counts "the gross amount of 'loss of time' insurance" | CONFIRMED | Income too low (input defaults to 0) |
| UT | Circuit breaker | Capital loss carryovers claimed in the year are not added back ((20)(a)(ii); TC-90CB line 5 "exclude carryforwards/carrybacks"); `long_term_capital_loss_carryover` exists as a memo input | CONFIRMED | Income too low, credit too high |
| UT | Circuit breaker | Gambling winnings are missing from federal AGI on main | COVERED (#10070) | Income too low |
| UT | Circuit breaker | Taxable SSDI: the statute counts it through federal AGI (PE does too); TC-90CB line 4 leaves out all SSDI "taxable and nontaxable" | TWO-READINGS | Under the form's reading, income too high |
| UT | Circuit breaker | Federal exclusions the list does not name (foreign earned income, pre-tax health premiums, HSA, above-the-line deductions): "amounts excluded from adjusted gross income ..., including" could be illustrative or exhaustive; PE adds only named kinds | TWO-READINGS | Under the illustrative reading, income too low |
| UT | Circuit breaker | No input: gains excluded from AGI, depreciation on the residence, NOL and short-term loss carryforwards, the parent/grandparent exclusion | NOT-MODELABLE | Mixed |
| OR | Retirement income credit | Household income is only federal AGI + tax-exempt interest - taxable Social Security. ORS 316.157(2)(c)(A) also adds veterans' benefits, workers' compensation, child support, SSI, welfare payments (TANF, general assistance), strike benefits and nontaxable disability/sick pay; none is added | CONFIRMED (7 categories) | Income too low, credit too high |
| OR | Retirement income credit | Losses reduce household income in full; (2)(c)(B) allows only $1,000 of net loss per category (business, farm, rental/royalty, property dispositions), and Pub. OR-17 disallows capital loss carryforwards | CONFIRMED (2 rows) | Income too low, credit too high |
| OR | Retirement income credit | Foreign income excluded under IRC 911 is not added ((2)(c)(A)(xix)); rare | CONFIRMED | Income too low |
| OR | Retirement income credit | A taxable Oregon income tax refund stays in through federal AGI; (2)(c)(C)(ii) excludes it. The input (`salt_refund_income`) is not Oregon-specific | CONFIRMED (no test) | Income too high, credit too low (small) |
| OR | Retirement income credit | Gambling and lottery winnings are missing from federal AGI on main | COVERED (#10070) | Income too low |
| OR | Retirement income credit | Roth distributions: the checklist says "Roth IRA Payments received No"; the statute adds exempt pensions "less return of investment", which would reach Roth earnings. PE follows the checklist | TWO-READINGS | Under the statute's reading, income too low |
| OR | Retirement income credit | Alimony outside federal AGI: not in the statute's list; the checklist says "Alimony and separate maintenance Yes". PE leaves it out | TWO-READINGS | Under the checklist's reading, income too low |
| OR | Retirement income credit | No usable input: tier 2 railroad benefits (one lumped input on main), gifts over $500, inheritances, life insurance proceeds, exempt military pay, depreciation over $5,000, NOLs | NOT-MODELABLE | Income too low |
| OR | WFHDC | "Oregon adjusted gross income": PE uses federal AGI + Oregon additions - subtractions; the agency uses federal AGI alone for full-year residents. They differ only if additions exceed subtractions (`or_other_additions` input, default 0) | TWO-READINGS | Under the agency's reading, income too high in that case only |
| NE | Child care refundable tax credit | Total household income is plain federal AGI; the statute says "federal modified adjusted gross income" and the Department's worksheet adds Schedule 8812 line 2d (income excluded under IRC 911, 931 and 933). `agi_plus_section_911_931_933_exclusions` already computes it | CONFIRMED (2 rows) | Income too low, credit too high (rare for Nebraska residents) |
| NE | Child care refundable tax credit | Gambling winnings are missing from federal AGI on main | COVERED (#10070) | Income too low |
| NE | Child care refundable tax credit | "Total household income" is measured on the claiming parent's federal return (agency and PE); the term could be read to include other household members' income, with no support in the Act | TWO-READINGS | Under the household reading, income too low |

## 1. Arizona — property tax credit household income (Form 140PTC)

### What PE does
- `parameters/gov/states/az/tax/income/credits/property_tax/income_sources.yaml` (one list from 2021): `tax_exempt_interest_income`, `tax_exempt_public_pension_income`, `tax_exempt_private_pension_income`, `az_property_tax_credit_agi`, `az_property_tax_credit_dependent_income`, `az_property_tax_credit_unemployment`, `az_property_tax_credit_nontaxable_income`.
- `az_property_tax_credit_income` (TaxUnit) `adds` the list. `az_property_tax_credit_household_income` (Household) sums it over every tax unit in the household. Only `az_property_tax_credit_potential` reads it (schedule lookup, floored at 0), which feeds `az_property_tax_credit`.
- `az_property_tax_credit_agi`: federal AGI, less taxable Social Security, less taxable unemployment compensation, with federal capital gains and the federal capital loss deduction replaced by each non-dependent's line D amount (net loss floored at -$1,500 per person, long-term carryover added back), and every above-the-line deduction except `loss_ald` added back. Not floored: business, farm, rental, partnership and estate losses count.
- `az_property_tax_credit_dependent_income`: each federal gross income source of dependents, signed, skipping Social Security, unemployment and capital gains, plus the dependent's line D amount.
- `az_property_tax_credit_unemployment`: other states' unemployment compensation (input `az_other_state_unemployment_compensation`, default 0). `az_property_tax_credit_nontaxable_income`: strike benefits and alimony that federal gross income leaves out.
- Federal AGI brings in `irs_employment_income` (wages less `pre_tax_contributions`), self-employment, partnership/S corp, farm, rent, interest, dividends, `taxable_pension_income`, `taxable_retirement_distributions` (IRA, 401(k), 403(b), SEP, Keogh), `taxable_roth_conversions`, `military_retirement_income`, `taxable_disability_benefits`, `estate_income`, `miscellaneous_income`, `debt_relief`, `salt_refund_income`, `taxable_alimony_income`.

### What the law says
- ARS 43-1072(H)(5): "\"Household income\" means all income received by all persons of a household in a taxable year while members of the household."
- ARS 43-1072(H)(6): "\"Income\" means the sum of the following: (a) Adjusted gross income as defined by the department. (b) The amount of capital gains excluded from adjusted gross income. (c) Nontaxable strike benefits. (d) Nontaxable interest received from the federal government or any of its instrumentalities. (e) Payments received from a retirement program paid by this state or any of its political subdivisions. (f) Payments received from a retirement program paid by the United States ... (g) The gross amount of any pension or annuity not otherwise exempted except as provided in subsection I of this section."
- ARS 43-1072(I): income "shall not include monies received from cash public assistance and relief, relief granted under the provisions of this section, railroad retirement benefits, payments received under the federal social security act (49 Stat. 620), payments received under Arizona state unemployment insurance laws, payments received from veterans' disability pensions, payments received as workers' compensation, the gross amount of \"loss of time\" insurance, and gifts from nongovernmental sources or surplus foods or other relief in kind supplied by a governmental agency."
- A.A.C. R15-2C-502(A)(1): "\"Adjusted gross income\" means the sum of all income not specifically excluded in A.R.S. § 43-1072 whether or not subject to Arizona income tax, except those items that A.R.S. § 43-1072 specifically includes in income." (C)(3): "Net losses are limited to $1,500 for each household member."
- ITR 12-1 (file pages 1-3): items (1)-(11) included; item (9): "Pension and annuity income includes Arizona state and local retirement benefits, and U.S. Government pensions including civil service and military retirement benefits. Pension and annuity income for the year does not include amounts of pension distributions that were transferred into another retirement plan without federal tax consequences during the year (a rollover)." Item (11): "Any other income not specifically described in items 1 through 10 above that is not specifically excluded".
- 2025 Form 140PTC instructions, file page 4, line E: "You must include income from all other pensions and annuities. Pension income that you must enter here includes the following: all retirement payments from the federal government, except those listed above, all retirement payments from the State of Arizona, all retirement payments from any local government (including police and school districts), and any IRA distributions." Line I examples: "strike benefits exempt from tax, and unemployment insurance payments from states other than Arizona." Excluded list adds "Arizona Form 140PTC refunds received last year."

### Differences
1. **Tax-exempt retirement account distributions — CONFIRMED undercount.** `tax_exempt_retirement_distributions` (Roth IRA, Roth 401(k)/403(b), SEP) is in no list item. The statute counts the "gross amount" of pensions and annuities, the rule counts income "whether or not subject to Arizona income tax", and line E names "any IRA distributions". The list's own comment adds the tax-exempt part of pensions on that ground. Fix: add `tax_exempt_retirement_distributions` to `income_sources.yaml`. Caveat: the statute does not name IRAs; the form does. Rollovers stay out (ITR 12-1 item (9)); the input is documented as qualifying Roth distributions, not rollovers. Test: `tests-D/az_property_tax_credit_income.yaml`.
2. **Gambling winnings — COVERED (#10070).** Not in `gov.irs.gross_income.sources` on main; #10070 adds them, and they then flow into both AGI-based pieces here.
3. **"Loss of time" insurance — TWO-READINGS.** PE counts `taxable_disability_benefits` through AGI. If employer-paid disability insurance benefits are "loss of time" insurance, subsection (I) excludes their gross amount; if the phrase means only personally held policies, PE is right. The agency repeats the statute's words without defining them. PE cannot separate an insurance benefit from a disability pension inside `disability_benefits`.
4. **Child support — TWO-READINGS.** Not excluded by (I); the rule's "all income not specifically excluded" would count it as line I other income. No Arizona source names child support, and it is not income in the federal sense the rule builds on. PE leaves it out.
5. **Pre-tax deferrals and the foreign earned income exclusion — TWO-READINGS, small.** Same "all income ... whether or not subject to Arizona income tax" clause; PE starts from federal wages (`irs_employment_income`) and does not add `foreign_earned_income_exclusion`.
6. **NOT-MODELABLE:** gains excluded from federal AGI ((H)(6)(b); no input, already documented in the parameter file); VA benefits other than "veterans' disability pensions" (`veterans_benefits` is one input); income only "while members of the household" (part-year members); passive-loss rules (ITR 12-1 items (4)-(5)).

Everything else matches: wages, business and farm losses, taxable and tax-exempt interest, dividends, per-member capital losses, gross pensions, military retired pay (through federal AGI), Social Security and SSI out, railroad retirement out, Arizona unemployment out and other states' in, workers' compensation and public assistance out, all alimony in, strike benefits in, dependents' and co-residents' income in, no above-the-line deductions. Timing: nothing is counted on a received-versus-earned basis that PE gets wrong; the prior-year 140PTC refund is excluded outright.

### Open PRs checked
- #10727 (strike benefits): changes `az_property_tax_credit_nontaxable_income` to add only the non-taxable part; no category change.
- #10696 (railroad retirement taxation): subtracts the newly taxable railroad benefits in `az_property_tax_credit_agi` and skips them for dependents; keeps the exclusion.
- #10070 (gambling winnings in federal gross income): covers item 2.
- No open PR touches `income_sources.yaml`.

### Not verified
- The Form 140PTC itself (page 2, Part 1) was downloaded but only the instructions were read line by line.
- ARS 43-1072 was read on azleg.gov as currently published; no session-law history was checked.

## 2. Colorado — TABOR state sales tax refund modified AGI

### What PE does
- `parameters/gov/states/co/tax/income/credits/sales_tax_refund/magi_sources.yaml` (from 1999): `adjusted_gross_income`, `tax_exempt_social_security`, and a commented-out placeholder `# - non_taxable_interest_income_from_state_and_local_bonds`.
- `co_modified_agi` (TaxUnit) `adds` the list. No floor: a negative federal AGI passes through.
- `tax_exempt_social_security` = `tax_unit_social_security` (every member's `social_security`, dependents included) less `tax_unit_taxable_social_security` (the filers' taxable part).
- Read only by `co_sales_tax_refund`, and only in years when `amount.flat_amount_enabled` is false (the six-tier years: 2021, 2022, 2024, 2025, and 2027 on; 2023 is flat; 2026 has no refund).

### What the law says
- C.R.S. 39-22-2003(1.5): "For purposes of this section, \"adjusted gross income\" means: ... (b) For the taxable year commencing on January 1, 2001, ... and for each subsequent taxable year thereafter, the combined total of: (I) Federal adjusted gross income; (II) Social security benefits excluded from federal adjusted gross income for the tax year; and (III) Repealed. (IV) The amount of interest income from state and local bonds added to federal taxable income pursuant to section 39-22-104 (3)(b)."
- (3)(d): for a joint return, "the amount of the refund shall be based upon the aggregate adjusted gross income of the qualified individuals".
- 2025 Book 104, file pages 13-14 and 42 (DR 0104 lines 34-37): line 34 "Enter your adjusted gross income from your federal income tax form ... If your federal adjusted gross income is a negative amount, enter the amount as negative"; line 35 "Refer to your federal income tax form 1040, 1040 SR, or 1040 SP lines 6a and 6b. Subtract line 6b from line 6a"; line 36 "Nontaxable Interest Income from State and Local Bonds. Refer to the DR 0104 line 9. If you entered any bond interest on line 9, enter the amount of bond interest income here"; line 37 "Sum of lines 34 through 36."
- Book 104, file page 10 (line 9): "Bond interest: Interest earned from bonds issued by any state or political subdivision, but not bonds issued by the State of Colorado or its political subdivisions on or after May 1, 1980."

### Differences
1. **Dependents' Social Security — COVERED (#10647).** Main's `tax_exempt_social_security` includes a dependent's benefits. #10647 replaces it with `filer_tax_exempt_social_security` and adds `co_modified_agi.yaml`.
2. **Tier 1 railroad benefits — COVERED (#10722).** #10722 adds `tax_exempt_railroad_social_security_equivalent_benefits` to the list. (#10647 and #10722 both edit the same list line; whichever merges second must keep both changes.)
3. **Non-Colorado bond interest — NOT-MODELABLE.** The statute and line 36 count it. PE has only `tax_exempt_interest_income` (all federally exempt interest), no Colorado/non-Colorado split, and does not model the DR 0104 line 9 addition. Adding all of `tax_exempt_interest_income` would count Colorado bond interest the statute leaves out. A fix needs a new input for the line 9 bond interest addition, used both in `co_additions` and here.
4. **Gambling winnings — COVERED (#10070)** through federal AGI.

Everything else matches. The definition is federal AGI plus two named additions, so nontaxable pensions, Roth distributions, veterans' benefits, workers' compensation, SSI, public assistance, child support, gifts and credits are correctly out. Timing is the tax year throughout; the refund itself is attributed to the eligibility year (documented in the parameter descriptions).

### Colorado property tax/rent/heat (PTC) rebate
Not modeled on main. `git grep -i` for `39-31-101`, `0104PTC`, `104PTC` and "rent/heat" under `variables/`, `parameters/` and `programs.yaml` at upstream/main returns nothing, and the only Colorado property tax variable is the `co_property_tax_exemption` input (C.R.S. 39-3-203 senior homestead exemption). No open PR adds it. Nothing to audit.

### Open PRs checked
- #10647: dependents' Social Security out of per-return readers, including this list. Diff read.
- #10722: railroad benefits in state income tests, including this list. Diff read.
- #10070: gambling winnings in federal gross income.

### Not verified
- C.R.S. 39-22-104(3)(b) (the bond interest addition itself) was not opened; the Book 104 line 9 text was used for its scope.
- The statute was read on colorado.public.law (2024 C.R.S. text), not the 2025 or 2026 official publication.

## 3. Utah — homeowner's/renter's (circuit breaker) relief household income

The statute moved: former Utah Code 59-2-1202 is now 59-2a-101 (Chapter 2a, effective 1/1/2026), which is what the parameter cites and what was read.

### What PE does
- `ut_homeowner_renter_relief_household_income` (Household): for every member aged 18 or older (`adult_age_threshold`), `adjusted_gross_income_person` plus `ut_homeowner_renter_relief_nontaxable_income`; plus a fallback that adds the tax unit's `adjusted_gross_income` on the head when the members' person-level AGI sums to zero. Not floored.
- `adjusted_gross_income_person` = `irs_gross_income` less the person's above-the-line deductions. `irs_gross_income` is zero for a tax unit dependent, so a dependent contributes only nontaxable sources.
- `ut_homeowner_renter_relief_nontaxable_income` (Person) = the list `nontaxable_income/sources.yaml` + max(0, `social_security` - `social_security_disability` - `taxable_social_security`) + max(0, `total_unemployment_compensation` - `taxable_unemployment_compensation`).
- List (2024 on): `alimony_income`, `child_support_received`, `railroad_benefits`, `strike_benefits`, `tax_exempt_interest_income`, `tax_exempt_pension_income`, `tax_exempt_retirement_distributions`, `traditional_401k_contributions`, `traditional_403b_contributions`, `traditional_ira_contributions`, `self_employed_pension_contributions`, `veterans_benefits`, `workers_compensation`.
- Readers: `ut_renters_credit` (current year), `ut_homeowners_credit` (`period.last_year`), `ut_homeowner_renter_relief_pre_one_claimant_eligible` (income limit, same split).

### What the law says (Utah Code 59-2a-101, file pages 3-5)
- (15): "\"Household income\" means all income received by all members of a claimant's household in: (i) for a claimant who owns a residence, the calendar year preceding the calendar year in which property taxes are due; or (ii) for a claimant who rents a residence, the year for which a claim is filed. (b) \"Household income\" does not include income received by a member of a claimant's household who is: (i) under 18 years old; or (ii) a parent or a grandparent, through blood, marriage, or adoption, of the claimant or the claimant's spouse."
- (17): "\"Income\" means the sum of: (a) federal adjusted gross income as defined in Section 62, Internal Revenue Code; and (b) nontaxable income."
- (20)(a): "\"Nontaxable income\" means amounts excluded from adjusted gross income under the Internal Revenue Code, including: (i) capital gains; (ii) loss carry forwards claimed during the taxable year in which a claimant files for relief under this chapter; (iii) depreciation claimed pursuant to the Internal Revenue Code by a claimant on the residence ...; (iv) support money received; (v) nontaxable strike benefits; (vi) the gross amount of a pension or annuity, including benefits under the Railroad Retirement Act of 1974 ... and veterans disability pensions; (vii) except for payments described in Subsection (20)(b)(vi), payments received under the Social Security Act; (viii) state unemployment insurance amounts; (ix) nontaxable interest received from any source; (x) workers' compensation; (xi) the gross amount of \"loss of time\" insurance; and (xii) voluntary contributions to a tax-deferred retirement plan."
- (20)(b): "\"Nontaxable income\" does not include: (i) public assistance; (ii) aid, assistance, or contributions from a tax-exempt nongovernmental source; (iii) surplus foods; (iv) relief in kind supplied by a public or private agency; (v) relief provided under this chapter; (vi) social security disability income payments received under the Social Security Act; (vii) federal tax refunds; (viii) federal child tax credits ...; (ix) federal earned income tax credits ...; (x) payments received under a reverse mortgage; (xi) payments or reimbursements to senior program volunteers ...; or (xii) gifts or bequests."
- (24): "\"Public assistance\" means: (a) medical assistance provided under Title 26B, Chapter 3 ...; (b) SNAP benefits ...; (c) services or benefits provided under Title 35A, Chapter 3, Employment Support Act; and (d) foster care maintenance payments ..."
- TC-90CB (Rev. 4/26, rent year 2025), file page 1, lines 1-9: "2. Total interest income, dividends (taxable and nontaxable)"; "3. Pensions, annuities (taxable and nontaxable)"; "4. Social Security and railroad retirement (but not Social Security Disability) (taxable and nontaxable)"; "5. Capital gain/loss (exclude carryforwards/carrybacks)"; "6. Nontaxable income (see UCA §59-2a-101(20))"; "7. Unemployment, worker's compensation". Household Income Worksheet (file page 3): "Do not include income of children under 18 or your (or your spouse's) parents and grandparents, even if they live with you."

### Differences
1. **Taxable alimony counted twice — CONFIRMED overcount.** `alimony_income` (all alimony) is in the nontaxable list, and `taxable_alimony_income` is in federal gross income. `divorce_year` defaults to 2010, before the 2019 cutoff, so by default all alimony is taxable and is counted in both places. Only alimony outside AGI is "support money received" that the statute adds. Fix: add `alimony_income` less `taxable_alimony_income` (Arizona's `az_property_tax_credit_nontaxable_income` does this). #10727 makes the same kind of fix for strike benefits in this list but leaves alimony.
2. **Adult dependents' income — CONFIRMED undercount.** The statute counts every household member except under-18s and parents/grandparents. PE takes `adjusted_gross_income_person`, which is zero for any tax unit dependent, so the wages, interest or pension of a dependent aged 18 or older (an adult child or grandchild) are missing. Fix: for adult dependents, sum the federal gross income sources as `az_property_tax_credit_dependent_income` does.
3. **SSI — CONFIRMED on the statute's text.** (20)(a)(vii) counts "payments received under the Social Security Act" except SSDI; SSI is title XVI of that act; the exclusion for "public assistance" is a defined term that does not list SSI. PE's list has no `ssi`. The Tax Commission's form and web pages never mention SSI, so the agency's practice is unverified; if it treats SSI as public assistance, downgrade this to two-readings.
4. **Nontaxable disability insurance — CONFIRMED undercount.** `tax_exempt_disability_benefits` (IRC 104(a)(3) benefits) is not in the list; (20)(a)(xi) counts "the gross amount of 'loss of time' insurance". The input defaults to zero.
5. **Loss carryforwards — CONFIRMED undercount.** (20)(a)(ii) adds back "loss carry forwards claimed during the taxable year", and line 5 says "exclude carryforwards/carrybacks". PE's `long_term_capital_gains` is net of `long_term_capital_loss_carryover`, and nothing adds the used carryover back. NOL and short-term carryovers have no input.
6. **Taxable SSDI — TWO-READINGS.** Statute: SSDI is only kept out of "nontaxable income", so its taxable part stays in federal AGI; PE does this. Form line 4: leave out SSDI "taxable and nontaxable". Statute-first keeps PE as is.
7. **Unnamed federal exclusions — TWO-READINGS.** "Amounts excluded from adjusted gross income under the Internal Revenue Code, including:" can be read as illustrative (then the foreign earned income exclusion, pre-tax health premiums, HSA contributions and arguably above-the-line deductions count) or as the working list (the form's lines). PE adds only named kinds.
8. **Gambling winnings — COVERED (#10070)** through federal AGI.
9. **NOT-MODELABLE:** capital gains excluded from AGI ((20)(a)(i)); depreciation on the residence ((20)(a)(iii)); the parent/grandparent exclusion (documented in the variable; PE counts their income).

Smaller point, left as a match: PE adds traditional IRA contributions rather than the amount deducted; a nondeductible contribution was never excluded from AGI and is then counted twice. This needs a contribution above compensation or above the 219(g) limit, so it is out of reach for households near the $44,221 limit.

Matches: federal AGI with losses, tax-exempt interest, gross pensions and Roth distributions, railroad retirement, veterans' benefits, Social Security other than SSDI, taxable and nontaxable unemployment compensation, workers' compensation, child support, strike benefits, retirement deferrals, public assistance and credits out, under-18s out, and the renter/homeowner year split.

### Open PRs checked
- #10727: `strike_benefits` -> `tax_exempt_strike_benefits` in the list; does not touch alimony.
- #10696: drops `railroad_benefits` from the list and adds the non-taxable remainder in the formula.
- #10722: touches a Utah Social Security credit test only.
- #10070: gambling winnings.
- No open PR edits `ut_homeowner_renter_relief_household_income.py`; no open issue on this program was found.

### Not verified
- TC-90CY and TC-90H (homeowner forms): `tc-90cy.pdf` downloaded (352,599 bytes) but `pdftotext` returned no text, and TC-90H was not fetched; the homeowner side rests on the statute alone.
- Pub 36 (Rev. 5/25) was read; it gives eligibility and amounts but no income definition.
- No Tax Commission rule or guidance on SSI or on the "including" clause was found.

## 4a. Oregon — retirement income credit household income

### What PE does
- `or_retirement_credit_household_income` (TaxUnit): `adds = ["adjusted_gross_income", "tax_exempt_interest_income"]`, `subtracts = ["taxable_social_security"]`. No parameter list. Losses in federal AGI pass through in full; no floor.
- Read only by `or_retirement_credit` (worksheet line 7): the base ($7,500, or $15,000 joint, less Social Security) is reduced by household income above $15,000 ($30,000 joint).

### What the law says
- ORS 316.157(2)(b): "\"Household income\" means the aggregate income of the taxpayer and the spouse of the taxpayer who reside in the household, that was received during the taxable year for which a credit is claimed, except that \"household income\" does not include Social Security benefits received by the taxpayer or the spouse of the taxpayer."
- (2)(c): "\"Income\" means \"adjusted gross income\" as defined in the federal Internal Revenue Code ... with the following modifications: (A) There shall be added to adjusted gross income the following items of otherwise exempt income: (i) The gross amount of any otherwise exempt pension less return of investment, if any. (ii) Child support received by the taxpayer. (iii) Inheritances. (iv) Gifts and grants, the sum of which are in excess of $500 per year. (v) Amounts received by a taxpayer or spouse of a taxpayer for support from a parent who is not a member of the taxpayer's household. (vi) Life insurance proceeds. (vii) Accident and health insurance proceeds, except reimbursement of incurred medical expenses. (viii) Personal injury damages. (ix) Sick pay that is not included in federal adjusted gross income. (x) Strike benefits excluded from federal gross income. (xi) Worker's compensation, except for reimbursement of medical expense. (xii) Military pay and benefits. (xiii) Veteran's benefits. (xiv) Payments received under the federal Social Security Act that are excluded from federal gross income. (xv) Welfare payments, except ... (xvi) Nontaxable dividends. (xvii) Nontaxable interest not included in federal adjusted gross income. (xviii) Rental allowance paid to a minister ... (xix) Income from sources without the United States that is excluded from federal gross income."
- (2)(c)(B): "Adjusted gross income shall be increased due to the disallowance of the following deductions: (i) The amount of the net loss, in excess of $1,000, from all dispositions of tangible or intangible properties. (ii) ... from the operation of a farm or farms. (iii) ... from all operations of a trade or business, profession or other activity entered into for the production or collection of income. (iv) ... from tangible or intangible property held for the production of rents, royalties or other income. (v) The amount of any net operating loss carryovers or carrybacks included in federal adjusted gross income. (vi) The amount, in excess of $5,000, of the combined deductions or other allowances for depreciation, amortization or depletion."
- (2)(c)(C): "\"Income\" does not include ... (ii) Any refund of Oregon personal income taxes that were imposed under this chapter."
- (2)(f): "\"Social Security benefits\" means Social Security benefits, as defined in section 86 of the Internal Revenue Code (Title II Social Security or tier 1 railroad retirement benefits)."
- 2025 Publication OR-17 (Rev. 01-29-26), file page 107: "Household income generally includes all income (both taxable and nontaxable) each spouse received during the year. Household income includes gross income reduced by adjustments as reported in your federal AGI. You also need to include items not in your federal AGI. These items include but aren't limited to: Veteran's and military benefits. Gifts, grants, and scholarships (totaling more than $500 in value). Disability pay. Nontaxable dividends ... Inheritance. Insurance proceeds. Nontaxable interest. Lottery winnings. RRB benefits (Tier 2 only). IRA conversions included in AGI." "Don't include: Social Security and Tier 1 RRB benefits. Your state tax refund. Pension income excluded from federal AGI that is a return of your contributions. Pensions that are rolled over ..." "Any net loss from the source is limited to $1,000. NOL carrybacks or carryforwards aren't allowed. Capital loss carryforwards aren't allowed."
- Household Income Checklist, file pages 127-128: "Child support Yes"; "Disability income (entire amount) Yes"; "Workers' compensation Yes"; "Strike benefits Yes"; "Temporary Assistance for Needy Families (TANF) Yes"; "Supplemental Security Income (SSI) Yes"; "Foreign income excluded from federal AGI Yes"; "Capital loss carryover No"; "Roth IRA Payments received No"; "Cafeteria plan benefits No"; refunds: "Oregon income tax No", "Other states' income tax (if included in federal AGI) Yes".

### Differences
PE's definition is the statute's starting point plus one of its nineteen additions. Statute and agency agree on what is missing.

1. **CONFIRMED undercounts (each with a test):** veterans' benefits ((A)(xiii)); workers' compensation ((A)(xi)); child support ((A)(ii)); SSI ((A)(xiv); not a section 86 benefit, so the Social Security carve-out does not reach it); welfare payments such as TANF and general assistance ((A)(xv)); strike benefits ((A)(x)); nontaxable disability and sick pay ((A)(vii), (ix)); foreign income excluded under IRC 911 ((A)(xix)).
2. **CONFIRMED: loss limits.** Net losses above $1,000 from a business, a farm, rental or royalty property, or property dispositions must be added back ((B)(i)-(iv)). PE takes federal AGI as is, so a $5,000 business loss lowers household income by $5,000 instead of $1,000, and a $3,000 capital loss by $3,000 instead of $1,000. Capital loss carryovers are disallowed by the publication (the statute names only NOL carryovers); PE's gains are net of the carryover.
3. **CONFIRMED overcount, no test: Oregon tax refund.** A taxable state refund (`salt_refund_income`) is in federal AGI; (C)(ii) excludes Oregon refunds. The input is not Oregon-specific.
4. **COVERED (#10070):** gambling and lottery winnings.
5. **TWO-READINGS: Roth and other exempt retirement payments.** Statute: add exempt pensions "less return of investment". Checklist: "Roth IRA Payments received No". PE adds neither `tax_exempt_pension_income` (basis recovery, correctly out) nor `tax_exempt_retirement_distributions`.
6. **TWO-READINGS: alimony outside federal AGI.** Not in the statute's list; the checklist says "Alimony and separate maintenance Yes" without qualification.
7. **NOT-MODELABLE:** tier 2 railroad benefits (lumped with tier 1 on main; #10696 splits them but does not add the exempt tier 2 part here); gifts and grants over $500, inheritances, life insurance proceeds, personal injury damages, parental support; exempt military pay, nontaxable dividends, minister's rental allowance; depreciation over $5,000 and NOL carryovers.

A fix should move the definition into a parameter list (as other states do) and add a loss-limit step. Fixing it raises household income, so it lowers the credit; the credit is nonrefundable and capped at 9% of at most $7,500 ($15,000 joint).

Timing: the statute counts income "received during the taxable year"; no credit or rebate is counted, so there is no received-versus-earned issue.

### Open PRs checked
- #10696: subtracts taxable tier 1 railroad benefits here and counts tier 1 as Social Security in `or_retirement_credit`. Adds none of the missing categories.
- #10727 (strike benefits in federal gross income): taxable strike benefits would then count through AGI; the excluded part still would not.
- #10722: no Oregon file. #10070: gambling winnings.

### Not verified
- The 2025 Form OR-40 instructions were downloaded but not read for this credit; Publication OR-17 carries the worksheet.
- ORS 316.157 was read on oregon.public.law (2023 amendments shown in the history note), not on the legislature's site.
- The Oregon administrative rule cited in `or_retirement_credit_eligible_person` (secure.sos.state.or.us, ruleVrsnRsn=238290) returned a page with no rule text to curl, so no rule on household income was read.

## 4b. Oregon — working family household and dependent care credit household income

### What PE does
- `or_wfhdc_household_income` (TaxUnit) = `max_(adjusted_gross_income, or_agi)`, where `or_agi` = federal AGI + `or_additions` (the `or_other_additions` input, default 0) - `or_income_subtractions`.
- Readers: `or_wfhdc_income_eligible` (at most 300% of the poverty guideline) and `or_wfhdc_income_category` (percentage table row).

### What the law says
- ORS 315.264(4): "The credit under this section is not allowed to a taxpayer with federal adjusted gross income or Oregon adjusted gross income, whichever is greater, in excess of 300 percent of the federal poverty level."
- 2025 Schedule OR-WFHDC instructions (Rev. 10-16-25), file page 1, qualification 5: "Your federal adjusted gross income (AGI) on Form OR-40, line 7 (or for nonresidents and part-year residents, the greater of your federal AGI or your Oregon AGI on Form OR-40-N or Form OR-40-P, line 29S) isn't more than the limit for your household size."

### Differences
- No income category is missing: the test is AGI, with nothing nontaxable added, and PE matches that.
- **TWO-READINGS: "Oregon adjusted gross income".** PE reads it as federal AGI after Oregon additions and subtractions. The agency applies federal AGI alone to full-year residents and uses Oregon AGI (OR-40-N/P line 29S) only for part-year residents and nonresidents. The readings differ only when Oregon additions exceed subtractions, which in PE requires the `or_other_additions` input.
- Gambling winnings: COVERED (#10070) through federal AGI.

### Open PRs checked
None touches `or_wfhdc_household_income`.

### Not verified
- The statute's percentage table in subsection (2) and Publication OR-WFHDC-TB were not compared with PE's parameters (out of scope: income definition only).

## 5. Nebraska — child care refundable tax credit total household income

### What PE does
- `ne_refundable_ctc_total_household_income` (TaxUnit): `return tax_unit("adjusted_gross_income", period)`. No list, no additions, no floor.
- Readers: `ne_refundable_ctc` (the $2,000 / $1,000 / $0 amount scale) and `ne_refundable_ctc_income_eligible` (at or below 100% of the poverty guideline, which waives the licensed-care requirement in `ne_refundable_ctc_eligible_child`).

### What the law says
- Neb. Rev. Stat. 77-7202(8): "Total household income means federal modified adjusted gross income." (5): "Parent or legal guardian means an individual who claims a child as a dependent for federal income tax purposes".
- 77-7203(1)(c), (2), (3): eligibility without licensed care if "total household income is less than or equal to one hundred percent of the federal poverty level"; "Two thousand dollars per child if the parent's or legal guardian's total household income is no more than seventy-five thousand dollars; or ... One thousand dollars per child if ... more than seventy-five thousand dollars but no more than one hundred fifty thousand dollars"; no credit above $150,000.
- Nebraska Department of Revenue, "Child Care Refundable Tax Credit Total Household Income Calculation" (one page): "1 Adjusted gross income from the Federal Form 1040 for the tax year return on which you are claiming the credit. ... 2 Enter line 2d of the Federal Schedule 8812 or if you have not filed, enter the total of any income from Puerto Rico, American Samoa; and from Form 2555 include the calculated foreign earned income exclusion adjustment for the housing deduction on the foreign earned income ... 3 Add lines 1 and 2. This amount is your total household income".
- Form 7203 instructions, file page 2, Part A: the same components, including "Line 2d, Federal Schedule 8812*", "Minus: Adjustments to income based on Federal Schedule 1. Equals your total household income".
- The Department's web page repeats: "Total household income means federal modified adjusted gross income."

### Differences
1. **Modified AGI add-backs — CONFIRMED undercount.** The statute's "modified" has content only through the Department's worksheet: federal AGI plus Schedule 8812 line 2d, which is the child tax credit's modified AGI (income excluded under IRC 911, 931 and 933). PE uses plain AGI. PE already has `agi_plus_section_911_931_933_exclusions` for this measure; the fix is a one-line swap. Two rows (section 911; sections 931/933), two test cases. Material only for the few Nebraska residents with excluded foreign or possession income.
2. **Gambling winnings — COVERED (#10070)** through federal AGI.
3. **Whose income — TWO-READINGS, PE follows the agency.** "Household" is in the term, but the definition and the worksheet point at the claiming parent's Form 1040. No text supports adding an unmarried partner's or other members' returns.

Nothing nontaxable is added by the law, and PE adds nothing: Social Security outside AGI, SSI, child support, veterans' benefits, workers' compensation, tax-exempt interest and public assistance are correctly out. Timing: the tax year of the return; the application is an estimate that the return's figure overrides.

### Outside the income definition (not verified by running anything)
- `amount.yaml` has thresholds at 0, 75,000 and 150,000. The statute pays $2,000 at "no more than" $75,000 and $1,000 at "no more than" $150,000, so the amounts at exactly $75,000 and exactly $150,000 depend on whether the scale treats a threshold as inclusive. Colorado's refund scale in this batch uses 36_001-style thresholds for the same wording.
- The first threshold is 0 and the income variable is not floored. The Arizona credit's code notes that a single-amount scale returns 0 below its first threshold; if that holds here, a parent with negative federal AGI gets $0 instead of $2,000 per child. Worth one test case by whoever picks this up.

### Open PRs checked
- #10654 (NE itemized deductions) and #10722 (railroad benefits): neither touches the refundable credit files. No open PR was found for "Nebraska child care refundable" or `ne_refundable_ctc`.

### Not verified
- The eDASH application itself (Form 7203 is submitted online); only the instructions PDF, the worksheet PDF, the FAQ page and the credit page were read.
- No Nebraska regulation or revenue ruling defining "federal modified adjusted gross income" for this Act was searched for beyond the Department's pages.
- 77-7202 and 77-7203 were read as currently published on nebraskalegislature.gov; amendments after LB 754 (2023) were not traced.
