# Batch E — state credit income definitions (MA, ME, OH, WV, IA)

Audited against upstream/main 06c0dcbc54 (2026-11-11). Read-only; no tests run.

## Findings

| State | Credit | Finding | Class | Dollar direction |
|---|---|---|---|---|
| MA | Senior circuit breaker | Total income starts from Massachusetts gross income, not adjusted gross income, so the deductions allowed in reaching AGI (Schedule Y lines 2-10: alimony paid, HSA, self-employed health insurance, student loan interest) never reduce it. The statute starts from Part A + B + C AGI; the Schedule CB worksheet subtracts those lines | CONFIRMED | Income too high, credit too low or denied |
| MA | Senior circuit breaker | A long-term capital loss cancels a short-term gain (and the reverse) because `capital_gains` nets the two classes. § 6(k)(1) adds back net capital losses deducted under § 2(c)(2); the worksheet counts gains "not including any losses" | CONFIRMED | Income too low, credit too high |
| MA | Senior circuit breaker | Tax-exempt retirement account distributions (`tax_exempt_retirement_distributions`: Roth IRA, Roth 401(k)/403(b)) are not added; the statute adds "the total amount of income and receipts from ... retirement, pension, or annuities" and line 5 is "Pensions/annuities/IRA/Keogh distributions not taxed" | CONFIRMED | Income too low, credit too high |
| MA | Senior circuit breaker | Workers' compensation is not added; DOR lists it on line 6 and the statute adds "gross receipts from any other source" | CONFIRMED | Income too low, credit too high |
| MA | Senior circuit breaker | EAEDC (`ma_eaedc`, the state's cash aid to people 65+) and `general_assistance` are not added; the statute adds cash public assistance | CONFIRMED | Income too low, credit too high |
| MA | Senior circuit breaker | Nontaxable disability and sick pay (`tax_exempt_disability_benefits`) is not added; DOR: "Include it if paid in lieu of wages" | CONFIRMED | Income too low (input defaults to 0) |
| MA | Senior circuit breaker | Railroad retirement benefits are not added | COVERED (#10722) | Income too low |
| MA | Senior circuit breaker | Gambling winnings are missing from federal gross income on main | COVERED (#10070) | Income too low |
| MA | Senior circuit breaker | SNAP: the statute adds "cash, but not in-kind, public assistance"; DOR's instructions and web page count "food stamps". PE follows the statute and documents the choice | TWO-READINGS | Under DOR's reading, income too low |
| MA | Senior circuit breaker | Veterans' benefits, child support and non-taxable alimony: the statute's "gross receipts from any other source" reaches them; DOR's list does not name them and its general rule is not to add back federally excluded amounts. PE leaves them out | TWO-READINGS (2 rows) | Under the statute-text reading, income too low |
| MA | Senior circuit breaker | No input: tax-exempt dividends, excluded gain on a home sale, gifts, return of capital | NOT-MODELABLE (3 rows) | Income too low |
| ME | Property tax and sales tax fairness credits | SSI is not counted. The statute adds "Payments received under the federal Social Security Act ... to the extent not included in federal adjusted gross income", and the Schedule PTFC/STFC instructions name "supplemental security income" | CONFIRMED | Income too low, credit too high |
| ME | Property tax and sales tax fairness credits | A loss that federal AGI nets against income on the same line (rental loss against partnership income; one spouse's loss against the other's gain) is ignored, because `irs_gross_income` floors each source for each person at zero. The statute adds back only "any net loss resulting from combining" those items | CONFIRMED | Income too high, credit too low |
| ME | Property tax and sales tax fairness credits | Railroad retirement benefits outside federal AGI are not counted | COVERED (#10722) | Income too low |
| ME | Property tax and sales tax fairness credits | A dependent's Social Security and tax-exempt interest are counted | COVERED (#10647, #9894) | Income too high |
| ME | Property tax and sales tax fairness credits | Gambling winnings are missing from federal gross income on main | COVERED (#10070) | Income too low |
| ME | Property tax and sales tax fairness credits | Adjustments the statute does not list: the statute adds back fourteen named deductions to federal AGI; the form starts from federal total income (before every adjustment). PE matches the form. Foreign earned income and other exclusions PE models as deductions are counted by PE but not by the statute | TWO-READINGS | Under the statute, income lower (rare) |
| OH | Homestead exemption | Timing: the law tests the prior year's modified AGI and the formula reads `oh_modified_agi` at `period.last_year`, but with one year of inputs that read returns 0 (core gives the default for an earlier period, and `state_code` is not OH there). Total income is 0 and the income limit never binds in the app or a microsimulation | CONFIRMED (timing; read from code, not run) | Income too low, exemption granted to every aged or disabled homeowner |
| OH | Homestead exemption | Income categories: total income is Ohio modified AGI (Ohio AGI + business income deduction + qualifying capital gain deduction), as R.C. 323.151(C) and 5747.01(II) define it. No category gap found | match | none |
| OH | Homestead exemption | Owners who received the reduction for 2013 are exempt from the income test; PE has no input for that and tests everyone | NOT-MODELABLE | Exemption too low for grandfathered owners above the limit |
| WV | Homestead excess property tax credit | Disability insurance benefits outside federal AGI (`tax_exempt_disability_benefits`) are not counted; § 11-21-23(d)(1)(C) counts "Workers' compensation and loss of earnings insurance". The form's line 4c names only workers' compensation in its parenthetical | CONFIRMED (statute over form) | Income too low, credit too high (input defaults to 0) |
| WV | Homestead excess property tax credit | Tier 1 railroad benefits outside federal AGI are not counted | COVERED (#10722) | Income too low |
| WV | Homestead excess property tax credit | Gambling winnings are missing from federal gross income on main | COVERED (#10070) | Income too low |
| WV | Homestead excess property tax credit | Other household members: Schedule HEPTC-1 line 4e adds "the income of all individuals living in the household but would file a separate tax return"; the statute defines gross household income from federal AGI plus four items and names no one else. PE counts the tax unit only | TWO-READINGS (agency counts them) | Under the form's reading, income too low |
| WV | Homestead excess property tax credit | SSI: line 4d counts "Social Security benefits, including SSI and SSDI"; the statute says "Nontaxable Social Security benefits". PE leaves SSI out | TWO-READINGS (agency counts it) | Under the form's reading, income too low |
| WV | Senior citizens tax credit | Income is plain federal AGI (≤ 150% of the poverty guideline), not gross household income; PE uses `adjusted_gross_income`. The two definitions differ in law and PE keeps them apart | match | none |
| IA | Low-income exemption, tax reduction, alternate tax (modified income, 2023 on) | The qualified business income deduction is added back twice: once inside `taxable_income_deductions` and again as its own list entry | CONFIRMED | Modified income too high, alternate tax and reduction cap too high, exemption denied |
| IA | Low-income exemption, tax reduction, alternate tax (modified income, 2023 on) | Every federal deduction from taxable income is added back, including the 2025-2028 tips, overtime and car loan interest deductions and the 2026 non-itemizer charitable deduction. Iowa Code 422.5 adds back only the itemized or standard deduction, the personal exemption deduction and the QBI deduction | CONFIRMED | Modified income too high, tax too high |
| IA | Low-income exemption, tax reduction, alternate tax (modified income, 2023 on) | Federal and Iowa taxable income are floored at zero before the deductions are added back; Iowa lets line 2 go negative. A filer whose deductions exceed AGI gets modified income of at least the standard deduction, above the $9,000 / $13,500 limits | CONFIRMED | Modified income too high; `ia_is_tax_exempt` false for exempt filers (tax effect usually nil) |
| IA | Low-income exemption, tax reduction, alternate tax | Gambling winnings are missing from federal gross income on main | COVERED (#10070) | Modified income too low |
| IA | Low-income exemption, tax reduction, alternate tax | No input: lump-sum distributions (Form 4972) and net operating loss carryovers, which the worksheets add | NOT-MODELABLE | Modified income too low |
| IA | Modified income, 2021-2022 | The reportable Social Security add-back comes from the 2021 and 2022 instructions, which I did not open; the 2022 statute names only excluded pensions | UNVERIFIED | n/a (historic years) |

## 1. Massachusetts — senior circuit breaker total income (Schedule CB)

### What PE does
- `variables/gov/states/ma/tax/income/credits/senior_circuit_breaker/ma_scb_total_income.py` (TaxUnit, YEAR): `max(0, ma_gross_income + add-backs - exemptions)`.
- Add-backs: `parameters/.../senior_circuit_breaker/income/disallowed_deductions.yaml` = `social_security`, `tax_exempt_unemployment_compensation`, `tax_exempt_pension_income`, `taxable_public_pension_income`, `tax_exempt_interest_income`, `ssi`, `ma_state_supplement`, `tanf`, `military_retirement_income` (SNAP and WIC commented out). Person-level items are summed over head and spouse only (`tax_unit_non_dep_add`); `tanf` is the SPM unit's.
- `ma_gross_income` = head's and spouse's `irs_gross_income` (each source floored at 0 per person) + `ma_gross_income_loss_adjustment` (business, farm, rental and partnership losses restored) + excess business loss + foreign earned income add-back − taxable Social Security − state tax refunds − `taxable_public_pension_income` − `military_retirement_income`, floored at 0. It is **before** the § 2(d) deductions that `ma_part_b_agi` takes.
- Exemptions subtracted: $700 per head/spouse 65+, $2,200 per blind head/spouse, $1,000 per dependent.
- Read by `ma_senior_circuit_breaker` only (the income limit by filing status and the 10% threshold).

### What the law says
- M.G.L. c. 62 § 6(k)(1), "Taxpayer's total income": "the sum of the taxpayer's Part A adjusted gross income, Part B adjusted gross income and Part C adjusted gross income, as defined in section 2, increased by, to the extent they are excluded or subtracted from adjusted gross income, the following: the total amount of income and receipts from social security, retirement, pension, or annuities, cash, but not in-kind, public assistance, tax-exempt interest and dividends, net capital losses deducted pursuant to paragraph (2) of subsection (c) of section 2, net losses in any class of Part C adjusted gross income as defined in subsection (e) of section 2, capital gains deducted pursuant to subparagraph (K) of paragraph (1) of subsection (d) of section 2, income from a partnership or trust not included therein and gross receipts from any other source other than assistance received by this subsection; and reduced by the total amount of the exemptions allowed by subparagraphs (B) and (C) of paragraph (1), ... and paragraph (3), of subsection (b) of section 3."
- 2025 Schedule CB (file p. 1): line 3 Massachusetts AGI (worksheet), line 4 "Full amount of Social Security benefits received before Medicare premiums", line 5 "Pensions/annuities/IRA/Keogh distributions not taxed on your Massachusetts tax return", line 6 "Miscellaneous income, including cash public assistance", line 8 "Combine Form 1, lines 2b through 2d", line 9 qualifying income.
- Schedule CB line 3 worksheet (file p. 2): "1. Enter your total 5.0% income from Form 1, line 10 ... Not less than 0"; "2. Enter the total of Schedule Y, lines 2 through 9b and line 10"; "3. Subtract line 2 from line 1"; Part 2 adds Schedule B line 9, lines 6a/6b and line 15; Part 3 adds "any gains (not including any losses) included in U.S. Schedule D".
- 2025 Form 1 instructions (file p. 30), line 6: "This includes but is not limited to food stamps and welfare payments, disability income, gifts, sick pay, worker's compensation and return of capital."
- DOR web page (read through a reader proxy because mass.gov returns 403 to scripts; saved as `src/ma_scb_webpage.md`): lists "Workers' compensation (Schedule CB, Line 6)", "Previously taxed income distributions (Schedule CB Line 5) from: IRA/Keogh ...", "Gains from sale of personal residence under $250,000/$500,000", and "Generally, do not add back anything excluded from federal gross income into the total income calculation if it's not defined as income and not included in Massachusetts gross income by specific law."
- TIR 01-19 (same proxy; `src/ma_tir_01_19.md`): "gross receipts (e.g., return of capital or gifts) from any other source except the tax credit itself"; example 3 adds a $25,000 pension "not taxable in Massachusetts" to $21,000 of AGI.

### Differences
1. **AGI deductions (CONFIRMED, overcount).** PE's comment says starting from gross income is "an equivalent path" to starting from AGI. It is for capital losses (partly, see 2) but not for the § 2(d) deductions: `ma_part_b_agi` subtracts the federal above-the-line deductions Massachusetts allows (HSA, self-employed health insurance and pension contributions, alimony paid, student loan interest, educator expenses ...), and `ma_scb_total_income` never does. The statute starts from AGI and adds back only income and receipts; the worksheet subtracts Schedule Y lines 2-9b and 10. A filer with $30,000 of wages and a $2,000 HSA deduction has $27,300 of total income, not $29,300.
2. **Cross-class capital losses (CONFIRMED, undercount).** `irs_gross_income` adds `max(0, capital_gains)` per person and `capital_gains` is short-term plus long-term, so a $10,000 long-term loss wipes out a $10,000 short-term gain. Under § 2(c)(2)(b) that loss is deducted from Part A gains, and § 6(k)(1) adds it back; the worksheet takes Schedule B line 15 (before short-term losses) and Schedule D gains "not including any losses".
3. **Tax-exempt retirement account distributions (CONFIRMED, undercount).** `tax_exempt_pension_income` is added but `tax_exempt_retirement_distributions` is not.
4. **Workers' compensation (CONFIRMED, undercount).** Named by DOR; `workers_compensation` exists.
5. **EAEDC and general assistance (CONFIRMED, undercount).** `ma_eaedc` is modeled; cash public assistance is in the statute's list.
6. **Nontaxable disability and sick pay (CONFIRMED, undercount).** `tax_exempt_disability_benefits` exists (default 0).
7. Railroad benefits: covered by #10722. Gambling winnings: covered by #10070 (federal gross income).

### Open PRs checked
Searches "Massachusetts circuit breaker", "ma_scb", "Massachusetts senior": #10722 (railroad; touches this list), #10070 (gambling; federal), #9894 (dependents' capital income; touches MA Part A/C variables, not this definition), #10764 (benefit programs only). None covers findings 1-6.

### Two readings
- SNAP: statute "cash, but not in-kind"; DOR counts food stamps. PE follows the statute and says so in the YAML.
- Veterans' benefits, child support, alimony outside federal gross income: the statute's catch-all "gross receipts from any other source" reaches them, and DOR counts comparable receipts (workers' compensation, gifts), but DOR names none of them and states a general rule against adding back federally excluded amounts. PE leaves them out.
- Fuel assistance: DOR counts it "if paid directly to you" and treats discounted-rate programs as in-kind. Not listed in PE; no row.

### Not verified
- 830 CMR: I found no regulation on § 6(k); DOR's guidance is TIR 01-19 and the annual TIRs. TIR 25-7 (2025 amounts) was not opened; the 2025 limits were read from the 2025 Schedule CB.
- Unrelated to this definition but seen on the way: `gov.states.ma.tax.income.ald.disallowed` lists `early_withdrawal_penalty`, while 2025 Schedule Y line 2 is "Penalty on early savings withdrawal". Not audited.

## 2. Maine — property tax fairness credit and sales tax fairness credit income (Schedule PTFC/STFC)

### What PE does
- `parameters/gov/states/me/tax/income/credits/fairness/income_sources.yaml`: `irs_gross_income`, `tax_exempt_social_security`, `tax_exempt_interest_income`.
- `variables/gov/states/me/tax/income/credits/fairness/me_sales_and_property_tax_fairness_credit_income.py` (TaxUnit, YEAR): `adds` of that list.
- `irs_gross_income` is person-level, zero for tax unit dependents, and adds `max(0, source)` for each entry of `gov.irs.gross_income.sources`. It is before every above-the-line deduction. So no loss and no adjustment ever reduces Maine income.
- `tax_exempt_social_security` (tax unit) = all members' Social Security less the taxable part. `tax_exempt_interest_income` is summed over all members.
- Read by `me_sales_tax_fairness_credit` (phase-out) and `me_property_tax_fairness_credit_base_cap` (4% of income).

### What the law says
- 36 M.R.S. § 5219-KK(1)(D) and § 5213-A(1)(B) (identical): "'Income' means federal adjusted gross income increased by the following amounts: (1) Trade or business losses; capital losses; any net loss resulting from combining the income or loss from rental real estate and royalties, the income or loss from partnerships and S corporations, the income or loss from estates and trusts, the income or loss from real estate mortgage investment conduits and the net farm rental income or loss; any loss associated with the sale of business property; and farm losses included in federal adjusted gross income; (2) Interest received to the extent not included in federal adjusted gross income; (3) Payments received under the federal Social Security Act and railroad retirement benefits to the extent not included in federal adjusted gross income; and (4) The following amounts deducted in arriving at federal adjusted gross income: (a) Educator expenses ... (n) The tuition and fees deduction".
- MRS Rule 813 .03 (file p. 4) restates it: "C. Social security and railroad retirement benefits that are not included in federal adjusted gross income". Rule 813 .01(C) (p. 1): joint filers claim "based on their joint income".
- 2025 Schedule PTFC/STFC (file p. 1): line 2a "Federal total income. (From federal Form 1040, line 9 ...)", 2b Social Security (line 6a minus 6b) and railroad retirement not on 2a, 2c "Interest not included on line 2a", 2d "Loss add-backs".
- Instructions (file p. 3), line 1a: "Enter all payments received under the federal Social Security Act, including regular social security benefits, social security disability benefits and supplemental security income. Include the gross amount before Medicare is subtracted." Line 2b: "enter all payments received under the federal Social Security Act and the amount of railroad retirement benefits received. See the instructions for line 1a above."
- Instructions (file p. 4), line 2d: "Enter on line 2d the amount of any negative amount (net loss) included on federal Form 1040 or Form 1040-SR, line 7 and federal Schedule 1, lines 3, 4, 5, 6, and 8a through 8z."

### Differences
1. **SSI (CONFIRMED, undercount).** Paid under title XVI of the Social Security Act, never in federal AGI, named by the form. `ssi` is not in the list. An SSI recipient with $10,000 of Social Security and $3,000 of SSI has $13,000 of income, not $10,000.
2. **Losses netted on the federal return (CONFIRMED, overcount).** The law adds back a loss only where the federal line is a net loss. PE floors every source for every person, so a rental loss absorbed by partnership or trust income on Schedule 1 line 5, or one spouse's capital or business loss absorbed by the other's gain, is added back although federal AGI kept it netted.
3. Railroad benefits (#10722), dependents' Social Security (#10647), dependents' tax-exempt interest (#9894), gambling winnings (#10070): covered.

### Open PRs checked
Search "Maine fairness credit": #10647, #10722, #9894 (all touch this definition; none adds SSI or changes the loss treatment). #10070 (federal).

### Two readings
- Unlisted adjustments. The statute adds back fourteen named deductions; the form starts from line 9 total income, which is before all adjustments. They differ only for adjustments outside the list (the "other adjustments" of Schedule 1 line 24). PE matches the form. For the foreign earned income exclusion, employer adoption assistance and possession income, which PE subtracts as above-the-line deductions, PE counts the income; the statute does not (it starts from federal AGI and does not list them); the form does only on a literal reading of line 2d ("any negative amount ... lines 8a through 8z"). Rare.

### Not verified
- Whether Maine Revenue Services treats TANF or other title IV payments as "payments received under the federal Social Security Act": no text found; the form's examples are Social Security, disability and SSI. Recorded as a match (not counted) with a note.
- The 2025 Form 1040ME general instructions were downloaded but not needed.

## 3. Ohio — homestead exemption total income (DTE 105A)

### What PE does
- `variables/gov/states/oh/tax/property/homestead_exemption/oh_homestead_exemption_total_income.py` (TaxUnit, YEAR, no `defined_for`): `tax_unit("oh_modified_agi", period.last_year)`.
- `oh_modified_agi` (TaxUnit, `defined_for = StateCode.OH`) = `oh_agi` + `oh_business_income_deduction` + `oh_qualifying_capital_gain_deduction`. `oh_agi` sums `oh_agi_person` = `adjusted_gross_income_person` + `oh_additions` − `oh_deductions`.
- No parameter list of its own. `income_limit.yaml`: 40,000 (2025), 41,000 (2026).
- Read by `oh_homestead_exemption_eligible` (`total income <= income_limit`), which gates `oh_homestead_exemption`.

### What the law says
- R.C. 323.151(C): "'Total income' means modified adjusted gross income, as that term is defined in section 5747.01 of the Revised Code, of the owner and the owner's spouse for the year preceding the year in which application for a reduction in taxes is made."
- R.C. 5747.01(II): "'Modified adjusted gross income' means Ohio adjusted gross income plus any amount deducted under divisions (A)(28) and (34) of this section for the taxable year." (A)(28) is the business income deduction; (A)(34) is "qualifying capital gains and deductible payroll".
- R.C. 323.152(A)(1)(b)(iii): the reduction applies "If the person is not described in division (A)(1)(b)(i) or (ii) of this section and the person's total income does not exceed thirty thousand dollars, as adjusted under division (A)(1)(d)".
- R.C. 323.153(A)(3): applications "shall be filed on or before the thirty-first day of December of the year for which the reduction is sought. The original application and any subsequent application for a reduction in manufactured home taxes shall be filed in the year preceding the year for which the reduction is sought."
- DTE 105A (Rev. 01/21; file p. 3): "'Total Income' is that of the owner and the owner's spouse for the year preceding the year for which you are applying." File p. 1: "For real property, file on or before December 31 of the year for which the exemption is sought."
- DTE 105H (Rev. 10/19; file p. 1): "your county auditor is required to verify an applicant's modified adjusted gross income for the year prior to the year of application"; "If you are married, the amounts must include income and deductions for both you and your spouse"; p. 2 line 4: "Do NOT include any Social Security benefits as they are not taxable in Ohio."

### Timing
- Law: for real property and tax year T the application year is T, so the income year is T−1. PE's formula says the same (`period.last_year`).
- In practice the read returns 0. policyengine-core (`.venv311/Lib/site-packages/policyengine_core/simulations/simulation.py`, lines 816-828) carries an input forward to later periods but returns the default for an earlier one: "if last_known_period.start > period.start: return holder.default_array()". With one year of inputs, the prior year has no wages and no `state_code` (so `defined_for = StateCode.OH` is false). `oh_homestead_exemption_total_income` is 0 and the limit never binds. The existing tests pass only because they give `oh_modified_agi` and `state_code` for both years.
- The repo's convention for this elsewhere: `or_tax_before_credits_in_prior_year` is an input that "defaults to the current year's Oregon income tax before credits as a proxy", and the Montana elderly credit comment (#10331) says a prior-year read "reads 0 whenever the inputs cover only one year".
- I could not run the model, so this is from reading the code. The test in `tests-E/oh_homestead_exemption_total_income.yaml` assumes the fix is a current-year proxy when no prior-year amount is supplied; if the fix is a new prior-year input instead, the expected values still hold when that input defaults to the current year.
- Manufactured and mobile homes apply in the year before the tax year, so their income year is T−2. PE has one exemption variable and does not separate them.

### Income categories
Total income is Ohio's general modified AGI by cross-reference, and PE uses the same variable the income tax credits use. Business income deducted under (A)(28) and the 2026 capital gain deduction under (A)(34) are added back. Social Security, military retired pay and income outside federal AGI are out in law and in PE. I did not audit Ohio AGI's own additions and deductions.

### Open PRs checked
Searches "Ohio homestead", "oh_modified_agi": #9939 (dependents' items in Ohio subtractions) and #10722 (railroad) touch Ohio AGI inputs, not this variable or its timing. No open PR or issue on the prior-year read.

### Two readings
None on the definition. (Age: the statute's "sixty-five years of age or older" means having "attained age sixty-four prior to the first day of January of the year of application"; not an income matter.)

### Not verified
- The 2025 and 2026 income limits ($40,000, $41,000): not checked against the Department of Taxation's annual notice; outside the income definition.
- Spouses filing separately: the law combines owner and spouse; I did not trace how PE represents the other spouse's tax unit here.
- Whether DTE 105A has a revision later than 01/21 that mentions the (A)(34) add-back.

## 4. West Virginia — homestead excess property tax credit gross household income (Schedule HEPTC-1), and the senior citizens tax credit

### What PE does
- `parameters/gov/states/wv/tax/income/credits/heptc/gross_household_income/sources.yaml` (from 2012): `adjusted_gross_income`, `wv_additions`, `tax_exempt_interest_income`, `workers_compensation`, `tax_exempt_social_security`.
- `variables/.../heptc/wv_gross_household_income.py` (TaxUnit, YEAR): `adds` of that list. Losses and adjustments reduce it exactly as they reduce federal AGI. `wv_additions` is only the input `wv_other_additions`. `tax_exempt_social_security` and `tax_exempt_interest_income` cover every tax unit member.
- Readers: `wv_homestead_excess_property_tax_credit` (property tax − SCTC − 4% of gross household income, floored, capped at $1,000) and `..._eligible` (same comparison, plus federal AGI ≤ 300% of `tax_unit_fpg`).
- Senior citizens tax credit: `wv_sctc_eligible` tests `adjusted_gross_income` ≤ 150% of `tax_unit_fpg`. It does not read gross household income.

### What the law says
- W. Va. Code § 11-21-23(a): credit equal to the amount by which property taxes paid "minus the amount of credit authorized in section twenty-one of this article, exceeds four percent of the taxpayer's gross household income for the tax year".
- § 11-21-23(d)(1): "'Gross household income' is defined as federal adjusted gross income plus the sum of the following: (A) Modifications in subsection (b), section twelve of this article increasing federal adjusted gross income; (B) Federal tax-exempt interest reported on federal tax return; (C) Workers' compensation and loss of earnings insurance; and (D) Nontaxable Social Security benefits".
- § 11-21-23(h)(2): "'Low income' means federal adjusted gross income for the tax year that is three hundred percent or less of the federal poverty guideline for the year in which property tax was paid, based upon the number of individuals in the family unit residing in the homestead".
- 2025 Schedule HEPTC-1 (booklet file p. 11): line 4 federal AGI; 4a "increasing income modifications reported on line 61 of Schedule M"; 4b "federal tax-exempt interest income"; 4c "amount received in 2025 in the form of earnings replacement insurance (Workers' Compensation Benefits)"; 4d "Social Security benefits, including SSI and SSDI, received that are NOT included in your Federal Adjusted Gross Income"; 4e "the income of all individuals living in the household but would file a separate tax return"; line 6 "Total Gross Income".
- § 11-21-21(b)(1) (senior citizens tax credit): "'Low income' means federal adjusted gross income for the taxable year that is one hundred fifty percent or less of the federal poverty guideline". TSD-411 (Rev. July 2026, p. 1): "The eligible persons' federal adjusted gross income and the number of persons in the home determine eligibility ... The income does not include any social security income" (for those not required to file).

### Differences
1. **Loss of earnings insurance (CONFIRMED, undercount).** The statute's item (C) has two parts; PE lists only `workers_compensation`. `tax_exempt_disability_benefits` holds disability insurance benefits outside federal AGI. The form's parenthetical narrows the line to workers' compensation; the statute controls.
2. Tier 1 railroad benefits: covered by #10722. Gambling winnings: covered by #10070.
3. Everything else in the list matches the statute item for item.

### Two readings
- **Other household members (form line 4e).** Statute: federal AGI plus four add-backs, "the taxpayer's" gross household income. Form: also the income of everyone living in the household who would file separately. The term "household" in the defined name leaves room for the form's reading, and the agency follows it. PE counts one tax unit.
- **SSI (form line 4d).** Statute: "Nontaxable Social Security benefits". Form: "including SSI and SSDI". The federal meaning of "social security benefit" (IRC 86(d)) leaves SSI out, and #10722 relies on that federal meaning to bring tier 1 railroad benefits in. PE leaves SSI out.
- Both go the same direction: under the agency's reading PE's income is too low and the credit too high.

### Senior citizens tax credit
Modeled (`wv_sctc`, `wv_sctc_eligible`). Its income test is federal AGI alone, so it differs from gross household income by the four add-backs; PE matches. Not an income matter but noted: the guideline size in law is the "family unit residing in the homestead" and PE uses the tax unit.

### Open PRs checked
Searches "West Virginia homestead", "wv_gross_household_income", "West Virginia senior citizen": #10722 (adds tier 1 railroad benefits to this list and a test file), #10647 (dependents' Social Security; does not touch this list), #10673 (529 contributions), #9894 (WV low-income family credit AGI). None adds loss-of-earnings insurance, SSI or other household members.

### Not verified
- No West Virginia legislative rule (Title 110) on § 11-21-23 was found or opened.
- Whether the Tax Division accepts private disability insurance benefits on line 4c in practice.

## 5. Iowa — modified income (low-income exemption, single-filer tax reduction, alternate tax)

### Years
The definition is still current law. Iowa Code 2026 § 422.5(2)-(3) keeps the exemption ($9,000 single, $13,500 others; $24,000 and $32,000 at 65), the reduction, and the alternate tax at 4.3% of net income over the limit. The 2025 worksheets (41-145, 41-146) apply it. PE has two lists: 2021-2022 and 2023 on. I audited 2023 on in full and 2021-2022 briefly.

### What PE does
- `parameters/gov/states/ia/tax/income/modified_income/sources.yaml`: from 2021 `ia_net_income`, `ia_pension_exclusion`, `ia_reportable_social_security`; from 2023 `ia_taxable_income_consolidated`, `taxable_income_deductions`, `qualified_business_income_deduction`.
- `ia_modified_income` (TaxUnit, YEAR): `adds` of the list.
- `ia_taxable_income_consolidated` = `max(0, taxable_income + ia_additions_consolidated − ia_subtractions_consolidated)`; federal `taxable_income` = `max(0, AGI − exemptions − taxable_income_deductions)`.
- `taxable_income_deductions` is the standard deduction or itemized deductions plus `qualified_business_income_deduction`, `tip_income_deduction`, `overtime_income_deduction`, and from 2025 `additional_senior_deduction` and `auto_loan_interest_deduction` (plus `charitable_deduction_for_non_itemizers` for non-itemizers, `wagering_losses_deduction` for itemizers).
- Readers: `ia_is_tax_exempt`, `ia_reduced_tax`, `ia_alternate_tax_consolidated` (2023 on), `ia_alternate_tax_unit` (2021-2022).

### What the law says
- Iowa Code 2026 § 422.5(2)(a) (file p. 1; (3)(a) repeats it for age 65+): "The tax shall not be imposed on a resident or nonresident whose net income, as defined in section 422.7, is thirteen thousand five hundred dollars or less ... or nine thousand dollars or less in the case of all other persons ... In calculating net income for purposes of this subsection, any amount of itemized or standard deduction, personal exemption deduction, or qualified business income deduction that was allowed as a deduction in computing federal taxable income under the Internal Revenue Code shall be added back."
- § 422.5(2)(b): "the alternate state individual income tax rate of four and three-tenths percent times the portion of the net income in excess of thirteen thousand five hundred dollars".
- 2025 expanded instructions (file p. 10): "The following items must be added ... to determine if you qualify for low-income exemption, alternate tax, or tax reduction: 1. Iowa taxable income from IA 1040, line 4 2. Standard deduction or itemized deductions from IA 1040, line 1d not to exceed the amount that is included in IA 1040, line 2 3. Personal exemption allowed for federal purposes from federal Schedule 1-A, line 37 4. Qualified business income deduction from IA 1040, line 1e 5. Any amount of lump-sum distribution separately taxed on federal form 4972 6. Carryover of net operating loss claimed on the IA 1040 Schedule 1, line 17b".
- Same instructions, line 2 (file pp. 9-10): "If the amount of federal taxable income is zero, subtract the amount reported on IA 1040 lines 1d and 1e, and federal form 1040 line 13b from the amount reported on IA 1040, line 1c and report this amount (this amount can be negative)."
- Line 1f (file p. 9): the enhanced deduction for seniors "is considered a personal exemption" and "must be added back when calculating the low-income exemption, alternate tax, tax reduction".
- 2025 Alternate Tax Worksheet 41-145 line 1 and Tax Reduction Worksheet 41-146 line 1: the same six items.

### Differences (2023 on)
1. **QBI deduction counted twice (CONFIRMED, overcount).** It is in `taxable_income_deductions` and listed again. A filer with a $2,000 QBI deduction has modified income $2,000 too high.
2. **Deductions the law does not add back (CONFIRMED, overcount).** The statute and the instructions add back three kinds of deduction. `taxable_income_deductions` also holds the tips, overtime and car loan interest deductions (Form 1040 line 13b, 2025-2028) and the non-itemizer charitable deduction (2026 on). Iowa's line 2 keeps those deductions, and they stay out of modified income.
3. **Zero floors (CONFIRMED, overcount).** Iowa's line 2 can be negative, so line 4 plus the add-backs comes back to about federal AGI plus Iowa modifications. PE floors both taxable incomes at zero first. The result is a modified income no lower than the deductions, which already exceed the under-65 limits; the exemption flag is wrong for exactly the filers it is for. Regular tax on zero taxable income is zero, so tax changes only when Iowa additions make line 4 positive.
4. Lump-sum distributions and NOL carryovers: no inputs.
5. Gambling winnings: covered by #10070.

### 2021-2022 (brief)
Iowa Code 2022 § 422.5(3)(a): "net income includes all amounts of pensions or other retirement income ... not taxable under this subchapter as a result of the government pension exclusions". PE adds `ia_pension_exclusion` (match) and `ia_reportable_social_security`, which it sources to the 2021 and 2022 instructions. I did not open those instructions, so the Social Security add-back is unverified.

### Open PRs checked
Searches "Iowa modified income", "Iowa alternate tax", "ia_modified_income": #10070 (gambling; touches Iowa gross income sources), #10722 and #9894 (touch `ia_reportable_social_security` only). None changes the 2023 list.

### Two readings
None found. On the senior deduction the statute ("personal exemption deduction") and the agency (line 1f) agree.

### Not verified
- 2021 and 2022 IA 1040 instructions (the Social Security add-back).
- Whether the "not to exceed the amount that is included in IA 1040, line 2" limit on the standard deduction add-back ever binds once line 2 may be negative; I read it as not binding.
- Iowa Code § 422.7 itself (the definition of net income) was not opened; I relied on § 422.5 and the 2025 instructions.
