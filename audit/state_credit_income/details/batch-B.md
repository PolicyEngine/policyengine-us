# State credit income-definition audit: batch B
Code read at `upstream/main` 06c0dcbc54 (no checkout, nothing run). Sources are under `C:/tmp/sci-audit/src/` unless a path is given. Finished: Montana, North Dakota, New Mexico, Oklahoma, Missouri. All five definitions are written.

## Findings

| State | Credit | Finding | Class | Dollar direction |
|---|---|---|---|---|
| MT | Elderly homeowner/renter credit | Alimony from a divorce after 2018 is outside federal AGI and the source list doesn't add it; MCA 15-30-2337(9)(a)(iii) and Schedule 2EC line 9 count all alimony | CONFIRMED | Income too low, credit too high |
| MT | Elderly homeowner/renter credit | Tax-exempt 401(k), 403(b) and SEP distributions are left out, though the tax-exempt IRA and pension amounts are counted; (9)(a)(i), ARM 42.4.301(2)(d), line 5 | CONFIRMED | Income too low, credit too high |
| MT | Elderly homeowner/renter credit | Savings bond interest excluded under IRC 135 (and employer adoption assistance) reduces federal AGI and isn't added back; (9)(a)(vii) counts interest on federal bonds. An existing test pins the low figure | CONFIRMED | Income too low (small), credit too high |
| MT | Elderly homeowner/renter credit | Foreign earned income excluded under IRC 911 isn't added back; (9)(a) adds "all nontaxable income" | CONFIRMED | Income too low (rare), credit too high |
| MT | Elderly homeowner/renter credit | Refundable credits received: timing is right after #10331, but every receipt except the 2020-21 Economic Impact Payments is an input that defaults to 0 | Left by #10331 (no gap in law) | Income too low by default, credit too high |
| MT | Elderly homeowner/renter credit | Railroad retirement benefits not counted | COVERED (#10722) | Income too low until merged |
| MT | Elderly homeowner/renter credit | Gambling winnings not counted (not in federal gross income) | COVERED (#10070) | Income too low until merged |
| MT | Elderly homeowner/renter credit | Above-the-line deductions: the statute starts from federal AGI (PolicyEngine follows it); the 2025 Schedule 2EC adds gross lines with no adjustments | TWO-READINGS | Form reading gives higher income, lower credit |
| MT | Elderly homeowner/renter credit | Basis in nontaxable IRA distributions: (9)(b) reduces income by basis; ARM (2)(d) and line 4 count all IRA payments (PolicyEngine follows the agency) | TWO-READINGS | Statute reading gives lower income, higher credit |
| MT | Elderly homeowner/renter credit | Federal refundable credits received before 11/10/2017 (kept from #10331) | TWO-READINGS | Reading A gives higher 2009-2016 income |
| MT | Elderly homeowner/renter credit | Gifts, life insurance, scholarships, other survivor benefits, paid leave: inputs exist, the catch-all may reach them, the schedule names none | TWO-READINGS | Catch-all reading gives higher income |
| MT | Elderly homeowner/renter credit | Capital gains excluded from AGI (home sale), qualified charitable distributions, pension cost recovery inside `tax_exempt_pension_income`, Social Security paid to a nursing home, part-year household members | NOT-MODELABLE | Mixed: the first two undercount income, the next two overcount |
| ND | Renter's refund | Gambling winnings aren't counted: `market_income` has no such component, and #10070 adds them to federal gross income only | CONFIRMED | Income too low, refund too high |
| ND | Renter's refund | A net capital loss of any size reduces income; the homestead application takes Form 1040 line 7 (loss limited to $3,000) and the guideline lists only net gains | CONFIRMED (statute silent; both agency sources differ from PolicyEngine) | Income too low, refund too high |
| ND | Renter's refund | Tax-exempt interest, nontaxable pension and retirement distributions, and wages before elective deferrals are counted on main | COVERED (#10697) | Income too high, refund too low until merged |
| ND | Renter's refund | SSI isn't counted on main, though the application's line 7 names it | COVERED (#10724) | Income too low until merged |
| ND | Renter's refund | Railroad retirement not counted | COVERED (#10722) | Income too low until merged |
| ND | Renter's refund | TANF: statute counts public assistance; the guideline's item 11 says TANF isn't income (main follows the guideline, #10724 the statute) | TWO-READINGS | Statute reading gives higher income |
| ND | Renter's refund | Alimony after 2018: guideline counts alimony (main); the statute's exclusion clause may remove it (#10697) | TWO-READINGS | #10697 reading gives lower income |
| ND | Renter's refund | "Excluded from income by ... state law": North Dakota income tax reductions (retired military pay, U.S. interest) are kept in income, as the guideline does | TWO-READINGS | Other reading gives lower income, higher refund |
| ND | Renter's refund | `survivor_benefits` is excluded in full; the guideline excludes only workers' compensation survivor benefits and life insurance | TWO-READINGS (on what the input holds) | Possible undercount of income |
| NM | Low income comprehensive tax rebate, property tax rebate, child day care credit | Farm income (Schedule F, Form 4835) and partnership/S corporation income are not in the list; 7-2-2(L)(2), (5), (13). Open issue #10062, no PR | CONFIRMED | Income too low, rebates too high |
| NM | same | Workers' compensation is not in the list; 7-2-2(L)(18) | CONFIRMED | Income too low, rebates too high |
| NM | same | General assistance (and the New Mexico SSI supplement) not in the list; 7-2-2(L)(19), 3.3.1.10(A)(1)(d) NMAC | CONFIRMED | Income too low, rebates too high |
| NM | same | Disability benefits and sick pay not in the list; 3.3.1.10(C) NMAC | CONFIRMED | Income too low, rebates too high |
| NM | same | Discharge of indebtedness not in the list; 7-2-2(L)(12) | CONFIRMED | Income too low, rebates too high |
| NM | same | Gambling winnings not in the list (the file has a comment naming them and no entry); #10070 doesn't reach this list | CONFIRMED | Income too low, rebates too high |
| NM | same | Cash gifts not in the list; 7-2-2(L)(21) | CONFIRMED | Income too low, rebates too high |
| NM | same | Scholarships and grants not in the list; 3.3.1.10(A)(2) NMAC | CONFIRMED | Income too low, rebates too high |
| NM | same | Miscellaneous income (and strike, other survivor, guaranteed income payments) not in the list | CONFIRMED | Income too low, rebates too high |
| NM | same | Capital gain distributions and Form 4797 gains not in the list; 7-2-2(L)(3) | CONFIRMED | Income too low (small) |
| NM | same | Losses still net: a short-term loss reduces a long-term gain, and one spouse's loss reduces the other's income from the same source; 3.3.1.10(B) NMAC and PIT-RC line 9 | CONFIRMED (two rows) | Income too low, rebates too high |
| NM | same | Foreign earned income excluded under IRC 911 not added back | CONFIRMED (rare) | Income too low |
| NM | same | Military retired pay | COVERED (#10769) | Income too low until merged |
| NM | same | Railroad retirement | COVERED (#10722) | Income too low until merged |
| NM | same | Life insurance death proceeds: regulation ties item (10) to IRC 72 amounts; instructions count insurance settlements | TWO-READINGS | Second reading gives higher income |
| NM | same | Excluded home-sale gain, inheritances, settlements, cost-of-living allowances; both spouses' income when filing separately | NOT-MODELABLE | Income too low |
| OK | Sales tax relief credit, property tax credit | Income is summed over the tax unit; the statute counts "all persons occupying the same household" (68 O.S. 5012, 2904(3); 538-S line 13) | CONFIRMED | Income too low, credits too high |
| OK | same | IRA, 401(k), 403(b) and other retirement account distributions are not in the list (only `pension_income`); 538-S line 6 | CONFIRMED | Income too low, credits too high |
| OK | same | Veterans' disability compensation is not in the list, though the statute names it | CONFIRMED | Income too low, credits too high |
| OK | same | Loss-of-time insurance and disability benefits are not in the list, though the statute names them | CONFIRMED | Income too low, credits too high |
| OK | same | TANF is not in the list ("public assistance payments") | CONFIRMED (narrow) | Income too low for the property tax credit |
| OK | same | Nontaxable W-2 income (dependent care benefits) is subtracted from wages; 538-S line 1 includes it | CONFIRMED | Income too low |
| OK | same | School grants and scholarships are not counted; both forms name them | CONFIRMED (agency reading of the catch-all) | Income too low |
| OK | same | Gambling winnings (and strike, other survivor, guaranteed income payments) are not counted; #10070 doesn't reach this list | CONFIRMED | Income too low |
| OK | same | Foreign earned income excluded under IRC 911 not added back | CONFIRMED (rare) | Income too low |
| OK | same | Earned income credit: the forms count the credit received during the year (federal and Oklahoma); PolicyEngine counts this year's federal credit and no Oklahoma credit | TIMING | Either direction; the Oklahoma credit is always missing |
| OK | same | Military retired pay | COVERED (#10769) | Income too low until merged |
| OK | same | Railroad retirement | COVERED (#10722) | Income too low until merged |
| OK | same | Capital losses: PolicyEngine nets short- and long-term amounts before the floor (pinned by a test); "gross amount of income of every type" may bar any offset | TWO-READINGS | Second reading gives higher income |
| OK | same | Business income: positive net profit (PolicyEngine) or gross income before expenses (538-H instructions) | TWO-READINGS | Second reading gives higher income |
| OK | same | In-kind aid: 538-H names housing assistance as public assistance; the statute says "payments" | TWO-READINGS | Form reading gives higher income |
| MO | Property tax credit | Military retirement benefits are subtracted from Missouri AGI (143.121.3(12)) and never added back, though 135.010(5)(b) counts "all other public and private pensions". Same family as #10769, which doesn't cover Missouri | CONFIRMED | Income too low, credit too high |
| MO | Property tax credit | Interest on U.S. obligations is subtracted from Missouri AGI and not added back; 135.010(5)(e) | CONFIRMED | Income too low, credit too high |
| MO | Property tax credit | General assistance and the Missouri state supplement (`mo_ssp`) are not in the public assistance list; 135.010(5)(c) | CONFIRMED | Income too low, credit too high |
| MO | Property tax credit | Rental, estate and other Schedule E losses reduce income; only the capital loss is added back. 135.010(5)(d), and the instructions treat only Schedule C and F losses as business losses | CONFIRMED (agency reading of "trade or business") | Income too low, credit too high |
| MO | Property tax credit | Tax-exempt retirement account distributions (Roth IRA, 401(k), 403(b), SEP) are not added; the line 3 instructions take every Form 1099-R amount outside Missouri AGI | CONFIRMED (agency reading) | Income too low, credit too high |
| MO | Property tax credit | The spouse of a 100% service-connected disabled veteran still has their own veterans' benefits counted | CONFIRMED (rare) | Income too high, credit too low |
| MO | Property tax credit | Railroad retirement not counted | COVERED (#10722) | Income too low until merged |
| MO | Property tax credit | Child support: the forms count it on the public assistance line (PolicyEngine follows them); the statute's list doesn't include it | TWO-READINGS | Statute reading gives lower income, higher credit |
| MO | Property tax credit | Nontaxable pension cost recovery: statute says "total amount" (PolicyEngine); the instructions leave out excludable cost | TWO-READINGS | Agency reading gives lower income |
| MO | Property tax credit | Alimony after 2018: outside Missouri AGI and the statute's list (PolicyEngine); the MO-PTC instructions list alimony | TWO-READINGS | Form reading gives higher income |

Class: CONFIRMED (law is clear, PolicyEngine differs), TWO-READINGS, COVERED (an open PR fixes it), NOT-MODELABLE (no input), UNVERIFIED. Dollar direction is the effect of the gap on the income figure and on the credit.

## Across the five definitions

Counts (CSV rows): 154 rows; 82 match; 35 confirmed gaps (34 undercount income, 1 overcounts) plus 1 timing finding; 15 two-readings; 13 covered by an open PR; 8 not modelable; 0 unverified rows. What could not be opened is listed under each definition.

- **The #10769 pattern recurs in Missouri.** Missouri AGI subtracts military retirement benefits, and the property tax credit's income adds all public pensions back; PolicyEngine doesn't. No open PR covers it.
- **The #10331 timing pattern recurs in Oklahoma.** Forms 538-S and 538-H count the earned income credit "received in 2025"; PolicyEngine counts the credit earned on the 2025 return and no Oklahoma credit.
- **Oklahoma sums the wrong entity.** The statute counts every person in the household; `ok_gross_income` sums one tax unit.
- **Lists built source by source miss whole categories.** New Mexico's list lacks farm, partnership, workers' compensation, disability, debt relief, general assistance, gifts, scholarships, gambling and miscellaneous income. Oklahoma's lacks retirement account distributions, veterans' benefits, disability benefits and TANF.
- **Gambling winnings are outside federal gross income on main.** #10070 fixes that for definitions that read federal AGI (Montana, Missouri). North Dakota (through `market_income`), New Mexico and Oklahoma keep the gap after it merges.
- **Tax-exempt retirement account distributions** (`tax_exempt_401k_distributions` and the 403(b) and SEP equivalents) are missed in Montana and Missouri, which add back only `tax_exempt_pension_income` or the IRA amount.
- **Loss netting.** New Mexico and Oklahoma floor each source after summing the tax unit, so one person's loss offsets another's income, and short-term losses offset long-term gains. North Dakota lets a net capital loss of any size reduce income. Missouri adds back only the capital loss.

## 1. Montana: elderly homeowner/renter credit, gross and net household income

### What PolicyEngine does
- **Files.** `parameters/gov/states/mt/tax/income/credits/elderly_homeowner_or_renter/gross_income_sources.yaml`; `variables/gov/states/mt/tax/income/credits/mt_elderly_homeowner_or_renter/mt_elderly_homeowner_or_renter_credit_gross_household_income.py` and `..._net_household_income.py`, `..._federal_refundable_credits.py`, `..._other_federal_refundable_credits.py`, `..._state_refundable_credits.py`, `..._received.py`, `..._property_tax_rebate_received.py`, `..._unemployment_compensation_addback.py`.
- **List (2023 onward).** `adjusted_gross_income_person`, `tax_exempt_interest_income`, `tax_exempt_ira_distributions`, `tax_exempt_pension_income`, `veterans_benefits`, `child_support_received`, `strike_benefits`, `general_assistance`, `ssi`, `mt_ssp`, `tanf_person`, `workers_compensation`, `gi_cash_assistance`, `tax_exempt_disability_benefits`, the unemployment add-back, and four receipt amounts: state refundable credits, this credit received, federal refundable credits, and the property tax rebate received. The 2009 list has no federal credits or rebate; the 2017 list adds federal credits.
- **Formula adds.** A tax unit dependent's own gross income less their own deductions; Social Security not already counted as taxable; `loss_ald` (on the head); and capital gains that losses or the carryover had netted away.
- **Entity.** Person-level. `..._net_household_income` sums it over `person.household` and puts the total on each tax unit head, so every household member counts, including people on other returns.
- **Loss floors.** `irs_gross_income` floors each federal source at zero, and the formula adds back `loss_ald`, so no business, rental or capital loss reduces income.
- **What federal AGI already holds.** `gov.irs.gross_income.sources` includes `military_retirement_income`, `taxable_pension_income`, `taxable_retirement_distributions`, `taxable_roth_conversions`, `taxable_alimony_income`, `taxable_disability_benefits`, `miscellaneous_income`, `debt_relief` and `estate_income`. It doesn't include `gambling_winnings`, `railroad_benefits`, `survivor_benefits` or `pfml_benefits`.
- **Net household income.** (gross - $12,600) times the rate from the 15-30-2340(4) table; both match the statute.
- **Readers.** `mt_elderly_homeowner_or_renter_credit` (through net household income and the 15-30-2340(5) gross-income multiplier) and `..._eligible`.

### What the law says
- **MCA 15-30-2337(4)** (`mt_mca_15-30-2337.html`): "'Gross household income' means all income received by all individuals of a household while they are members of the household."
- **MCA 15-30-2337(9)(a)**: "'Income' means, except as provided in subsection (9)(b), federal adjusted gross income, without regard to loss, as that quantity is defined in the Internal Revenue Code of the United States, plus all nontaxable income, including but not limited to: (i) the amount of any pension or annuity, including Railroad Retirement Act benefits and veterans' disability benefits; (ii) the amount of capital gains excluded from adjusted gross income; (iii) alimony; (iv) support money; (v) nontaxable strike benefits; (vi) cash public assistance and relief; (vii) interest on federal, state, county, and municipal bonds; and (viii) all payments received under federal social security except social security income paid directly to a nursing home."
- **MCA 15-30-2337(9)(b)**: "For the purposes of this subsection (9), income is reduced by the taxpayer's basis."
- **MCA 15-30-2337(8)**: "'Household income' means the amount obtained by subtracting $12,600 from gross household income."
- **ARM 42.4.301(2)**, current from 9/7/2024 (`mt_arm_42-4-301_current.html`): gross household income "includes: (a) all capital gains income transactions less return of capital; (b) federal refundable tax credits received; and (c) any state refundable tax credits received, including elderly homeowner/renter credit refunds; (d) all federal taxable and nontaxable pension, annuity, and IRA payments received during the year; (e) qualified charitable distributions under IRC § 408(d)(8); and (f) conversion from a traditional IRA to Roth IRA under IRC § 408A(d)(3)."
- **2025 Form 2 instructions, Schedule 2EC** (`mt_2025_form2_instructions.pdf`, PDF pages 45-46): "This amount includes income that is both taxable and nontaxable to you, as well as the taxable and nontaxable income of each member of your household." Line 4: "Enter all IRA distributions, both taxable and nontaxable ... includes qualified charitable distributions ... and conversions from a traditional IRA to a Roth IRA. However, do not include any nontaxable rollovers." Line 5: "Enter all taxable and nontaxable pensions and annuities, including Tier II Railroad Retirement benefits ... However, do not include any nontaxable rollovers and your cost or net investment." Line 7: "Do not adjust the capital gain for any federal exclusions, such as the gain from the sale of a primary residence and do not include any capital losses." Line 8: "Combine all the refundable credits received by all household members in 2025." Line 9: "Enter the total of all alimony received during the year." Line 17: "Report the combined taxable and nontaxable items of income listed above for all other members of the household."

### Differences, row by row
1. **Alimony after 2018 (CONFIRMED, undercount).** Federal AGI holds only `taxable_alimony_income`, which is `alimony_income` when `divorce_year` is before 2019 (the default is 2010). For a later divorce the alimony is in neither AGI nor the list. The statute names "(iii) alimony" as nontaxable income to add, and line 9 takes all of it.
2. **Tax-exempt 401(k), 403(b) and SEP distributions (CONFIRMED, undercount).** `tax_exempt_401k_distributions`, `tax_exempt_403b_distributions` and `tax_exempt_sep_distributions` are inputs; only `tax_exempt_ira_distributions` and `tax_exempt_pension_income` are in the list. (9)(a)(i) counts "the amount of any pension or annuity" and ARM (2)(d) "all federal taxable and nontaxable pension, annuity, and IRA payments". The countable amount is net of the taxpayer's cost ((9)(b); line 5), which PolicyEngine can't separate.
3. **Federal exclusions modeled as above-the-line deductions (CONFIRMED, undercount, small).** `us_bonds_for_higher_ed` (IRC 135) and `qualified_adoption_assistance_expense` (IRC 137) reduce `adjusted_gross_income_person`, and nothing restores them. (9)(a)(vii) counts interest on federal bonds whether taxed or not. The case "Parent-owned exclusions recorded on a dependent are not deducted twice" in `mt_elderly_homeowner_or_renter_credit_dependent_deductions.yaml` expects 18,800 for a 20,000 pension with 500 + 700 of exclusions; the statute gives 20,000.
4. **Foreign earned income exclusion (CONFIRMED on the catch-all, rare).** `foreign_earned_income_exclusion` is outside the other income inputs and outside the list.
5. **Railroad retirement (COVERED, #10722).** `railroad_benefits` is an input on main that neither federal gross income nor this list reads. #10722 adds `tax_exempt_railroad_pension_benefits` to the list and the untaxed tier 1 equivalent benefit to the formula.
6. **Gambling winnings (COVERED, #10070).** `gambling_winnings` isn't in federal gross income, so it isn't in this definition. #10070 adds it federally.
7. **What #10331 left.** The timing rule is right: receipts count in the year received. Every receipt other than the 2020 and 2021 recovery rebate credits is an input that defaults to 0 (other federal credits, Montana credits, this credit, the property tax rebate), so a household run without those inputs, and any microsimulation, counts none. The 2021 advance child tax credit isn't computed. The CAA payment is counted in 2020, though its advance could run to 1/15/2021.
8. **Not modelable.** Capital gains excluded from AGI ((9)(a)(ii); line 7); qualified charitable distributions and IRA health funding distributions (ARM (2)(e); line 4); Social Security paid directly to a nursing home ((9)(a)(viii)); income only "while they are members of the household". `tax_exempt_pension_income` is counted in full, and it has no documentation or cost split, so any part that is cost recovery or a rollover is overcounted against (9)(b) and line 5.

### Two readings
- **Above-the-line deductions.** The statute starts from federal AGI, so the IRA deduction, self-employment tax deduction and the like reduce income; PolicyEngine follows it. The 2025 Schedule 2EC sums gross lines 1 to 17 and has no adjustments line, which gives a higher figure. The statute-first rule keeps PolicyEngine's reading.
- **Basis in nontaxable IRA distributions.** (9)(b) reduces income by the taxpayer's basis. ARM (2)(d) and line 4 count all IRA payments but rollovers, while line 5 (pensions) does take out cost. PolicyEngine counts `tax_exempt_ira_distributions` in full, the agency reading. No basis input exists.
- **Federal refundable credits before 11/10/2017.** Old ARM 42.4.301(2)(b) (`mt_arm_42-4-301_2004-2017.html`): "federal refunds received during the tax year to the extent that the amount recovered reduced the claimant's Montana income tax in a prior year". Reading A counts refundable credits as nontaxable income from 2009; reading B, which main follows, counts them only from the 2017 amendment. #10331 recorded this as an open source-conflict candidate.
- **Gifts, life insurance proceeds, scholarships, other survivor benefits, paid leave benefits.** Inputs exist (`financial_assistance`, `life_insurance_benefits`, `educational_assistance`, `survivor_benefits`, `pfml_benefits`) and none is counted. The catch-all "all nontaxable income, including but not limited to" may reach them; the schedule names none. A survivor annuity is the likeliest real gap.

### Open PRs checked
#10722 (railroad benefits; edits this list and formula), #10070 (gambling winnings in federal gross income), #10727 (taxable strike benefits into federal gross income; edits this list), #10175 (unemployment exclusion; edits only the add-back's test), #10696 (railroad taxation), #9894 (dependents' capital income; no elderly-credit file). None touches alimony, the 401(k)/403(b)/SEP amounts, the IRC 135/137 exclusions or the foreign earned income exclusion.

### Not verified
- The 2016-2024 instructions cited in the parameter file were not re-read; only the 2025 instructions, the current and 2004-2017 ARM text, and MCA 15-30-2337, 2338, 2340 and 2341 were read.
- The 2025 Schedule 2EC form itself (as opposed to its instructions) was not opened.

### Tests
`tests-B/mt_elderly_credit_gross_household_income.yaml`: four cases (alimony, tax-exempt employer-plan distributions, savings bond interest, foreign earned income exclusion).

## 2. North Dakota: renter's refund income

### What PolicyEngine does
- **Files.** `parameters/gov/states/nd/tax/property/renters_refund/income_sources.yaml`; `variables/gov/states/nd/tax/property/renters_refund/nd_renters_refund_income.py`.
- **List (2025 onward).** `market_income`, `social_security`, `total_unemployment_compensation`, `general_assistance`.
- **`market_income` components.** `employment_income` (gross wages, before pre-tax deductions), `self_employment_income`, `sstb_self_employment_income`, `partnership_s_corp_income`, `pension_income`, `dividend_income`, `interest_income`, `gi_cash_assistance`, `capital_gains`, `non_sch_d_capital_gains`, `other_net_gain_person`, `rental_income`, `farm_rent_income`, `estate_income`, `illicit_income`, `farm_operations_income`, `miscellaneous_income`, `alimony_income`, `strike_benefits`, `retirement_distributions`, `military_retirement_income`, `disability_benefits`, `ak_permanent_fund_dividend`. Totals, so tax-exempt interest, pensions and retirement distributions are inside.
- **Formula.** Sum of the list over the tax unit, less `pre_tax_health_insurance_premiums`, less the tax-exempt part of disability benefits, less `itemized_medical_expenses` plus `itemized_medical_expenses_applied_exclusion`, floored at zero.
- **Entity.** Tax unit: head, spouse and dependents.
- **Loss floors.** None. Negative business, rental and capital amounts reduce income without limit.
- **Readers.** `nd_renters_refund` (20% of rent less 4% of income, $5 to $600) and `nd_renters_refund_eligible` ($70,000 limit).

### What the law says
- **N.D.C.C. 57-02-08.1(5)(c)** (`nd_ndcc_t57c02.pdf`, PDF page 16): "'Income' means income for the most recent complete taxable year from all sources, including the income of any dependent of the applicant, and including any county, state, or federal public assistance benefits, social security, or other retirement benefits, but excluding any federal rent subsidy, any amount excluded from income by federal or state law with the exception of income from social security benefits, and medical expenses paid during the year by the applicant or the applicant's dependent which is not compensated by insurance or other means."
- **Tax Commissioner guideline** (`nd_homestead_renters_guideline.pdf`, PDF page 2, content revised 7-2025). Item 10: "Income includes but is not limited to: Social security benefits. Pensions, including military pension and I.R.A. Salaries and wages. Dividends and Interest. Net gains from the sale of property. Net rental income. Net profit from any business, including farming and ranching. Unemployment compensation benefits. Alimony." Item 11: "Items which are not income ... Life insurance proceeds. Money received from gifts or inheritance. Social security lump sum death payments. Workers compensation payments, including survivor benefits. ... Child support. Federal fuel assistance. Renters refund. Food stamps. VA disability. TANF (Temporary Assistance for Needy Families)." Item 37 (page 7): "A renter must meet the same income requirements as a homeowner."
- **Renter's refund application, SFN 24777 (10-2025)** (`nd_renters_refund_application_sfn24777.pdf`, page 1): line 4 "Applicant's and spouse's income from Social Security benefits (exclude Medicare)"; line 7 "income from other sources (S.S.I., net rental income, net income from business, capital gains, unemployment compensation, etc.)"; line 8 "Dependent's income from all sources". Page 2: "Life insurance death proceeds, Workers' Compensation, and Veterans' Disability are not included as income."
- **Homestead credit application, SFN 24757 (10-2025)** (`nd_2026_homestead_credit_application.pdf`, page 1), same statutory definition: "b. Income from wages, salary, etc. (From Form 1040 or 1040-SR, line 1z)"; "c. Income from taxable interest and dividend income (... lines 2b and 3b)"; "d. Income from IRAs, pensions, and annuities (... lines 4b and 5b)"; "e. Capital gains and losses (... line 7)"; "f. Income from all other sources (... Schedule 1, line 10)". Page 2 lists "2. SSI benefits" and "10. Net profit or loss from any business, including farming and ranching."

### Differences, row by row
1. **Gambling winnings (CONFIRMED, undercount).** `gambling_winnings` is an input that `market_income` doesn't include. Income is "from all sources" and nothing excludes winnings; the homestead application's line 4f takes Schedule 1 line 10, which holds them. #10070 adds winnings to federal gross income only, so this definition stays short after it merges.
2. **Capital losses (CONFIRMED against both agency sources, undercount).** `capital_gains` enters without a floor or limit, so a $20,000 net loss takes $20,000 off income. The statute doesn't mention losses. The homestead application takes Form 1040 line 7, where a loss stops at $3,000; the guideline lists only "Net gains from the sale of property". Neither open ND PR changes this.
3. **Federally excluded parts of market income (COVERED, #10697).** Main counts tax-exempt interest, nontaxable pensions and retirement distributions, and wages before 401(k), 403(b) and HSA payroll deferrals. The statute excludes "any amount excluded from income by federal or state law", and the homestead application takes the taxable Form 1040 lines. #10697 also subtracts the IRC 135, 137, 931 and 933 exclusions the model deducts above the line.
4. **SSI (COVERED, #10724).** Main leaves it out; the application's line 7 names "S.S.I."
5. **Railroad retirement (COVERED, #10722).** Tier 1 equivalent benefit and the taxable part of the annuity.
6. **Medicare premiums.** The application nets the premium out of Social Security and tells the applicant not to claim it again as a medical expense. PolicyEngine counts the gross benefit and subtracts the modeled Part B premium as a medical expense. Same result; no finding.

### Two readings
- **TANF.** The statute counts "any county, state, or federal public assistance benefits"; guideline item 11 says TANF is not income. Main follows the guideline; #10724 follows the statute and logs a source-conflict candidate.
- **Alimony after 2018.** Guideline item 10 counts "Alimony" without limit (main). #10697 reads the statute's exclusion clause to remove alimony that federal law leaves out of the recipient's income.
- **"Excluded ... by state law".** North Dakota's income tax reduces taxable income by retired military pay, U.S. obligation interest and part of long-term gains (N.D.C.C. 57-38-30.3(2), cited from #10697's body; not opened here). If those are exclusions, they leave refund income; the guideline keeps "Pensions, including military pension" and "Net gains", and PolicyEngine follows it. #10697 logs this as a candidate.
- **`survivor_benefits`.** Case 3 of `nd_renters_refund_income.yaml` pins it as not income. The guideline excludes workers' compensation survivor benefits and life insurance; a taxable survivor annuity is "other retirement benefits". The input doesn't say which it holds.

### Open PRs checked
#10697 (federally excluded income; rewrites the formula), #10724 (SSI and TANF; stacked on #10697), #10722 (railroad benefits), #10070 (gambling winnings federally; doesn't touch `market_income`), #10764 (railroad benefits in benefit programs; no renter's refund file).

### Not verified
- N.D.C.C. 57-38-30.3(2) (state income tax reductions) was not opened.
- The May 2013 guideline edition that #10724 says counted TANF was not opened.
- Rent-side rules (landlord-paid utilities, federal rent subsidy in rent) are outside this audit.

### Tests
`tests-B/nd_renters_refund_income.yaml`: two cases (gambling winnings; capital loss limited to $3,000).

## 3. New Mexico: modified gross income

### What PolicyEngine does
- **Files.** `parameters/gov/states/nm/tax/income/modified_gross_income.yaml`; `variables/gov/states/nm/tax/income/nm_modified_gross_income.py`.
- **List (2021 onward).** `tax_unit_social_security`, `capital_gains`, `tanf`, `ssi`, `interest_income`, `dividend_income`, `alimony_income`, `child_support_received`, `rental_income`, `pension_income`, `retirement_distributions`, `total_unemployment_compensation`, `irs_employment_income`, `self_employment_income`, `sstb_self_employment_income`, `veterans_benefits`, `estate_income`. The file ends with a comment, "income such as gambling winnings, insurance settlements, scholarships, grants and inheritance,", and no entry under it.
- **Formula.** For each source, the tax unit's sum floored at zero, then added.
- **Entity.** Tax unit: head, spouse and dependents.
- **Loss floors.** One floor per source for the whole tax unit, so a loss can't reduce a different source, but it does reduce the same source on another person, and short-term and long-term gains net inside `capital_gains`.
- **Readers.** `nm_low_income_comprehensive_tax_rebate`, `nm_property_tax_rebate` and `nm_property_tax_rebate_eligible`, `nm_cdcc_eligible`.
- **Open PRs.** #10769 adds `military_retirement_income`; #10722 adds the three railroad benefit parts.

### What the law says
- **NMSA 1978 7-2-2(L)** (2025 text, `nm_nmsa_7-2-2_justia.html`): "'modified gross income' means all income of the taxpayer and, if any, the taxpayer's spouse and dependents, undiminished by losses and from whatever source, including: (1) compensation; (2) net profit from business; (3) gains from dealings in property; (4) interest; (5) net rents; (6) royalties; (7) dividends; (8) alimony and separate maintenance payments; (9) annuities; (10) income from life insurance and endowment contracts; (11) pensions; (12) discharge of indebtedness; (13) distributive share of partnership income; (14) income in respect of a decedent; (15) income from an interest in an estate or a trust; (16) social security benefits; (17) unemployment compensation benefits; (18) workers' compensation benefits; (19) public assistance and welfare benefits; (20) cost-of-living allowances; and (21) gifts".
- **7-2-2(M)**: it "excludes: (1) payments for hospital, dental, medical or drug expenses to or on behalf of the taxpayer; (2) the value of room and board provided ... based upon financial need ...; (3) payments pursuant to a federal, state or local government program directly or indirectly to a third party ...; or (4) payments for credits and rebates pursuant to the Income Tax Act and made for a credit pursuant to Section 7-3-9 NMSA 1978".
- **3.3.1.10 NMAC** (`nm_nmac_3-3-1-10_cornell.html`). (A)(1)(a): Social Security "including any amount deducted for part B coverage". (A)(1)(d): public assistance "means unrestricted cash payments made under the supplemental security income program, the aid to families with dependent children program, general assistance or similar programs", not housing subsidies. (A)(2): "Scholarships, grants, fellowships or similar payments ... which do not have to be repaid are modified gross income." (B): "zero is the lowest amount which may be reported for any item ... The loss from one business or activity shall not reduce the income from another business or activity." (C): "'Sick pay', payments received for damages for personal injury or illness and disability payments from whatever source are 'modified gross income'." (D): settlements and judgments count.
- **2025 PIT-RC instructions** (`C:/tmp/irs27/nm_pitrc_2025.pdf`, PDF pages 2 and 4; shifted text layer, so spaces are restored and digits are missing). Page 4: "In general modified gross income is all income and other compensation you receive from all sources regardless of whether that income is taxable by the US Government or the State of New Mexico for you your spouse and your dependents"; "Enter your unemployment benefits from all sources and any workers' compensation benefits you received"; "Enter your net profit from business farm or rentals ... you may not offset the loss of one business farm or rental against the profit of another business farm or rental or against any other source of income"; "Enter your gross capital gains Do not reduce them by capital losses"; "Enter all gifts of cash or marketable tangible items no matter who gave them to you"; and the other-income list, which names interest on government obligations, dividends, "Gross gambling gaming and lottery winnings from any source without reducing winnings by any losses", insurance or court settlements, scholarships, VA benefits, estate or trust income, alimony and child support, deferred compensation withdrawals, royalties, discharge of indebtedness, inheritances, pass-through distributions and "All ordinary gains from dealing in or selling property".

### Differences, item by item (statute numbering)
| Item | PolicyEngine | Result |
|---|---|---|
| (1) compensation | `irs_employment_income` | Match. `foreign_earned_income_exclusion` is not added back (CONFIRMED, rare) |
| (2) net profit from business | `self_employment_income`, `sstb_self_employment_income` | Non-farm: match. Farm (`farm_operations_income`): missing, CONFIRMED |
| (3) gains from dealings in property | `capital_gains` | Net gain: match. Short-term loss against long-term gain: CONFIRMED. `non_sch_d_capital_gains`, Form 4797 gains: missing, CONFIRMED. Excluded home-sale gain: no input |
| (4) interest | `interest_income` | Match |
| (5) net rents, (6) royalties | `rental_income` | Match; `farm_rent_income` missing (with farm) |
| (7) dividends | `dividend_income` | Match |
| (8) alimony | `alimony_income` (and `child_support_received`) | Match |
| (9) annuities, (11) pensions | `pension_income`, `retirement_distributions` | Match; military retired pay COVERED by #10769; railroad COVERED by #10722 |
| (10) life insurance and endowment contracts | inside `pension_income` by its documentation | Death proceeds (`life_insurance_benefits`): TWO-READINGS |
| (12) discharge of indebtedness | none | `debt_relief` missing, CONFIRMED |
| (13) partnership income | none | `partnership_s_corp_income` missing, CONFIRMED |
| (14) income in respect of a decedent | none | No input |
| (15) estate or trust | `estate_income` | Match |
| (16) social security | `tax_unit_social_security` | Match |
| (17) unemployment | `total_unemployment_compensation` | Match |
| (18) workers' compensation | none | `workers_compensation` missing, CONFIRMED |
| (19) public assistance | `ssi`, `tanf` | `general_assistance` and `nm_ssi_state_supplement` missing, CONFIRMED |
| (20) cost-of-living allowances | none | No input |
| (21) gifts | none | `financial_assistance` missing, CONFIRMED |
| Regulation (A)(2) scholarships and grants | none | `educational_assistance`, `pell_grant` missing, CONFIRMED |
| Regulation (C) sick pay and disability | none | `disability_benefits` missing, CONFIRMED |
| Instructions: gambling winnings | none | `gambling_winnings` missing, CONFIRMED |
| Catch-all "from whatever source" | none | `miscellaneous_income`, `strike_benefits`, `survivor_benefits`, `gi_cash_assistance` missing, CONFIRMED |
| Regulation (B) losses | per-source floor on the tax unit sum | Cross-person netting within a source: CONFIRMED |

### Two readings
- **Life insurance death proceeds.** 3.3.1.10(A)(1)(j) defines item (10) by IRC 72 (annuity-type amounts), which death proceeds are not. The instructions count "Insurance or court settlements", and the statute counts income "from whatever source". PolicyEngine counts none of `life_insurance_benefits`.
- **Household members.** The instructions say to include "the taxpayer and all household members"; the statute says taxpayer, spouse and dependents. PolicyEngine follows the statute. No finding.

### Not modelable
Gain on a home sale that federal law excludes; inheritances and income in respect of a decedent; insurance and court settlements; cost-of-living allowances; room and board received as compensation; gifts of marketable goods; and the rule that spouses filing separately each report both spouses' income (two tax units in PolicyEngine).

### Open PRs and issues checked
#10769 (military retired pay), #10722 (railroad), #10070 (gambling winnings in federal gross income; this list doesn't read federal gross income), #10696, #10146. Open issue #10062 names the partnership and farm gap; no PR is linked.

### Not verified
- PIT-RC line numbers: digits are missing from the text layer, so lines 4 to 12 are inferred from their order and from the references already in the parameter file.
- The nmonesource.com statute page (JavaScript) was not opened; the 2025 Justia copy was read.

### Tests
`tests-B/nm_modified_gross_income.yaml`: 14 cases, one per confirmed gap.

## 4. Oklahoma: gross household income

### What PolicyEngine does
- **Files.** `parameters/gov/states/ok/tax/income/credits/gross_income_sources.yaml`; `variables/gov/states/ok/tax/income/credits/ok_gross_income.py`.
- **List (2021 onward).** `irs_employment_income`, `self_employment_income`, `sstb_self_employment_income`, `partnership_s_corp_income`, `farm_operations_income`, `farm_rent_income`, `short_term_capital_gains`, `long_term_capital_gains`, `interest_income`, `rental_income`, `estate_income`, `dividend_income`, `pension_income`, `debt_relief`, `total_unemployment_compensation`, `workers_compensation`, `social_security`, `alimony_income`, `child_support_received`, `illicit_income`, `miscellaneous_income`, `ssi`, `ok_ssp`, `general_assistance`, `eitc`.
- **Formula.** Short- and long-term capital gains are added and floored at zero; every other source is summed over the tax unit and floored at zero.
- **Entity.** Tax unit. The law counts everyone in the household (see the first difference).
- **Readers.** `ok_stc` ($20,000 and $50,000 limits) and `ok_ptc` ($12,000 limit and the 1% offset).
- **Open PRs.** #10769 adds `military_retirement_income`; #10722 adds the three railroad benefit parts.

### What the law says
- **68 O.S. 5012** (sales tax relief; `ok_68os_5012.html`) and **68 O.S. 2904(3)** (property tax relief; `ok_68os_2904.html`), same words: "'gross household income' means the gross amount of income of every type, regardless of the source, received by all persons occupying the same household, whether such income was taxable or nontaxable for federal or state income tax purposes, including pensions, annuities, federal social security, unemployment payments, veterans' disability compensation, public assistance payments, alimony, support money, workers' compensation, loss-of-time insurance payments, capital gains and any other type of income received; and excluding gifts."
- **OAC 710:50-15-96(c)** (`ok_oac_710-50-15-96_cornell.html`): "'Gross Household Income' is the gross income of every type received by all persons occupying the same household. ... It is not relevant whether or not the income is taxable for state or federal income tax purposes. 'Gross Household Income' does not include gifts, or income that is considered deferred."
- **2025 Form 538-S** (`C:/tmp/irs27/ok511pkt.pdf`, PDF pages 50-52). Part 3: "Enter taxable and nontaxable gross income and assistance received by ALL members of your household in the year 2025." Lines: 1 wages "(including nontaxable income from your W-2s)"; 2 interest and dividends; 3 dependents' income; 4 "Social Security payments (total including Medicare)"; 5 Railroad Retirement; 6 "Other pensions, annuities, and Individual Retirement Accounts (IRAs)"; 7 alimony; 8 unemployment; 9 "Earned Income Credit (EIC) received in 2025 (if applicable, combine federal and Oklahoma amounts)"; 10 nontaxable sources; 11 "gross (positive) income from rentals, royalties, partnerships, estates, trusts, and gains from the sale or exchange of property (taxable & nontaxable)"; 12 "gross (positive) income from business and farm"; 13 "Other income, including income of others living in your household". Page 3 definition: gross household income "includes, but is not limited to, public assistance payments, support money (example: Child support), workers' compensation, school grants or scholarships, veterans disability compensation, loss-of-time insurance payments ... Income that is exempt must be included in the year received, for example: Nontaxable sources of income on your W-2 (such as a dependent care reimbursement account), military housing assistance, and the distribution of earnings from a Roth IRA. Note: Do not include income deferred for federal income tax purposes, for example: Tax deductible contributions to a 401K or to a traditional IRA."
- **2025 Form 538-H** (`ok_538h_2025.pdf`, pages 1 and 3): same lines; line 10 examples "Veterans disability payments, workers' compensation, loss of time insurance, support money and public assistance (housing assistance, cash, etc.)"; page 3 adds "school grants or scholarships" and "If self-employed, enter the gross income from business".
- **68 O.S. 5011(C), 2905-2907** (`ok_68os_5011.html`, `ok_68os_2905.html` to `2907`): the $20,000 / $50,000 and $12,000 limits, and the credit of taxes above 1% of household income up to $200.

### Differences, row by row
1. **Whose income (CONFIRMED, undercount).** The statute, the rule and both forms count every person living in the household. `ok_gross_income` sums the tax unit, so an adult child, parent, partner or roommate on another return is left out. Montana's elderly credit sums the same kind of amount over `person.household`.
2. **Retirement account distributions (CONFIRMED, undercount).** `retirement_distributions` is missing; only `pension_income` is listed. Line 6 names IRAs, and deferred income "will be included when distributed". For a Roth account the form counts the distribution of earnings.
3. **Veterans' disability compensation (CONFIRMED, undercount).** Named in the statute; `veterans_benefits` is not in the list.
4. **Loss-of-time insurance and disability benefits (CONFIRMED, undercount).** Named in the statute; `disability_benefits` is not in the list.
5. **TANF (CONFIRMED, narrow).** "Public assistance payments" count; `tanf` is missing while `ssi`, `ok_ssp` and `general_assistance` are listed. TANF recipients can't claim the sales tax credit, so this reaches the property tax credit and people who live with a TANF family.
6. **Nontaxable W-2 income (CONFIRMED for dependent care benefits).** `irs_employment_income` removes `dependent_care_employer_benefits`, pre-tax health premiums and HSA payroll contributions along with the 401(k)/403(b) deferrals. The form keeps deferrals out but includes nontaxable W-2 income and names a dependent care account.
7. **School grants and scholarships (CONFIRMED on the agency's reading).** Both forms name them; `educational_assistance` and `pell_grant` are not counted.
8. **Gambling winnings and other inputs (CONFIRMED for gambling).** `gambling_winnings`, `strike_benefits`, `survivor_benefits` and `gi_cash_assistance` are not in the list.
9. **Foreign earned income exclusion (CONFIRMED, rare).**
10. **Earned income credit (TIMING).** Line 9 counts the credit "received in 2025", federal and Oklahoma combined. That is the 2024 credit. `eitc` in the list is the 2025 credit, paid in 2026, and the Oklahoma credit isn't counted. This is the same rule #10331 fixed for Montana. "OK gross income unit test 1" pins the current-year amount.
11. **Military retired pay (COVERED, #10769); railroad retirement (COVERED, #10722).**

### Two readings
- **Capital losses.** PolicyEngine nets short- and long-term amounts and floors the result, and the case "OK gross income nets capital gains before applying positive-only rule" pins it. The statute's "gross amount of income of every type" and line 11's "gross (positive) income from ... gains" can be read to count each gain with no loss offset. The form only bars a negative line. Capital gain distributions are missing under either reading.
- **Business income.** Line 12 asks for "gross (positive) income from business and farm"; the 538-H instructions say "enter the gross income from business". PolicyEngine uses positive net profit. Gross income before expenses has no input.
- **In-kind aid.** Form 538-H lists "public assistance (housing assistance, cash, etc.)". The statute says "public assistance payments". Neither names SNAP. PolicyEngine counts no in-kind aid.

### Open PRs and issues checked
#10769 (military retired pay), #10722 (railroad; edits this list), #10070 (gambling winnings federally; this list doesn't read federal gross income), #10043 (edits `ok_stc.py` for claimable filers, not the income list), #10696. No open PR or issue touches the household entity, retirement distributions, veterans' benefits or the credit timing.

### Not verified
- 68 O.S. 2908-2911 were downloaded and not read past their titles (filing, proration, audit and direct payment rules).
- The oscn.net copies were not opened; the 2025 Justia copies were read.
- Whether the Tax Commission counts gross receipts or net profit for the self-employed in practice.

### Tests
`tests-B/ok_gross_income.yaml`: ten cases. Case 9 (credit timing) assumes the fix adds a receipt input that defaults to zero.

## 5. Missouri: property tax credit income

### What PolicyEngine does
- **Files.** `variables/gov/states/mo/tax/income/credits/property_tax/mo_ptc_gross_income.py`, `mo_ptc_income_offset.py`, `mo_ptc_net_income.py`, `mo_ptc_income_limit.py`; `parameters/gov/states/mo/tax/income/credits/property_tax/public_assistance_types.yaml`, `income_offset/*.yaml`, `upper_income_limit/*.yaml`.
- **Gross income (no source list; the formula follows Form MO-PTS).** Tax unit sum of `mo_adjusted_gross_income`, `tax_exempt_pension_income` and `tax_exempt_interest_income`; plus `tax_exempt_social_security`; plus `veterans_benefits` of anyone who isn't `is_fully_disabled_service_connected_veteran`; plus the public assistance list (`ssi`, `child_support_received`, `tanf_person`); plus `limited_capital_loss`.
- **Missouri AGI.** `irs_gross_income` less above-the-line deductions, plus `mo_additions`, less `mo_agi_subtractions`: `mo_qualified_health_insurance_premiums`, `mo_capital_gains_subtraction_person` (from 2025), `us_govt_interest_person`, `mo_529_deduction`, `salt_refund_income`, `military_retirement_pay`, `mo_other_subtractions`. Floored at zero per person.
- **Net income.** Gross less the offset: $0 unless filing jointly; joint renters $2,000 and joint owners $4,000 through 2025, $2,800 and $5,800 from 2026.
- **Limits.** $27,500, or $30,000 for a full-year owner, through 2025; from 2026 $38,200 / $42,200 single and $41,000 / $48,000 married.
- **Entity.** Tax unit. Dependents' Social Security, veterans' benefits and public assistance are in; their Missouri AGI is zero.
- **Loss floors.** Federal sources are floored in `irs_gross_income`; business, rental, estate and capital losses come back out through `loss_ald`. Only `limited_capital_loss` is added back here.
- **Readers.** `mo_property_tax_credit`, `mo_ptc_taxunit_eligible`.

### What the law says
- **RSMo 135.010(5)** (effective 8/28/2025; `mo_rsmo_135.010.html`): "'Income', Missouri adjusted gross income as defined in section 143.121 less two thousand dollars for all calendar years ending on or before December 31, 2025, or in the case of a homestead owned and occupied, for the entire year, by the claimant, less four thousand dollars as an exemption for the claimant's spouse residing at the same address ... or for all calendar years beginning on or after January 1, 2026, less two thousand eight hundred dollars, or ... less five thousand eight hundred dollars ...; and increased, where necessary, to reflect the following: (a) Social Security, railroad retirement, and veterans payments and benefits unless the claimant is a one hundred percent service-connected, disabled veteran or a spouse of a one hundred percent service-connected, disabled veteran. ... (b) The total amount of all other public and private pensions and annuities; (c) Public relief, public assistance, and unemployment benefits received in cash, other than benefits received under this chapter; (d) No deduction being allowed for losses not incurred in a trade or business; (e) Interest on the obligations of the United States, any state, or any of their subdivisions and instrumentalities".
- **RSMo 143.121** (effective 8/28/2025; `mo_rsmo_143.121.html`). Subsection 3 subtracts from federal AGI "(1) ... interest or dividends on obligations of the United States", "(12) One hundred percent of any retirement benefits received by any taxpayer as a result of the taxpayer's service in the Armed Forces of the United States", and "(14) (a) For all tax years beginning on or after January 1, 2025, one hundred percent of all income reported as a capital gain for federal income tax purposes by an individual". Subsection 7(2) subtracts qualified health insurance premiums.
- **RSMo 135.030.1(1)** (`mo_rsmo_135.030.html`): maximum upper limit $27,500, or $30,000 for a homestead owned and occupied all year, through 2025; the four 2026 limits listed above.
- **2025 Form MO-PTS** (`mo_pts_2025.pdf`, pages 1-2). Line 1 "income from Form MO-1040, Line 6"; line 2 "nontaxable social security benefits received by you, your spouse, and your minor children before any deductions and the amount of social security equivalent railroad retirement benefits"; line 3 "the total amount of pensions, annuities, dividends, rental income, unemployment compensation, or interest income not included in Line 1. Include tax exempt interest from MO-A, Part 1, Line 8"; line 4 railroad retirement; line 5 veterans payments; line 6 "public assistance, Supplemental Security Income (SSI), child support, or Temporary Assistance payments (TA and TANF)"; line 7 "nonbusiness loss(es) ... (Include capital loss from Federal Form 1040 or 1040-SR)"; line 9 the $0 / $2,000 / $4,000 options; line 10 limits printed as $27,200 and $30,000.
- **2025 MO-1040 instructions, Form MO-PTS** (`mo_1040_instructions_2025.pdf`, PDF page 18). Line 3: "(Do not include amount of excludable costs of pensions or annuities.) ... Form(s) 1099-R - Total amount before deduction not included on Form MO-1040, Line 6 (Missouri adjusted gross income)." Line 7: "A nonbusiness loss is a loss of income that did not result from a trade or business. (Losses from Federal Form 1040 or 1040-SR, Schedule F and Schedule C are considered business losses and should not be included here.)" and "An individual taxpayer cannot have a negative federal adjusted gross income (FAGI) for purposes of computing Missouri adjusted gross income".
- **2025 MO-PTC instructions** (`mo_ptc_instructions_2025.pdf`, PDF pages 4-6): "Household income is all income received by a claimant, spouse, and minor children (taxable or nontaxable)"; line 5 "Do not include the value of commodity foods, food stamps, or heating and cooling assistance."

### Differences, row by row
1. **Military retirement benefits (CONFIRMED, undercount).** Missouri AGI subtracts all of `military_retirement_pay`. The credit's income adds back "the total amount of all other public and private pensions", and line 3 takes pensions "not included in Line 1". `mo_ptc_gross_income` adds only `tax_exempt_pension_income`, so the retired pay is gone. A retiree with $20,000 of military retired pay and a $15,000 pension shows $15,000, not $35,000. #10769 fixes the same omission for New Mexico and Oklahoma; no PR covers Missouri.
2. **Interest on U.S. obligations (CONFIRMED, undercount).** `us_govt_interest_person` is subtracted in Missouri AGI. 135.010(5)(e) adds interest on obligations of the United States, and line 3 says to include the exempt interest from MO-A line 8. Only `tax_exempt_interest_income` (state and municipal interest) is added.
3. **General assistance and the state supplement (CONFIRMED, undercount).** The list has `ssi`, `child_support_received` and `tanf_person`. `general_assistance` and `mo_ssp` are missing; the file still has a commented-out `mo_state_supplement` line from before `mo_ssp` existed.
4. **Nonbusiness losses other than capital losses (CONFIRMED on the agency reading, undercount).** A rental, estate or other Schedule E loss reduces federal AGI through `limited_business_loss` and isn't added back. The instructions count only Schedule C and F losses as business losses.
5. **Tax-exempt retirement account distributions (CONFIRMED on the agency reading, undercount).** `tax_exempt_retirement_distributions` is not added. The instructions take every Form 1099-R amount outside Missouri AGI, less excludable cost.
6. **Spouse of a 100% disabled veteran (CONFIRMED, overcount, rare).** The statute exempts the veteran and the veteran's spouse. PolicyEngine applies the exclusion person by person, so the spouse's own veterans' benefits still count.
7. **Railroad retirement (COVERED, #10722).**
8. **Capital gains from 2025.** They leave Missouri AGI under 143.121.3(14)(a), and 135.010(5) has no add-back for gains, so they leave credit income too. PolicyEngine does the same. Not a finding, but a large change in who qualifies.
9. **Limits.** The 2025 forms print $27,200 for renters; the statute says $27,500 and PolicyEngine uses it. A renter's credit in that last band is zero either way.

### Two readings
- **Child support.** Forms MO-PTS (line 6) and MO-PTC (line 5) count it with public assistance, and PolicyEngine follows them. The statute's income is Missouri AGI plus items (a) to (e), and child support is in neither. The statute-first rule points to leaving it out.
- **Pension cost recovery.** The statute says "the total amount of all other public and private pensions and annuities"; the instructions say not to include excludable cost. PolicyEngine adds all of `tax_exempt_pension_income`. No cost input exists.
- **Alimony after 2018.** It is outside Missouri AGI and the statute's list; PolicyEngine leaves it out. The MO-PTC instructions (for claimants who don't file a return) list "alimony" and call household income all income "taxable or nontaxable".

### Open PRs and issues checked
#10722 (railroad; edits `mo_ptc_gross_income.py`), #10769 (military retired pay for NM and OK only), #10768 (VA rating flag; no property tax credit file), #10015 (Missouri AGI split between spouses; edits `mo_adjusted_gross_income.py`), #10696 (railroad taxation; edits `agi_subtractions.yaml`), #10647. No open PR or issue covers the military, U.S. interest, general assistance or loss findings.

### Not verified
- The instruction that a veteran under 100% who can't work because of service-connected impairments also leaves out benefits, and the surviving-spouse rule, are agency additions that PolicyEngine doesn't model; they were read but not compared against any regulation.
- 12 CSR rules for the credit were not opened.
- The order of the zero floor in Missouri AGI (before or after modifications) differs from the instructions only for filers with negative federal AGI and Missouri additions; it belongs to the Missouri AGI variable.

### Tests
`tests-B/mo_ptc_gross_income.yaml`: six cases.
