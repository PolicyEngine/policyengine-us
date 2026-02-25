# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.586.2] - 2026-02-25 19:58:01

### Added

- Added boundary tests for Montana CTC eligibility and reduction thresholds.

### Fixed

- Montana CTC now requires federal CTC eligibility per HB 268 Section 1(1).
- Fixed parameter metadata typos in Montana CTC income limit files.

## [1.586.1] - 2026-02-25 16:09:12

### Fixed

- Split baseline (excl states) CI batch into memory-aware sub-batches to prevent OOM kills in NonStructural-Other job.

## [1.586.0] - 2026-02-24 19:55:56

### Added

- Connecticut HB-5009 expanded property tax credit reform

## [1.585.0] - 2026-02-24 17:42:10

### Added

- Added Python 3.14 support and dropped Python 3.10.

## [1.584.0] - 2026-02-24 14:42:50

### Added

- Connecticut SB-100 reduced income tax rates reform

## [1.583.0] - 2026-02-24 14:30:18

### Fixed

- Fix NY supplemental tax for filers with AGI above $25 million in 2022+.

## [1.582.1] - 2026-02-24 09:57:52

### Fixed

- Fix ACTC earned income to subtract half of SE tax for self-employed filers per IRC 24(d)(1)(B)(i) and 32(c)(2)(A)(ii).

## [1.582.0] - 2026-02-24 01:42:07

### Added

- Implement SECURE 2.0 enhanced 401(k) catch-up contributions for ages 60-63 (starting 2025).

## [1.581.2] - 2026-02-23 22:15:43

### Added

- Add tests for tax_unit_state, emp_self_emp_ratio, is_premium_free_part_a, and savers_credit_credit_limit variables

## [1.581.1] - 2026-02-23 21:02:29

### Changed

- Add pragma no cover to truly untestable code (microsim branches, behavioral responses, TAXSIM compatibility).

## [1.581.0] - 2026-02-23 20:47:20

### Added

- Implement Connecticut 2026 tax rebate proposal (Gov. Lamont).

## [1.580.0] - 2026-02-23 19:09:02

### Added

- Add Connecticut refundable child tax credit (HB 5134) as a reform.

## [1.579.0] - 2026-02-23 16:14:13

### Added

- Added non-age work registration exemptions for SNAP ABAWD (student, UI recipient, child under 6) per 7 U.S.C. 2015(o)(3)(D).
- Added is_snap_abawd_hr1_in_effect variable to centralize state-level HR1 adoption routing.

### Changed

- Refactored SNAP ABAWD work requirements to absorb California pre-HR1 delay logic, eliminating duplicate CA variable.
- Updated federal SNAP ABAWD parameter effective dates to 2025-07-04 per Public Law 119-21 enactment date.
- Backdated ABAWD age exemption parameters to 1997-03-01 (PRWORA effective date) and added FRA 2023 phase-in history (50→51→53→55).
- Removed blanket HI/AK ABAWD exemption from formula; both states are implementing ABAWD. Preferential waiver authority documented in parameter file.

## [1.578.1] - 2026-02-23 15:39:55

### Fixed

- Remove duplicate pr_gross_income.py that caused a VariableNameConflictError for pr_gross_income_person.

## [1.578.0] - 2026-02-23 13:53:18

### Added

- Add SNAP immigration status eligibility, reflecting changes from the One Big Beautiful Bill Act of 2025.
- Exclude immigration-ineligible members from SNAP unit size.
- Add California-specific delayed effective date (April 1, 2026) for SNAP immigration eligibility changes per ACL 25-92.

## [1.577.1] - 2026-02-23 13:51:33

### Fixed

- Implement NJ same-category loss rule (N.J.S. 54A:5-1) for gross income calculation. Losses in any income category (capital gains, S-corp/partnership, rental, self-employment) are now disregarded and cannot offset income from other categories.

## [1.577.0] - 2026-02-23 13:49:59

### Added

- Add Washington Apple Health for Kids and Apple Health Expansion programs.

## [1.576.0] - 2026-02-23 13:47:45

### Added

- Colorado alternative minimum tax (AMT).

## [1.575.0] - 2026-02-23 13:46:51

### Added

- Maryland county income tax rates for 2024 and 2025.

## [1.574.0] - 2026-02-23 13:45:06

### Added

- added 2018 CHIP pregnant income limit

## [1.573.0] - 2026-02-23 13:42:35

### Added

- Puerto Rico non-refundable child tax credit (CTC).

## [1.572.5] - 2026-02-23 06:32:41

### Fixed

- Fix WA Working Families Tax Credit phaseout to phase to $50 minimum instead of zero per RCW 82.08.0206(3)(f).

## [1.572.4] - 2026-02-23 06:19:36

### Fixed

- Fix Stay NJ benefit formula order of operations and add Senior Freeze offset per P.L. 2024 c.88.

## [1.572.3] - 2026-02-23 00:04:18

### Fixed

- Fix circular dependency in NY A06774 Enhanced CDCC reform by using cdcc_potential instead of cdcc, which avoids the income_tax_before_credits dependency cycle.

## [1.572.2] - 2026-02-22 23:59:28

### Fixed

- Cap DC self-employment loss addition at the amount actually deducted in federal AGI via loss_ald.

## [1.572.1] - 2026-02-20 22:56:55

### Fixed

- Hawaii child and dependent care credit (hi_cdcc) no longer goes negative when spouse has negative self-employment income.

## [1.572.0] - 2026-02-20 22:34:21

### Added

- Multnomah County Preschool for All (PFA) Personal Income Tax with progressive rates by filing status.

## [1.571.1] - 2026-02-20 21:53:15

### Added

- Add historical TANF parameter data for DE, MO, RI, SD (pre-2018 values).
- Add PA TANF Work Expense Reimbursement (WER) for 2009-2020 era.
- Add PA TANF work expense mechanism toggle (deduction_applies parameter).

## [1.571.0] - 2026-02-20 19:38:12

### Added

- Add 2024 SLCSP premiums by rating area for all states, scraped from the KFF 2024 subsidy calculator (age 0 benchmark).

## [1.570.7] - 2026-02-19 06:54:52

### Fixed

- Cap all state TANF benefit formulas to prevent negative countable income from inflating benefits above the payment standard. Fixes NC household size .sum() bug and adds min_() caps to 38 state programs (AL, AK, AR, AZ, CA, CO, CT, DC, FL, HI, IA, IL, IN, KS, LA, MA, MD, MI, MN, MO, MS, MT, NC, ND, NE, NH, NJ, NM, NV, NY, OH, OK, OR, PA, RI, SC, SD, TX, UT, VT, WV, WY). Previously, negative countable income could produce benefits exceeding $1M per household, inflating total TANF microsimulation from $9B target to $17.9T.

## [1.570.6] - 2026-02-19 06:19:21

### Fixed

- Cap all state TANF benefit formulas to prevent negative countable income from inflating benefits above the payment standard. Fixes NC household size .sum() bug and adds min_() caps to 38 state programs (AL, AK, AR, AZ, CA, CO, CT, DC, FL, HI, IA, IL, IN, KS, LA, MA, MD, MI, MN, MO, MS, MT, NC, ND, NE, NH, NJ, NM, NV, NY, OH, OK, OR, PA, RI, SC, SD, TX, UT, VT, WV, WY). Previously, negative countable income could produce benefits exceeding $1M per household, inflating total TANF microsimulation from $9B target to $17.9T.

## [1.570.5] - 2026-02-19 02:18:18

### Fixed

- Eliminate Montana federal income tax deduction for 2024+, per Senate Bill 399.

## [1.570.4] - 2026-02-19 02:12:57

### Fixed

- Missouri Social Security deduction now correctly requires age 62+ (SSDI has no age limit per MO Form MO-A Section C).

## [1.570.3] - 2026-02-19 01:56:51

### Changed

- Updated state CTCs list to include Georgia CTC, Maine Dependent Exemption Credit, and corrected Massachusetts credit reference.
- Updated state EITCs list to separate Maryland and Virginia into refundable and non-refundable components.

## [1.570.2] - 2026-02-19 00:48:35

### Fixed

- Fix Arkansas income tax credits to use net taxable income (AGI) when low income tax table applies.

## [1.570.1] - 2026-02-19 00:30:41

### Fixed

- Fix MN CTC eligible child check to require dependent status.

## [1.570.0] - 2026-02-19 00:12:01

### Added

- Add Wisconsin retirement income exclusion (Line 16, $24K, age 67+).

## [1.569.0] - 2026-02-18 21:12:35

### Changed

- Wire up all 39 state TANF programs, add takeup support, and remove tanf_reported short-circuit.

## [1.568.3] - 2026-02-18 18:07:53

### Changed

- Update California income tax parameters for 2025.

## [1.568.2] - 2026-02-17 23:10:10

### Changed

- Update Wisconsin 2025 income tax brackets (Act 15 expanded 4.4% bracket with inflation adjustment), standard deduction, and add 2025 references to all WI income tax parameters.

## [1.568.1] - 2026-02-17 22:50:07

### Changed

- Update DC 2025 tax parameters for Property Tax Credit ($1,425 max, $66,000/$90,000 AGI limits), KCCATC max ($1,200), and KCCATC income limits ($180,100/$90,000), and add 2025 D-40 Booklet references to all DC income tax parameters.

## [1.568.0] - 2026-02-17 21:11:33

### Changed

- Update Ohio income tax model for tax year 2025 with new brackets, exemptions, credits, and $750k/$500k personal exemption phase-out per HB 96.

## [1.567.3] - 2026-02-17 19:26:10

### Changed

- Add 2025 rate of 0 for repealed NH Interest and Dividends tax, add TIR 2025-001 repeal reference to remaining parameter files, fix unit metadata on age parameters, and update broken statute URLs to gc.nh.gov.

## [1.567.2] - 2026-02-17 18:18:36

### Fixed

- Split CI state baseline tests into 3 sequential batches to fix timeout and memory issues.
- Move NY baseline tests back into the states job as its own batch.

## [1.567.1] - 2026-02-17 15:07:07

### Fixed

- Fix Maryland CDCC to use the federal credit allowed (cdcc) instead of the potential credit (cdcc_potential).

## [1.567.0] - 2026-02-17 05:32:19

### Changed

- Updated Oregon 2025 income tax parameters (tax brackets, standard deduction, exemption credit, federal tax subtraction caps, CTC/Kids Credit, kicker rate) and added 2025 references to all parameters.

### Fixed

- Fixed Oregon federal tax subtraction cap rounding intervals for married filing separately (100 to 25, matching half of other filing statuses' interval of 50).
- Removed incorrect OR-40 page 20 references from Oregon retirement income credit parameters (page 20 contains kicker worksheet, not retirement income credit; OR-17 references remain as authoritative source).

## [1.566.0] - 2026-02-17 05:27:49

### Added

- Adds New Jersey ANCHOR property tax relief program with income-based benefit amounts for homeowners and renters.
- Adds New Jersey Stay NJ senior property tax reimbursement program for eligible seniors aged 65+.

### Changed

- Updates New Jersey income tax parameters with 2025 references including tax brackets, exemptions, deductions, and credits.

## [1.565.1] - 2026-02-17 04:22:10

### Changed

- {'description': 'Updates Idaho income tax parameters with 2025 references per HB 40.\nImplements military retirement full exemption for 2025 (no age requirement).\nAdds comprehensive 2025 test coverage for tax calculations, grocery credit, and CTC.\n', 'title': 'Update Idaho individual income tax for 2025'}

## [1.565.0] - 2026-02-17 00:21:20

### Added

- Updated Arizona 2025 standard deductions ($15,750 single/$31,500 joint/$23,625 HOH).
- Added 2025 references to Arizona income tax parameters.
- Added comprehensive 2025 integration tests for Arizona income tax model.

### Changed

- Updated Arizona charitable contribution credit with 2025 references.
- Updated Arizona capital gains subtraction rate with 2025 references.
- Updated Arizona family tax credit, dependent credit, and exemption parameters with 2025 values.

## [1.564.2] - 2026-02-16 21:05:30

### Added

- Comprehensive Kansas 2025 income tax integration tests.

### Changed

- Updated Kansas disabled veteran exemption from $2,250 to $2,320 for 2025+.
- Added 2025 Form K-40 references to all Kansas income tax parameters.
- Kansas food sales tax credit removed from nonrefundable credits list for 2025+ (credit eliminated).

## [1.564.1] - 2026-02-16 20:38:19

### Changed

- Update Iowa income tax to flat 3.8% rate for 2025 per SF 2442
- Update Iowa alternate tax rate to 4.3% for 2025

## [1.564.0] - 2026-02-16 19:11:59

### Changed

- Update Washington capital gains tax with 2025 tiered rates (7% up to $1M, 9.9% above $1M per ESSB 5813), inflation-adjusted deductions, and Working Families Tax Credit amounts.

## [1.563.2] - 2026-02-16 17:49:52

### Changed

- Update North Dakota income tax parameters for 2025 with new bracket thresholds, marriage penalty credit values, and form references.

## [1.563.1] - 2026-02-16 16:09:28

### Changed

- Add 2025 references with page numbers to Pennsylvania income tax parameters

## [1.563.0] - 2026-02-16 14:52:53

### Added

- Montana Temporary Assistance for Needy Families (TANF).

## [1.562.3] - 2026-02-16 03:46:10

### Fixed

- Fix Maryland Child Tax Credit AGI eligibility boundary to include filers with exactly $24,000 AGI per Worksheet 21C.

## [1.562.2] - 2026-02-16 03:42:03

### Changed

- Update Massachusetts income tax parameters for 2025, including surtax threshold ($1,083,150), Senior Circuit Breaker credit max ($2,820), income limits, and property value limit ($1,298,000).

## [1.562.1] - 2026-02-16 03:09:22

### Changed

- Update Arkansas income tax parameters for 2025 including tax rate brackets, reduction schedule, standard deductions, low income tax tables, and additional tax credit for qualified individuals.

## [1.562.0] - 2026-02-16 02:17:35

### Added

- Create Oregon dependent exemption credit reform to separate dependent exemptions with configurable age limits and universal mode.

## [1.561.1] - 2026-02-16 01:39:50

### Changed

- Add 2025 form references to North Carolina income tax parameters confirming unchanged values for standard deduction, child deduction, and other provisions.

## [1.561.0] - 2026-02-16 01:39:11

### Changed

- Update Maine income tax parameters for 2025 including bracket thresholds, personal exemption, deduction and exemption phaseout thresholds, itemized deduction cap, pension exclusion cap, and add 2025 references.

## [1.560.3] - 2026-02-16 01:34:59

### Fixed

- Fix ga_exemptions formula in repeal_state_dependent_exemptions reform to use correct parameter path.
- Fix ks_exemptions in repeal_state_dependent_exemptions reform to handle 2024+ by_filing_status branch.

## [1.560.2] - 2026-02-16 01:32:52

### Changed

- Update Nebraska income tax parameters for 2025 with new bracket thresholds, standard deduction amounts, exemption credit, and form references.

## [1.560.1] - 2026-02-16 01:29:52

### Changed

- Add 2025 Delaware income tax form references to parameter files.

## [1.560.0] - 2026-02-16 01:29:02

### Added

- Add 2025 CTC values from official NM PIT Packet Table 4
- Add 2025 PIT Packet references to all NM income tax parameters
- Update armed forces retirement exemption to reflect HB-0252 making it permanent

## [1.559.0] - 2026-02-16 01:28:23

### Added

- Adds 2025 references with page numbers to all Maryland income tax parameters.

## [1.558.5] - 2026-02-16 01:26:34

### Changed

- Update West Virginia income tax rates for 2025 per SB 2033.

## [1.558.4] - 2026-02-16 01:25:53

### Fixed

- Michigan surtax reform now activates correctly when in_effect parameter is toggled in the app.

## [1.558.3] - 2026-02-16 01:24:59

### Changed

- Update Indiana county income tax rates with 2022-2025 data from official DOR publications, fix rate errors for Allen and Dearborn counties, fix Bartholomew County parameter key typo, and update references to 2025 IT-40 and legal code.

## [1.558.2] - 2026-02-16 01:16:13

### Fixed

- Fix student loan interest deduction eligibility (IRC § 221) to remove incorrect AOC eligibility requirement. The previous implementation required is_eligible_for_american_opportunity_credit to be true, but this is not a legal requirement. While § 221(d)(3) references § 25A(b)(3) for the definition of "eligible student", this refers to the student's status when the loan was originally taken out, not current-year AOC eligibility.

## [1.558.1] - 2026-02-16 00:14:38

### Fixed

- Remove taxable_social_security from NJ subtractions to fix double exclusion bug. Social Security was already excluded from NJ gross income.

## [1.558.0] - 2026-02-15 23:33:04

### Changed

- Update Montana income tax parameters for 2025, including bracket thresholds, capital gains thresholds, old age subtraction inflation adjustment, 529 tuition subtraction cap increase, and references.

## [1.557.2] - 2026-02-14 03:01:37

### Changed

- Update Louisiana income tax parameter references from House Bill 10 to enacted legal code and add 2025 IT-540 form references.

### Fixed

- Fix Louisiana disability income exemption cap incorrectly set to $12,000 for 2025 (actual value remains $6,000 per RS 47:44.1(B)).

## [1.557.1] - 2026-02-14 02:56:16

### Changed

- Update Colorado Child Tax Credit income thresholds for 2025 (single $26K/$51K/$77K, joint $36K/$61K/$87K).
- Update Colorado CollegeInvest contribution subtraction limits for 2025 (single $25,400, joint $38,100).
- Update Colorado ABLE contribution subtraction caps for 2025 (single $25,400, joint $38,100).
- Fix Colorado Care Worker Tax Credit start date from 2026 to 2025 per C.R.S. 39-22-566.
- Fix typo in Colorado CTC head of household rate threshold date (2015 to 2022).

## [1.557.0] - 2026-02-13 20:55:08

### Changed

- Update Mississippi income tax parameters with 2025 references and replace bill references with legal code citations.

## [1.556.2] - 2026-02-13 19:31:10

### Changed

- Update CBO baseline projections to February 2026 (Budget and Economic Outlook 2026 to 2036), extending all calibration targets and CPI parameters through 2036.

## [1.556.1] - 2026-02-13 18:38:12

### Changed

- Update CPI-U, C-CPI-U, and CPI-W projections for 2026+ based on CBO September 2025 interim inflation update

## [1.556.0] - 2026-02-13 17:37:15

### Added

- Iowa Family Investment Program (FIP), the state's TANF cash assistance program.

## [1.555.3] - 2026-02-12 22:42:22

### Changed

- Add 2025 Vermont income tax values, renter credit income limits, and form references to parameter files.

## [1.555.2] - 2026-02-12 18:16:49

### Changed

- Update Kentucky income tax model for 2025, including standard deduction ($3,270), tax rate (4%), and all tax credits with official 2025 references.

## [1.555.1] - 2026-02-12 17:44:36

### Changed

- DC EITC match rate updated to 100% for 2025 per Act 26-214.

## [1.555.0] - 2026-02-11 17:26:50

### Added

- Implement Utah HB 210 Substitute 2 marriage tax credit (Section 59-10-1049)

## [1.554.1] - 2026-02-10 15:34:12

### Fixed

- Fix RI high earner tax and social security exemption reform exports to match standard pattern

## [1.554.0] - 2026-02-08 04:15:39

### Added

- Add tax_unit_is_required_to_file variable for rules-based filing requirement.
- Add eligible_for_refundable_credits variable for EITC/CTC eligibility check.
- Add would_file_if_eligible_for_refundable_credit propensity variable.
- Add would_file_taxes_voluntarily propensity variable for voluntary filers.

### Changed

- Refactor tax_unit_is_filer to use three-part filing logic with propensity variables.

## [1.553.0] - 2026-02-07 18:08:52

### Added

- Add liquid asset input variables (bank_account_assets, stock_assets, bond_assets), ssi_countable_resources, and spm_unit_cash_assets aggregation
- Add takes_up_ssi_if_eligible variable for SSI takeup modeling

### Changed

- SSI resource test now uses actual imputed assets instead of random pass rate
- SSI benefit now applies takeup in microsimulation

## [1.552.0] - 2026-02-07 00:40:26

### Added

- Section 1931 deprivation requirement parameter for non-expansion states
- is_single_parent_household variable for Medicaid deprivation rules
- Head Start and Early Head Start takeup variables
- SSI resource test now uses actual policy logic in individual sim

### Changed

- Moved all stochastic randomness to data package for deterministic country package
- is_parent_for_medicaid_nfc now checks Section 1931 deprivation requirements
- Head Start and Early Head Start benefits now multiply by takeup
- WIC would_claim_wic and is_wic_at_nutritional_risk default to True (resolved in data package)

## [1.551.1] - 2026-02-07 00:23:46

### Changed

- Update Alabama 2025 Income tax.

## [1.551.0] - 2026-02-07 00:10:55

### Added

- Arizona Cash Assistance (TANF) program.

## [1.550.2] - 2026-02-05 04:45:16

### Fixed

- Fixed incorrect label for ca_ala_general_assistance_countable_income_person variable.

## [1.550.1] - 2026-02-04 19:32:22

### Fixed

- Fix NY ESCC post-2024 to allow ITIN holders in baseline (revert S.9077 reform).

## [1.550.0] - 2026-02-03 04:40:30

### Added

- is_qualifying_child_dependent variable for age-based qualifying child test
- is_qualifying_relative_dependent variable for income-based qualifying relative test
- dependent_gross_income variable for calculating dependent gross income

### Changed

- is_child_dependent now includes qualifying child, qualifying relative, and disability pathways
- Head of household eligibility now correctly includes qualifying relatives (fixes issue 6994)

## [1.549.0] - 2026-02-02 19:07:06

### Added

- Add NY S.9077 Empire State Child Credit ITIN expansion reform allowing children with ITINs to qualify starting 2027.

## [1.548.0] - 2026-02-02 19:05:08

### Added

- Update South Carolina income tax parameters for 2025, including reduced top rate (6.0%) and adjusted brackets.

## [1.547.0] - 2026-02-02 18:49:52

### Added

- Implement Maryland Temporary Cash Assistance (TCA) program.

## [1.546.1] - 2026-02-02 17:32:10

### Fixed

- Missouri income tax now correctly allocates above-the-line deductions proportionally by gross income, ensuring capital loss deductions are not lost when one spouse has no income.

## [1.546.0] - 2026-02-02 01:50:17

### Added

- Add 2025 references to all New York State and NYC income tax parameters.
- Update geothermal energy system credit cap to $10,000 for systems placed in service on/after July 1, 2025.
- Add 2025 NY income tax integration tests.

## [1.545.3] - 2026-02-02 01:38:39

### Changed

- Add historical data for Massachusetts TAFDC parameters

## [1.545.2] - 2026-02-02 01:21:49

### Changed

- Backdate DC TANF, GAC, and POWER parameters to program establishment dates.

## [1.545.1] - 2026-02-02 01:15:31

### Added

- Backdate Texas TANF program.

## [1.545.0] - 2026-02-02 01:03:18

### Fixed

- Implement NJ same category rule - net losses in any income category (capital gains, S-corp, partnership, rental, business) are now disregarded and cannot offset income from other categories.

## [1.544.0] - 2026-02-02 00:56:29

### Changed

- {'description': 'Updates Georgia income tax parameters for 2025 tax year based on the IT-511 Instructions Booklet:\n- Corrects 2025 tax rate to 5.19% (from incorrectly projected 5.29%)\n- Adds 2025 IT-511 references to all income tax parameters\n- Verifies CDCC credit rate at 50% of federal credit for 2025\n- Confirms standard deductions, dependent exemption, retirement exclusions, military retirement exclusions, and itemizer credit values\n', 'title': 'Update Georgia 2025 individual income tax model'}

## [1.543.0] - 2026-02-02 00:48:06

### Changed

- Disable Montana _indiv computation path for 2024+ when married filing separately on same return is no longer allowed.

## [1.542.1] - 2026-02-02 00:34:36

### Changed

- {'title': 'Update Hawaii income tax parameters with 2025 references'}

## [1.542.0] - 2026-02-02 00:11:19

### Added

- NY TANF pre-October 2022 gross income test and immigration eligibility check.

### Changed

- NY TANF parameters backfilled to 1998 with October 2022 reform rules per 22-ADM-11.
- NY TANF earned income deduction calculation order changes by reform date.

## [1.541.1] - 2026-02-02 00:00:17

### Fixed

- CT Social Security benefit adjustment now uses actual federal taxable Social Security amount instead of 85% of gross Social Security.

## [1.541.0] - 2026-02-01 23:33:30

### Added

- Oregon Healthier Oregon program providing Medicaid-equivalent coverage for undocumented immigrants.

## [1.540.1] - 2026-02-01 23:24:58

### Changed

- Update Colorado income tax parameters for tax year 2025.

## [1.540.0] - 2026-02-01 23:13:46

### Added

- Add comprehensive 2025 test cases for Oklahoma income tax (103 tests).

### Changed

- Update Oklahoma income tax parameters for 2025 with current form references.
- Increase pension subtraction limit from $10,000 to $20,000 for 2024+ per HB 2020.
- Enhance documentation for Oklahoma income tax variables with calculation examples and regulatory references.

## [1.539.0] - 2026-02-01 22:33:33

### Changed

- Add 2025 references to all Missouri income tax parameters.
- Add 2025 value for mo_max_social_security_benefit ($48,216).
- Add 2025 test cases for Missouri income tax and capital gains subtraction.

## [1.538.1] - 2026-02-01 22:20:32

### Changed

- Update Illinois TANF parameter historical dates to reflect actual policy enactment dates.

## [1.538.0] - 2026-02-01 22:15:00

### Added

- Backdating Maine TANF parameters.

## [1.537.4] - 2026-02-01 22:06:11

### Fixed

- Backdate Oklahoma TANF parameters to correct effective dates.
- Backdate Wisconsin Works parameters to correct effective dates.
- Backdate Ohio Works First parameters to correct effective dates and add COLA multiplier for dynamic payment standards.

## [1.537.3] - 2026-02-01 21:59:11

### Fixed

- Corrected 2020 surviving spouse standard deduction from $24,400 to $24,800 to match joint filers per 26 USC 63(c)(2)(A).

## [1.537.2] - 2026-02-01 21:55:06

### Fixed

- Mississippi income tax now correctly uses loss-limited capital gains (federal $3K limit) instead of unlimited raw capital gains.

## [1.537.1] - 2026-02-01 21:42:20

### Fixed

- Arizona long-term capital gains subtraction now correctly returns zero when there is a net capital loss, rather than using raw long-term capital gains.

## [1.537.0] - 2026-02-01 20:53:00

### Added

- Add Alabama Family Assistance (TANF) program.

## [1.536.0] - 2026-02-01 20:30:41

### Added

- Vermont TANF (Reach Up) program

## [1.535.0] - 2026-02-01 19:35:05

### Added

- South Carolina TANF (Temporary Assistance for Needy Families) program

## [1.534.6] - 2026-02-01 18:13:47

### Fixed

- Fix Rhode Island retirement income subtraction to apply the cap per person instead of per tax unit.

## [1.534.5] - 2026-01-31 20:58:31

### Added

- Tests for TAXSIM output variables to achieve 100% coverage.

## [1.534.4] - 2026-01-31 19:46:35

### Changed

- Pin black==26.1.0 in dev dependencies and update CI and Makefile to use uv for consistent formatting.

## [1.534.3] - 2026-01-31 16:52:24

### Added

- Tests for tax_unit_is_filer variable covering filing requirement logic.

## [1.534.2] - 2026-01-31 03:23:17

### Added

- Add 2018 CHIP FCEP pregnant income limits from MACPAC MACStats December 2018 Data Book.

## [1.534.1] - 2026-01-31 00:45:39

### Added

- Added income_tax_positive variable for CBO-consistent calibration

## [1.534.0] - 2026-01-30 20:44:48

### Added

- Add Virginia HB979 income tax reform with new 8% and 10% brackets for high earners.

## [1.533.0] - 2026-01-30 15:33:22

### Changed

- Update Michigan 2025 Individual Income Tax Model parameters

## [1.532.4] - 2026-01-29 23:19:08

### Changed

- Update Virginia 2025 income tax parameters with 2025 Form 760 references
- Add rebate values for 2024 ($200/$400) and 2025 ($0)
- Add 2025 tests for standard deduction, EITC, military benefit subtraction, age deduction, rebate, and exemptions

## [1.532.3] - 2026-01-29 21:06:35

### Fixed

- Medicaid category assignment now correctly evaluates mandatory groups (parent, pregnant, SSI) before optional expansion groups, per federal eligibility rules.

## [1.532.2] - 2026-01-29 05:35:07

### Added

- Backdate New Hampshire interest and dividends tax parameters to 2020.

## [1.532.1] - 2026-01-29 03:57:29

### Changed

- Updated uv.lock dependencies.

## [1.532.0] - 2026-01-29 02:38:20

### Added

- California CalWORKs Stage 2 (C2AP) child care subsidy for former CalWORKs recipients within 24 months of leaving cash aid.
- California CalWORKs Stage 3 (C3AP) child care subsidy for former CalWORKs recipients who exhausted Stage 2 eligibility.
- California Alternative Payment Program (CAPP) child care subsidy for income-eligible families who never received CalWORKs.

## [1.531.0] - 2026-01-29 02:17:08

### Added

- Illinois Home Weatherization Assistance Program (IHWAP) eligibility.
- Reusable SMI (State Median Income) function.

## [1.530.0] - 2026-01-28 21:20:03

### Added

- Illinois Senior Citizens Real Estate Tax Deferral Program (il_scretd)

## [1.529.0] - 2026-01-28 21:12:25

### Added

- Illinois I-PASS Assist program eligibility.

## [1.528.0] - 2026-01-28 21:05:51

### Changed

- Pin New York itemized deductions to pre-TCJA rules per Tax Law § 615

## [1.527.2] - 2026-01-28 16:04:08

### Fixed

- Exclude Medicaid recipients from QI (Qualifying Individual) eligibility.

## [1.527.1] - 2026-01-27 21:30:41

### Fixed

- Medicare Savings Program (MSP) calculation now returns correct benefit values instead of null.

## [1.527.0] - 2026-01-27 03:46:23

### Added

- Add Connecticut EITC $250 qualifying child bonus for tax year 2025.

### Changed

- Update Connecticut tax parameter references to 2025 CT-1040 Instructions.

## [1.526.2] - 2026-01-27 03:21:56

### Changed

- Add historical values to Minnesota MFIP parameters.

## [1.526.1] - 2026-01-27 03:18:40

### Changed

- Backdate North Carolina TANF parameters to 1997.

## [1.526.0] - 2026-01-27 03:13:11

### Changed

- Update DC Child Tax Credit for 2026+ based on new statute (DC Code 47-1806.17), including increased credit amount ($1,000), expanded age eligibility (under 18), removed child cap, lower income thresholds, and higher phase-out rate.

## [1.525.0] - 2026-01-26 23:05:41

### Changed

- Update Illinois income tax parameters for 2025 and add 2025 citations.

## [1.524.1] - 2026-01-26 20:28:28

### Added

- Update SSI federal benefit rates, student earned income exclusion, and SGA amounts for 2026.

## [1.524.0] - 2026-01-26 19:35:03

### Added

- Add census block-level geography variables (block_geoid, tract_geoid, cbsa_code, place_fips, vtd, puma, sldu, sldl, zcta) for granular geographic analysis

## [1.523.1] - 2026-01-26 14:37:21

## [1.523.0] - 2026-01-26 14:14:48

### Changed

- Pin New York itemized deductions to pre-TCJA rules per Tax Law § 615

## [1.522.0] - 2026-01-25 22:40:42

### Added

- Implement New Jersey WorkFirst (WFNJ).

## [1.521.0] - 2026-01-25 21:40:34

### Added

- Louisiana Family Independence Temporary Assistance Program (FITAP).

## [1.520.0] - 2026-01-25 21:25:01

### Added

- Add Alaska ATAP (Temporary Assistance Program) implementation with income eligibility tests, work incentive deductions, need standards, and benefit calculation based on 7 AAC 45.

## [1.519.0] - 2026-01-25 21:17:46

### Added

- Implemented North Dakota Temporary Assistance for Needy Families (TANF) program

## [1.518.0] - 2026-01-25 21:13:51

### Added

- Add New Mexico Works (NM Works) program

## [1.517.0] - 2026-01-25 20:55:20

### Added

- Add expanded income base option for CRFB AGI surtax reform, including retirement contributions, HSA contributions, student loan interest, tax-exempt Social Security, foreign earned income exclusion, tax-exempt interest, and health insurance premiums.

## [1.516.4] - 2026-01-25 19:35:47

### Fixed

- Add safety catch in aca_ptc to return zero before 2025 to prevent breaking 2024 microsim runs.

## [1.516.3] - 2026-01-25 18:31:23

### Fixed

- Update Iowa SNAP self-employment deduction effective date from 2021-10-01 to 2012-08-01 based on USDA FNS State Options Report research.

## [1.516.2] - 2026-01-25 18:19:02

### Changed

- Simplify Pell Grant calculation method by removing enum indirection and using time-based formula.

## [1.516.1] - 2026-01-25 17:33:26

### Changed

- Use default argument to numpy.select instead of dummy True condition for ~10% performance improvement.

## [1.516.0] - 2026-01-25 17:15:31

### Added

- partnership_se_income variable for general partners' SE income from Schedule K-1 Box 14, now included in taxable_self_employment_income per 26 USC 1402(a).

## [1.515.0] - 2026-01-25 16:54:14

## [1.514.2] - 2026-01-25 13:30:04

### Fixed

- Fix Iowa SNAP self-employment simplified deduction rate from 0% to 40%.

## [1.514.1] - 2026-01-25 13:03:30

### Added

- Added pandas 3.0 compatibility tests to verify policyengine-core fixes for StringDtype and StringArray handling

### Changed

- Removed pandas <3.0 version cap to enable pandas 3.0 support
- Bumped policyengine-core minimum version to 3.23.5 for pandas 3 compatibility (includes Enum.encode() fix)

## [1.514.0] - 2026-01-23 21:14:19

### Added

- AGI surtax reform.

## [1.513.1] - 2026-01-23 18:35:29

### Fixed

- Update SC H.3492 reform to use 5-year in_effect check pattern consistent with other contributed reforms.

## [1.513.0] - 2026-01-23 16:04:44

### Added

- Implement Virginia TANF program.

## [1.512.0] - 2026-01-23 15:27:36

### Added

- Add Wyoming POWER program

## [1.511.2] - 2026-01-22 23:38:46

### Fixed

- Use `uv sync --extra dev` in CI to correctly install optional dev dependencies including coverage.
- Improve selective test runner to only run tests for specific subfolders (states, congress, local) instead of entire parent directories.
- Pin pandas to <3.0 to prevent StringDtype incompatibility with numpy.

## [1.511.1] - 2026-01-21 21:46:53

### Fixed

- Remove DACA_TPS from immigration_status.

## [1.511.0] - 2026-01-21 20:53:40

### Added

- NY Assembly Bill A06774 Enhanced Child and Dependent Care Credit reform.

## [1.510.0] - 2026-01-21 20:02:25

### Added

- NY Senate Bill S04487 Supplemental Empire State Child Tax Credit for Newborns reform.

## [1.509.0] - 2026-01-21 16:28:14

### Added

- NY A04038 Enhanced Empire State Child Credit for Infants Act reform.

## [1.508.2] - 2026-01-21 15:19:45

### Changed

- Update 2026 federal poverty guidelines.

## [1.508.1] - 2026-01-20 19:20:31

### Added

- Add breakdown_labels metadata to parameters with range() dimensions for semantic labelling.

## [1.508.0] - 2026-01-19 22:07:57

### Added

- Update Rhode Island 2025 Individual Income Tax Model.

## [1.507.0] - 2026-01-19 19:54:16

### Added

- Add SC H.3492 partially refundable EITC reform.

## [1.506.0] - 2026-01-19 19:53:06

### Added

- Add Utah HB 210 (2026) structural reform implementing the taxpayer credit add-on for married filers ($543 MFS, $1,086 joint/surviving spouse) with phaseout.

## [1.505.0] - 2026-01-19 18:32:47

### Added

- Model RI Governor Dan McKee's 2027 tax proposals including a new child tax credit, Social Security exemption expansion, new top income tax bracket, and pension/annuity exemption updates.

## [1.504.0] - 2026-01-19 18:07:10

### Fixed

- Formatting.

## [1.503.3] - 2026-01-19 17:30:20

### Fixed

- Added missing breakdown and label metadata to pseudo-breakdown parameters.

## [1.503.2] - 2026-01-19 16:39:43

### Fixed

- Added missing label metadata to bracket/scale parameters that had no labels.

## [1.503.1] - 2026-01-19 16:19:40

### Fixed

- Added missing label metadata to breakdown parameters that had breakdown definitions but no labels.

## [1.503.0] - 2026-01-19 16:08:41

### Changed

- Replaced .claude git submodule with policyengine-claude plugin auto-install configuration.

## [1.502.3] - 2026-01-15 22:29:01

### Fixed

- Fix CA Medi-Cal immigration eligibility for DACA/TPS holders in 2026. Previously, DACA/TPS holders incorrectly lost eligibility after the January 2026 enrollment freeze. Per WCLP guidance, DACA/TPS holders are not affected by the freeze and can still newly enroll.

## [1.502.2] - 2026-01-15 22:18:44

### Added

- Add Microsimulation API documentation covering calc/calculate methods, map_to parameter, available datasets, subsampling, winners/losers analysis, and weight sanity checks.

## [1.502.1] - 2026-01-15 22:15:03

### Added

- Add parameter discovery documentation guide

## [1.502.0] - 2026-01-15 20:15:33

### Added

- Add range-based phaseout option for RI CTC with phaseout.start and phaseout.end parameters.

## [1.501.0] - 2026-01-15 20:02:12

### Added

- Adjust CLAUDE.md in US repo.

## [1.500.4] - 2026-01-14 23:20:21

### Changed

- Updated uv.lock dependencies.

## [1.500.3] - 2026-01-14 21:44:33

### Added

- Add is_blind to IL HBWD disability eligibility check.

### Fixed

- Fix IL HBWD earned income exemptions to apply only to disabled/blind persons.

## [1.500.2] - 2026-01-13 23:26:02

### Fixed

- Riverside County General Relief eligibility now correctly excludes units where all persons are ineligible.
- Riverside County General Relief SSI check changed from unit-level to person-level, so only the individual receiving SSI is excluded, not all household members.

## [1.500.1] - 2026-01-13 23:22:39

### Changed

- Remove concurrency block from push workflow to allow parallel CI runs.

## [1.500.0] - 2026-01-13 22:53:31

### Added

- Add il_aabd_use_reported_ssi flag to allow API partners to override SSI income for IL AABD calculation.

## [1.499.1] - 2026-01-13 22:35:23

### Fixed

- Fix test_batched.py incorrectly marking tests as passed when failure count ends in 0.
- Fix push.yaml concurrency to queue runs instead of cancelling versioning jobs.

## [1.499.0] - 2026-01-12 19:45:59

### Added

- CDCTC reform that makes families eligible if at least one parent works (instead of requiring both parents to work)

## [1.498.1] - 2026-01-12 18:30:41

### Fixed

- Remove 51 invalid County enum entries (wrong state assignments, non-existent county/state combinations). Validated against Census 2020 county reference data.

## [1.498.0] - 2026-01-08 18:02:47

### Added

- Colorado OmniSalud program providing ACA marketplace subsidies for undocumented immigrants and DACA recipients.

## [1.497.1] - 2026-01-06 14:58:50

### Changed

- Updated uv.lock dependencies.

## [1.497.0] - 2026-01-05 21:26:26

### Added

- Create reform to separate dependent children from Virginia personal exemption.

## [1.496.2] - 2026-01-05 16:26:06

### Changed

- Updated weekly uv.lock workflow to include changelog entry.

## [1.496.1] - 2026-01-05 15:41:57

### Changed

- Updated weekly uv.lock workflow to include changelog entry.

## [1.496.0] - 2026-01-05 00:21:45

### Added

- Tennessee TANF (Families First) program implementation

## [1.495.0] - 2026-01-05 00:20:33

### Added

- Nevada TANF (Temporary Assistance for Needy Families) program

## [1.494.0] - 2026-01-05 00:18:02

### Added

- West Virginia Works program implementation

## [1.493.0] - 2026-01-05 00:02:11

### Added

- Connecticut Temporary Family Assistance (TFA/TANF)

## [1.492.0] - 2026-01-04 23:28:13

### Added

- Implement Rhode Island TANF (Rhode Island Works) program

## [1.491.0] - 2026-01-04 22:56:53

### Added

- Add Delaware TANF (Temporary Assistance for Needy Families)

## [1.490.0] - 2026-01-04 22:20:49

### Added

- South Dakota Temporary Assistance for Needy Families (TANF) program

## [1.489.0] - 2026-01-04 22:11:59

### Added

- Implemented Maine TANF program

## [1.488.0] - 2026-01-04 22:05:35

### Added

- Add New Hampshire FANF (Financial Assistance to Needy Families) program with eligibility determination, payment standard (60% FPG), earned income disregards, and benefit calculation.

## [1.487.0] - 2026-01-04 21:45:18

### Added

- Hawaii TANF (Temporary Assistance for Needy Families) program

## [1.486.0] - 2026-01-04 20:46:59

### Added

- Add phase-out logic to CRFB Social Security nonrefundable credit based on AGI thresholds (6% rate above $150k joint, $75k other).

## [1.485.4] - 2026-01-02 21:22:24

### Fixed

- ACA required contribution percentage now correctly handles flat brackets (e.g., 0-133% FPL) per 26 USC 36B by separating thresholds, initial rates, and final rates into independent parameters.

## [1.485.3] - 2026-01-02 19:33:52

### Fixed

- Remove non-existent labels from weekly uv.lock workflow PR creation.

## [1.485.2] - 2026-01-02 19:06:03

### Fixed

- Weekly uv.lock workflow now targets main branch and uses native gh CLI for PR creation.

## [1.485.1] - 2026-01-02 18:29:05

### Added

- Add scheduled GitHub Action workflow for weekly uv.lock updates.

## [1.485.0] - 2025-12-29 22:22:39

### Fixed

- Arizona Family Tax Credit now correctly uses Arizona AGI plus exemptions for income eligibility determination per ARS 43-1073.

## [1.484.3] - 2025-12-29 21:31:29

### Added

- Updated SNAP BBCE gross income limits for New Mexico (200% FPL effective 2024-10-01) and Alaska (200% FPL effective 2025-07-01).
- Added South Dakota to BBCE parameters as non-BBCE state.
- Added and backdated Maryland SUA and LUA values.

## [1.484.2] - 2025-12-29 20:01:21

## [1.484.1] - 2025-12-29 19:18:44

### Changed

- Update Virginia 2025 income tax parameters with 2025 Form 760 references
- Add rebate values for 2024 ($200/$400) and 2025 ($0)
- Add 2025 tests for standard deduction, EITC, military benefit subtraction, age deduction, rebate, and exemptions

## [1.484.0] - 2025-12-29 16:26:00

### Added

- Illinois Health Benefits for Immigrants (HBI) program covering All Kids, HBIA (adults 42-64), and HBIS (seniors 65+).

## [1.483.0] - 2025-12-29 14:52:56

### Added

- Minnesota 2025 income tax parameter updates and new programs including K-12 Education Credit/Subtraction, 529 Contribution Subtraction, Military Pension Subtraction, and Active Duty Military Pay Subtraction.

## [1.482.0] - 2025-12-29 13:39:35

### Added

- Idaho Temporary Assistance for Families in Idaho (TAFI) program, implementing income eligibility, resource limits, and benefit calculation (closes

## [1.481.0] - 2025-12-29 02:02:32

### Added

- Michigan Family Independence Program (FIP/TANF)

## [1.480.0] - 2025-12-29 02:00:46

### Added

- Georgia TANF program implementation

## [1.479.0] - 2025-12-28 23:17:19

### Added

- Add Mississippi TANF program.

## [1.478.0] - 2025-12-28 22:59:09

### Added

- Nebraska Aid to Dependent Children (ADC) program.

## [1.477.0] - 2025-12-28 22:37:09

### Added

- Add Kansas TANF program.

## [1.476.0] - 2025-12-28 22:18:45

### Added

- Implement Arkansas Transitional Employment Assistance (TEA/TANF) program

## [1.475.0] - 2025-12-28 22:16:11

### Added

- Added Oklahoma TANF (Temporary Assistance for Needy Families) program

## [1.474.0] - 2025-12-28 21:35:08

### Added

- Adds Utah Temporary Assistance for Needy Families (TANF) program.

## [1.473.0] - 2025-12-28 21:23:14

### Added

- Minnesota Family Investment Program (MFIP).

## [1.472.0] - 2025-12-28 21:07:30

### Added

- Add Kentucky TANF (K-TAP) program

## [1.471.0] - 2025-12-26 20:04:36

### Added

- Add Emergency Medicaid eligibility for undocumented immigrants

## [1.470.1] - 2025-12-23 14:23:08

### Fixed

- County variable now persists across periods when running over datasets, fixing incorrect fallback to first alphabetical county.

## [1.470.0] - 2025-12-21 23:13:06

### Added

- Illinois Prevention Initiative (PI) program.

## [1.469.0] - 2025-12-19 23:08:59

### Added

- Illinois Preschool For All (PFA) and Preschool For All Expansion (PFAE) programs with age (3-5), income (400% FPL), and weighted priority factor eligibility.
- New input variables for IEP status, developmental delay, non-English speaking home, parent education level, born outside US, and no prior formal early learning.

## [1.468.0] - 2025-12-19 20:53:46

### Added

- Ohio Works First (OWF) cash assistance program.

## [1.467.0] - 2025-12-19 15:39:42

### Added

- Implement Oregon TANF (Temporary Assistance for Needy Families) program with income eligibility, resource limits, and benefit calculations.

## [1.466.0] - 2025-12-19 15:31:15

### Added

- Indiana TANF program.

## [1.465.5] - 2025-12-18 20:55:25

### Fixed

- Updates the thresholds and marginal tax rates rates for the Missouri individual income tax in `parameters/gov/states/mo/tax/income/rates.yaml`
- Adds the variable `mo_capital_gains_subtraction.py` and the parameter `parameters/gov/states/mo/tax/income/subtractions/net_capital_gain/rate.yaml` for the 2025 inclusion a full deductibility of capital gains in calculating Missouri adjusted gross income.
- Adds `agi_subtractions.yaml` list parameter with the two MO AGI subtractions for 2025, and creates a `mo_agi_subtractions.py` variable (Person-level), which is referenced in the `mo_adjusted_gross_income.py` calculation.
- Adds `mo_capital_gains_subtraction_person.py` to allocate the capital gains subtraction proportionally to each person based on their share of long-term capital gains, preventing overcounting in multi-person tax units.
- Updates the `parameters/gov/states/mo/tax/income/minimum_taxable_income.yaml` parameter with the new 2025 value.
- Adds new legislative references

## [1.465.4] - 2025-12-18 15:55:33

### Changed

- Rebalance CI test jobs by moving NY state tests to NonStructural-Other and CRFB structural tests to Structural-Heavy.

## [1.465.3] - 2025-12-18 15:12:11

### Added

- Employer payroll tax revenue allocation variables (employer_ss_tax_income_tax_revenue and employer_medicare_tax_income_tax_revenue) for CRFB reform analysis.

### Fixed

- Trust fund revenue allocation now uses double-branching methodology per 42 U.S.C. 401 note Section 121(e), correctly splitting TOB between OASDI and Medicare HI.

## [1.465.2] - 2025-12-17 04:59:37

## [1.465.1] - 2025-12-17 04:17:16

### Added

- Add scheduled GitHub Action workflow for weekly uv.lock updates

## [1.465.0] - 2025-12-16 15:06:15

### Added

- Missouri TANF program.

## [1.464.2] - 2025-12-16 13:23:24

### Fixed

- Arizona property tax credit now uses correct income definition per ARS 43-1072 and ITR 12-1, excluding only Social Security (not pensions, capital gains, or exemptions)

## [1.464.1] - 2025-12-16 04:11:35

### Fixed

- Iowa Child and Dependent Care Credit now uses taxable income instead of net income.

## [1.464.0] - 2025-12-16 00:26:02

### Added

- Wisconsin Works (W-2) program with placement-based benefits and eligibility.

## [1.463.0] - 2025-12-16 00:00:49

### Added

- Pennsylvania TANF.

## [1.462.1] - 2025-12-15 23:24:43

### Fixed

- MA income tax now allows short-term capital losses to offset long-term capital gains in Part C

## [1.462.0] - 2025-12-15 22:36:33

### Fixed

- Maine Dependent Exemption Credit now correctly includes Credit for Other Dependents (ODC) qualifying dependents age 17 and older, as required by Maine statute 36 M.R.S. Section 5219-SS which references IRC Section 24 (including both CTC and ODC).

## [1.461.3] - 2025-12-15 22:10:21

### Fixed

- Fix DC Property Tax Credit incorrectly granting credit for negative AGI with zero rent/property taxes

## [1.461.2] - 2025-12-15 21:42:35

### Fixed

- Montana income tax calculation with negative capital gains now correctly produces zero tax instead of phantom positive tax

## [1.461.1] - 2025-12-15 21:03:17

### Fixed

- Hawaii Food/Excise Tax Credit now correctly handles negative AGI

## [1.461.0] - 2025-12-15 19:02:39

### Added

- Trust fund revenue variables (tob_revenue_total, tob_revenue_oasdi, tob_revenue_medicare_hi) using exact branching methodology
- Tier 1 and tier 2 taxable Social Security variables for proper OASDI vs Medicare HI allocation
- LSR recursion guard to prevent infinite loops when branches calculate variables

### Fixed

- Labor supply behavioral response infinite recursion bug

## [1.460.2] - 2025-12-15 18:31:12

### Fixed

- WV homestead excess property tax credit with negative income and zero property taxes

## [1.460.1] - 2025-12-13 04:31:57

### Fixed

- Update uv.lock during version bump so contributors don't need to run uv lock --upgrade after pulling from master.
- Change push workflow concurrency to queue runs instead of cancelling to ensure each merge completes.

## [1.460.0] - 2025-12-12 23:16:34

### Added

- Medicare Savings Program (MSP) with federal structure supporting QMB, SLMB, and QI eligibility levels.
- State-specific MSP asset test rules (AL, AZ, CA, CT, DE, DC, LA, MS, NM, NY, OR, VT have eliminated the asset test).

## [1.459.2] - 2025-12-12 18:28:16

### Fixed

- Fix IL AABD non-financial eligibility to require SSI status eligibility per IDHS Policy Manual PM 11-01-00.
- Remove retirement_distributions from IL AABD asset sources (incorrectly included income variable).

## [1.459.1] - 2025-12-12 18:20:04

### Fixed

- Replace is_medicaid_eligible with receives_medicaid in il_fpp_eligible.
- Fix IL HBWD disability eligibility to use medical definition without SGA test.

## [1.459.0] - 2025-12-12 14:32:00

### Added

- ACA PTC 700% FPL cliff reform extending subsidies with 8.5% contribution cap to 600% FPL and phaseout to 9.25% at 700% FPL

## [1.458.2] - 2025-12-12 14:10:11

### Fixed

- Floor only business and rental income sources in MI household resources per MI-1040CR form instructions.

## [1.458.1] - 2025-12-12 04:32:17

### Changed

- Split structural YAML tests into parallel CI jobs for better memory management.
- Add workflow concurrency to cancel in-progress CI runs when new commits are pushed to the same PR.

## [1.458.0] - 2025-12-11 18:30:32

### Added

- Add spm_unit_tenure_type variable at SPM unit level for local area calibration.

## [1.457.1] - 2025-12-11 00:31:16

### Fixed

- Replace is_medicaid_eligible with receives_medicaid in il_bcc_insurance_eligible.

## [1.457.0] - 2025-12-10 18:16:05

### Added

- Create reform to separate dependent children from Delaware Personal Credit.

## [1.456.2] - 2025-12-10 17:53:29

### Fixed

- Fix state_group enum usage in FPG parameter indexing for KY and WV tax credits

## [1.456.1] - 2025-12-10 17:43:25

### Added

- CI check to enforce uv.lock freshness, ensuring tests use the same dependency versions users get.

## [1.456.0] - 2025-12-10 15:49:56

### Added

- Add 20% qualified REIT/PTP income component.

## [1.455.0] - 2025-12-10 11:48:36

### Added

- Illinois Supplementary Medical Insurance Benefit (SMIB) Buy-In Program.
- SMIB eligibility based on categorical criteria (AABD, TANF, SSI recipients).
- SMIB benefit covering Medicare Part B premiums for eligible individuals.

## [1.454.1] - 2025-12-09 22:07:46

### Fixed

- Fix IL qualified noncitizen status parameters and TANF immigration eligibility.

## [1.454.0] - 2025-12-09 18:51:53

### Added

- CA Medi-Cal continuous coverage for existing undocumented enrollees after 2026 enrollment freeze.
- receives_medicaid input variable to indicate current Medicaid enrollment status.
- medi_cal_enrollment_freeze parameter for CA.

## [1.453.1] - 2025-12-09 15:58:42

### Fixed

- Apply the net income test to the New Jersey childless EITC.

## [1.453.0] - 2025-12-08 23:40:59

### Added

- Add Utah Military Retirement Credit (code AJ).

## [1.452.0] - 2025-12-05 22:06:02

### Added

- Illinois Family Planning Program (FPP).

## [1.451.0] - 2025-12-05 21:40:25

### Added

- Illinois Medicaid Presumptive Eligibility (MPE).

## [1.450.0] - 2025-12-05 21:39:43

### Added

- Illinois Health Benefits for Persons with Breast or Cervical Cancer (BCC) eligibility.
- Shared Illinois HFS immigration status eligibility variable.
- has_bcc_qualifying_coverage variable for creditable health coverage determination.

## [1.449.8] - 2025-12-04 16:58:21

### Changed

- Bump policyengine-core to 3.23.0 (adds strict enum validation).

### Fixed

- IL TANF now correctly recognizes veterans as eligible regardless of immigration status per 89 Ill. Admin. Code 112.10.

## [1.449.7] - 2025-12-04 10:32:18

### Fixed

- Fix New Jersey gross income computation.

## [1.449.6] - 2025-12-03 22:50:04

### Fixed

- Fix invalid filing_status enum values in test files (lowercase 'single', numeric '0', typos 'WIDWO' and 'HEAD_OF_HOUSE_HOLD').

## [1.449.5] - 2025-12-03 22:13:14

### Added

- WIC integration tests.

### Fixed

- WIC eligibility now requires valid demographic category per 42 U.S.C. § 1786(d)(1).

## [1.449.4] - 2025-12-03 21:46:07

### Fixed

- Fix Filing Status Issues in Missouri Test Files.

## [1.449.3] - 2025-12-03 13:07:31

### Fixed

- Fixed typo in Colorado state supplement directory name (state_suplement → state_supplement).

## [1.449.2] - 2025-12-03 05:42:15

### Changed

- Parameterized Montana spouse allocation factor for itemized deductions (was hardcoded 0.5)

## [1.449.1] - 2025-12-02 23:28:11

### Fixed

- StateGroup enum warnings for contiguous US states in state_group variable.

## [1.449.0] - 2025-12-02 22:19:22

### Added

- Add Medicare Part A premiums (full, reduced, premium-free based on quarters of coverage).
- Add Medicare Part B premiums with Income-Related Monthly Adjustment Amount (IRMAA).

## [1.448.0] - 2025-12-02 15:33:28

### Added

- Washington TANF.

## [1.447.0] - 2025-12-02 15:22:21

### Added

- Puerto Rico adjusted gross income calculation.

## [1.446.1] - 2025-12-02 02:33:48

### Fixed

- Prevent negative subtractions from acting as additions under the Ohio joint filing credit.

## [1.446.0] - 2025-12-02 02:31:25

### Added

- Puerto Rico net taxable income calculation.

## [1.445.0] - 2025-12-02 00:29:05

### Added

- Puerto Rico regular tax before credits and gradual adjustment.

## [1.444.1] - 2025-11-29 11:29:24

### Fixed

- Arkansas tax reduction thresholds.

## [1.444.0] - 2025-11-27 11:14:24

### Added

- Mamdani Millionaire Income Tax.

## [1.443.0] - 2025-11-26 18:22:22

### Added

- Illinois Health Benefits for Workers with Disabilities (HBWD) program.

## [1.442.1] - 2025-11-26 17:50:37

### Fixed

- Utah EITC reform.

## [1.442.0] - 2025-11-26 09:56:33

### Added

- Integrate California alternative minimum tax (AMT) into CA income tax calculation.

## [1.441.3] - 2025-11-26 09:54:55

### Added

- Regression test for AMT calculation against TAXSIM35 (issue

## [1.441.2] - 2025-11-26 09:48:01

### Changed

- Split AMT exemption calculation into separate `amt_exemption` variable from `amt_income_less_exemptions`.

## [1.441.1] - 2025-11-25 20:18:51

### Fixed

- Add missing defined_for=StateCode.MA to ma_state_supplement, fixing bug where non-MA households received Massachusetts State Supplement.

## [1.441.0] - 2025-11-25 11:22:31

### Added

- is_federal_work_study_participant.
- is_part_time_college_student.

### Changed

- Refactor is_snap_ineligible_student to include part-time students and Federal Work Study exception.
- Update snap_countable_earner to exclude Federal Work Study income.

## [1.440.1] - 2025-11-25 11:02:51

### Fixed

- Adjust Colorado Care Worker credit parameter file names .

## [1.440.0] - 2025-11-25 05:59:26

### Added

- Utah refundable EITC contributed reform.

## [1.439.1] - 2025-11-24 01:28:19

### Changed

- Remove deprecated 'name' metadata field from 51 parameter files

## [1.439.0] - 2025-11-24 00:10:07

### Added

- Added 2018 income limit for optional senior or disabled pathway, changed dates to match with given reference.

## [1.438.1] - 2025-11-23 10:18:53

### Fixed

- Adjust the New Jersey CDCC to apply the actual federal CDCC instead of the potential.

## [1.438.0] - 2025-11-23 09:45:04

### Added

- Puerto Rico income tax.

## [1.437.0] - 2025-11-23 09:22:55

### Added

- Added 2026 base SLCSP values for all rating areas.

## [1.436.0] - 2025-11-22 01:36:58

### Added

- Colorado Care Worker Tax Credit.

## [1.435.1] - 2025-11-21 23:46:56

### Fixed

- Fix SSI spousal deeming to correctly use couple FBR instead of individual FBR.

## [1.435.0] - 2025-11-17 23:19:37

### Fixed

- Restructure Tlaib package

## [1.434.0] - 2025-11-17 16:29:28

### Added

- Rhode Island CTC young child boost.

## [1.433.0] - 2025-11-13 23:38:52

### Added

- Working Pennsylvanians Tax Credit.

## [1.432.9] - 2025-11-13 15:46:53

### Fixed

- Limit the Hawaii CDCC to households with at least one qualifying dependent .

## [1.432.8] - 2025-11-11 19:02:22

### Changed

- Revert age heterogeneity in labor supply response elasticities (v1.426.0).

## [1.432.7] - 2025-11-11 14:47:06

### Fixed

- Fix vectorization bugs in Lifeline, CA CARE, and Pell Grant eligibility causing incorrect categorical eligibility

## [1.432.6] - 2025-11-11 13:40:35

### Fixed

- Remove the repeal of the Hawaii alternative tax on capital gains.

## [1.432.5] - 2025-11-10 19:14:05

### Added

- Debug income security package.

## [1.432.4] - 2025-11-10 13:54:57

### Fixed

- Fix Head Start categorical eligibility vectorization bug causing incorrect benefits at high incomes

## [1.432.3] - 2025-11-10 11:57:39

### Changed

- Fix Head Start and Early Head Start variable metadata (add unit=USD, simplify labels)

## [1.432.2] - 2025-11-10 11:36:20

### Fixed

- Apply the potential federal CDCC when computing the Ohio CDCC.

## [1.432.1] - 2025-11-09 20:09:40

### Fixed

- Avoid removing older dependents from the Rhode Island exemption reform.

## [1.432.0] - 2025-11-07 23:12:15

### Added

- Virginia 2024 income tax rebate.

## [1.431.0] - 2025-11-07 23:08:43

### Added

- Puerto Rico tax computation.

## [1.430.0] - 2025-11-06 17:14:20

### Added

- Georgia Itemizer Tax Credit.

## [1.429.0] - 2025-11-06 17:11:46

### Fixed

- Fixed typo in tanf and snap parameter folders.

## [1.428.0] - 2025-10-31 17:27:49

### Added

- Federal TANF baseline infrastructure for simplified state implementations.

## [1.427.0] - 2025-10-31 00:57:16

### Added

- Fix Rhode Island Dependent Exemption to Match Model.

## [1.426.0] - 2025-10-28 20:44:10

### Added

- Age heterogeneity in labor supply response elasticities using multiplier approach.

## [1.425.7] - 2025-10-28 14:08:51

### Fixed

- Fix recursion errors when applying LSRs.

## [1.425.6] - 2025-10-25 22:24:57

### Changed

- Restructure PR CI workflow to run selective tests (with coverage) and full test suite in parallel for faster feedback and comprehensive validation.

## [1.425.5] - 2025-10-24 01:02:40

### Added

- Changed name of aca_ptc_phase_out_rate to aca_required_contribution_percentage to better reflect its purpose.

## [1.425.4] - 2025-10-22 20:34:02

### Fixed

- Rhode Island exemption reform now correctly applies baseline phase-out to personal exemptions at high incomes

## [1.425.3] - 2025-10-22 14:06:11

### Fixed

- Fix the baby bonus act payment test.

## [1.425.2] - 2025-10-22 12:30:35

### Fixed

- Fix contributed test cases.

## [1.425.1] - 2025-10-22 12:00:48

### Fixed

- CTC per-child phase-out reform to avoid double-counting when regular and ARPA phase-outs overlap.

## [1.425.0] - 2025-10-22 03:08:12

### Added

- 2026 IRS tax parameters from Revenue Procedure 2025-32 (standard deduction, tax brackets, EITC, AMT, CTC, capital gains, QBI phase-out, student loan interest deduction, aged/blind additional).
- Automatic uprating with statutory rounding rules for parameters that previously had no post-2025 values (tax brackets 1-2, retirement contributions, capital gains thresholds).
- Statutory rounding rules to parameters with uprating but no rounding (QBI phase-out).
- Actual BLS CPI data through August 2025 (C-CPI-U, CPI-U, CPI-W).

### Changed

- Replaced manual CBO forecast values (2027-2035) with automatic uprating for tax brackets 3-6, standard deduction, AMT exemption, AMT phase-out, aged/blind additional deduction, CTC base amount, and CTC refundable maximum.
- Replaced OBBB legislative references with permanent IRC statutory sections.
- Split capital_gains/brackets.yaml into separate rates.yaml and thresholds.yaml files.

### Fixed

- Corrected previously incorrect 2026 QBI phase-out threshold forecast values.

## [1.424.6] - 2025-10-21 17:40:03

### Fixed

- Do not allow for an additional exemption for head of household filers under the Kansas food sales tax credit.

## [1.424.5] - 2025-10-21 14:40:37

### Fixed

- Use cdcc_relevant_expenses in the South Carolina CDCC calculation.

## [1.424.4] - 2025-10-21 14:34:10

### Fixed

- Avoid double counting the unemployment compensation in the New Mexico modified gross income.

## [1.424.3] - 2025-10-21 14:28:43

### Fixed

- Include business income in the earned income concept for the Georgia retirement income exclusion.

## [1.424.2] - 2025-10-21 14:09:42

### Fixed

- Avoid negative Wisconsin married couple credit amounts.

## [1.424.1] - 2025-10-20 23:22:57

### Fixed

- Fix us itemization integration tests which were failing due to a new Illinois income tax rebate.

## [1.424.0] - 2025-10-20 21:00:28

### Added

- Rhode Island Child Tax Credit reforms.

## [1.423.4] - 2025-10-20 19:43:44

### Fixed

- Allow for the Colorado sales tax refund for filers with negative income .

## [1.423.3] - 2025-10-20 15:35:19

### Fixed

- Add taxable unemployment compensation to the list of California subtractions.

## [1.423.2] - 2025-10-20 14:35:58

### Fixed

- Minnesota child and working families credits child tax credit eligible child definition.

## [1.423.1] - 2025-10-19 23:10:23

### Added

- Hawaii ACT 115 rebate.
- Illinois income tax rebate.
- Maine relief rebate.
- Massachusetts taxpayer refund rebate.
- South Carolina 2022 rebate.
- Indiana automatic refund rebate.
- Colorado Tabor cash back.

### Fixed

- Apply state income tax rebates in the tax year rather than the payment year.

## [1.423.0] - 2025-10-19 09:34:25

### Added

- CTC per-child phase-out reform now includes avoid_overlap parameter to prevent double-counting when regular and ARPA phase-outs overlap.

## [1.422.0] - 2025-10-19 05:12:39

### Added

- Texas Child Care Services (CCS) program.

## [1.421.0] - 2025-10-18 17:49:59

### Added

- Texas Commodity Supplemental Food Program fpg limit.

## [1.420.0] - 2025-10-18 00:00:49

### Added

- Texas Lifeline fpg limit and supplement.

## [1.419.0] - 2025-10-17 22:13:09

### Added

- Texas TANF.

## [1.418.0] - 2025-10-17 21:50:35

### Added

- Texas Harris County RIDES program.

## [1.417.3] - 2025-10-17 19:20:53

### Fixed

- Fix the in_nyc vectorization issue.

## [1.417.2] - 2025-10-17 19:09:38

### Fixed

- Updated ACA reform to start in 2026.

## [1.417.1] - 2025-10-17 17:24:13

### Fixed

- Fix the income_security_package reform to apply the reform conditionally on the reform parameters.

## [1.417.0] - 2025-10-16 13:32:23

### Added

- Texas Family Planning Program

## [1.416.0] - 2025-10-15 15:31:19

### Added

- Adjust the ctc_value as part of the minimum refundable CTC reform.

## [1.415.0] - 2025-10-15 15:30:29

### Added

- NYC formula.

## [1.414.0] - 2025-10-15 14:45:38

### Added

- Rep. Rashida Tlaib Income Security Package.

## [1.413.3] - 2025-10-14 02:23:12

### Fixed

- Fix typo in Ohio modified AGI filename (oh_modifed_agi.py to oh_modified_agi.py)

## [1.413.2] - 2025-10-14 02:16:57

### Fixed

- Adjust the Louisiana non refundable CDCC to base it on actual and not potential credit amounts.

## [1.413.1] - 2025-10-14 02:06:24

### Fixed

- Adjust the PA tax forgiveness rate to use is_child_dependent.
- Remove the name metadata tag from the PA parameter system.

## [1.413.0] - 2025-10-09 22:40:48

### Added

- FY 2026 SMI values.

## [1.412.0] - 2025-10-09 22:32:59

### Added

- Federal poverty guidelines for 2015 and 2016 to support WIC calculations back to 2015.

## [1.411.0] - 2025-10-09 16:59:51

### Added

- ACA PTC additional bracket reform allowing custom contribution rate schedules by income level
- ACA PTC simplified bracket reform with linear phase-out starting at 100% FPL

## [1.410.0] - 2025-10-06 14:13:11

### Added

- Massachusetts Child Care Financial Assistance (CCFA).

## [1.409.0] - 2025-10-05 21:01:54

### Added

- New benchmark_premium_uprating parameter based on KFF historical SLCSP data (2014-2025)

### Changed

- Switch SLCSP uprating from Chained CPI-U to empirical benchmark premium growth rate of 4.3%
- Replace CRS references with IRS Revenue Procedures in ACA premium tax credit parameters
- Spell out acronyms in parameter descriptions (ACA, PTC, MAGI, FPL, SLCSP)

## [1.408.1] - 2025-10-04 04:24:45

### Fixed

- Vectorization of the CTC refundable maximum reform.

## [1.408.0] - 2025-10-03 08:08:20

### Added

- Update New Mexico personal income tax rate schedules for TY2025 per HB 252 (2024).

## [1.407.4] - 2025-10-02 21:05:58

### Added

- CTC reform integration tests.

### Fixed

- Typo in the ctc per child phase-in reform and
- Minimum refundable CTC reform logic.

## [1.407.3] - 2025-10-01 16:40:26

### Fixed

- Include partnership/S-corp income and farm income in Alabama gross income.

## [1.407.2] - 2025-09-30 19:59:15

### Fixed

- Apply the 5 year look back to the CTC reforms.

## [1.407.1] - 2025-09-30 19:58:04

### Added

- NY CTC 2027 bug fix.

## [1.407.0] - 2025-09-27 17:53:20

### Added

- CTC per child phase-in reform.
- CTC minimum refundable amount reform.
- CTC per child phase-out reform.

## [1.406.0] - 2025-09-26 15:55:30

### Added

- School meal subsidies 2024 and 2025 parameter updates.

## [1.405.0] - 2025-09-25 20:33:35

### Fixed

- Adjust the `state_agi` variable to reflect states that adopt federal AGI.

## [1.404.1] - 2025-09-25 20:18:49

### Fixed

- Improved test batching to avoid memory issues and reduce test duplication.
- Split baseline tests into separate batches for household and contrib folders.

## [1.404.0] - 2025-09-25 08:20:22

### Added

- Texas Dallas Area Rapid Transit (DART) reduced fare program.

### Fixed

- Don't publish to PyPI on push without passing tests.

## [1.403.2] - 2025-09-24 15:23:57

### Fixed

- Montana married filing jointly subtractions allocation issue.
- Rename mt_agi to mt_agi_indiv.

## [1.403.1] - 2025-09-24 00:54:25

### Fixed

- Increase the tolerance for itemization comparison.

## [1.403.0] - 2025-09-23 22:51:10

### Added

- Update SNAP parameters for FY 2026 Cost-of-Living Adjustments.

## [1.402.3] - 2025-09-23 22:49:31

### Fixed

- Adjust the Oklahoma child care/ child tax credit to use the actual CTC value, not the potential.

## [1.402.2] - 2025-09-23 22:47:11

### Fixed

- Reform tests related to social security taxation.

## [1.402.1] - 2025-09-22 21:29:46

### Fixed

- Connecticut and Montana federal social security tax parameter dependencies.

## [1.402.0] - 2025-09-22 20:32:00

### Added

- California state-funded Medicaid eligibility for undocumented immigrants with age-based phase-in from 2016-2024.

## [1.401.0] - 2025-09-22 18:07:07

### Added

- Separated Social Security taxation parameters to match each statutory percentage independently

### Changed

- Refactored Social Security taxation formula to use properly separated parameters per IRC Section 86

## [1.400.2] - 2025-09-19 20:09:46

### Fixed

- Default itemization to be based on state deductions when federal tax liability is equal.
- Compute state itemized and standard deductions for states that adopt the federal itemized and standard deductions.
- Account for the married filing separately structure in the state itemized and standard deductions.
- Adopt a parallel Montana federal tax deduction for federal itemization purposes.

## [1.400.1] - 2025-09-18 16:41:32

### Fixed

- Minnesota CDCC structure.

## [1.400.0] - 2025-09-18 16:40:36

### Added

- New Mexico 2024 low income tax rebate amounts.

## [1.399.1] - 2025-09-17 17:11:17

### Fixed

- New Jersey other retirement income exclusion calculation.

## [1.399.0] - 2025-09-17 15:33:26

### Added

- Puerto Rico exemptions.

## [1.398.1] - 2025-09-15 22:28:43

### Fixed

- Remove the self-employment income deduction from the SNAP deductions list.

## [1.398.0] - 2025-09-11 11:13:17

### Added

- Refactor the CTC phase-in relevant earnings.

## [1.397.2] - 2025-09-11 01:02:51

### Fixed

- Michigan integration test.

## [1.397.1] - 2025-09-10 23:55:47

### Fixed

- Refactor the CTC phase-in relevant earnings.

## [1.397.0] - 2025-09-10 10:36:26

### Added

- Include missing non-refundable credits in state non-refundable credits list.

## [1.396.0] - 2025-09-09 23:54:52

### Added

- Michigan 2024 home heating credit rate.

## [1.395.2] - 2025-09-09 22:03:48

### Fixed

- Social Security taxation formula now uses a separate parameter for combined income calculation instead of incorrectly reusing the base taxation rate

## [1.395.1] - 2025-09-05 20:35:09

### Fixed

- Add the qualified business income deduction to the list of additions in South Carolina.

## [1.395.0] - 2025-09-05 15:45:41

### Added

- Reform to extend senior deduction beyond 2028.

## [1.394.0] - 2025-09-05 09:32:44

### Fixed

- Adjusted run_selective_tests.py to improve test discovery.

## [1.393.0] - 2025-09-05 09:29:37

### Fixed

- Adjusted New York CTC calculations pre 2025.

## [1.392.0] - 2025-09-04 22:44:50

### Added

- Vermont child care contributions.

## [1.391.1] - 2025-09-04 20:41:18

### Fixed

- Minnesota child tax credit amount and phase-out thresholds uprating.

## [1.391.0] - 2025-09-04 09:30:12

### Added

- North Carolina Subsidized Child Care Assistance (SCCA) maximum payment variable.

### Fixed

- North Carolina Subsidized Child Care Assistance (SCCA) formula.

## [1.390.1] - 2025-09-04 09:23:57

### Fixed

- Fix the deductions if not itemizing list.

## [1.390.0] - 2025-09-03 17:50:49

### Added

- CRFB tax employer payroll tax reform with configurable percentage parameter

## [1.389.1] - 2025-09-03 17:02:51

### Changed

- Removed coverage tracking from push.yaml workflow to speed up master branch builds.
- Implemented selective test runner and coverage test for PR workflow to only test changed files.

## [1.389.0] - 2025-09-02 23:14:24

### Added

- Illinois Low Income Home Energy Assistance Program (LIHEAP)

## [1.388.0] - 2025-09-02 22:52:24

### Added

- California Riverside County General Relief Program.

## [1.387.3] - 2025-09-02 19:45:27

### Fixed

- Adjust the Montana 2024 capital gains tax.

## [1.387.2] - 2025-09-02 19:32:13

### Fixed

- Apply a floor to the Michigan household resources.

## [1.387.1] - 2025-09-02 18:08:37

### Fixed

- Apply a floor to the Michigan household resources.

## [1.387.0] - 2025-09-02 15:09:34

### Added

- Arkansas additional tax credit for qualified individuals.

### Fixed

- Arkansas 2024 income tax rates.

## [1.386.1] - 2025-09-01 22:58:34

## [1.386.0] - 2025-08-31 11:40:22

### Added

- Adjust the IED calculation to use FPG adjusted in March.

## [1.385.1] - 2025-08-30 18:43:46

### Added

- Georgia surplus tax rebate.

### Fixed

- Backdate the Georgia tax rates to 2021.

## [1.385.0] - 2025-08-30 16:08:36

### Added

- Adjust the IED calculation to use FPG adjusted in March.

## [1.384.0] - 2025-08-29 20:56:57

### Fixed

- Illinois TANF FPG calculation adjustments.

## [1.383.0] - 2025-08-29 16:29:36

### Added

- congressional_district_geoid variable to replace the congressional district portion of the removed UCGID concept

## [1.382.0] - 2025-08-29 14:50:10

### Added

- Idaho 2022 rebate.
- Idaho special seasonal rebate.

## [1.381.3] - 2025-08-29 06:00:04

### Added

- Fix Maine Property Tax Fairness Credit Veteran Cap.

## [1.381.2] - 2025-08-29 01:04:56

### Fixed

- Updated push.yaml to fix workflow hanging issue with PYTHONUNBUFFERED=1 and uv virtual environment

## [1.381.1] - 2025-08-28 14:57:49

### Added

- Memory-optimized test execution scripts for baseline and contrib tests
- Batch processing with periodic memory cleanup to prevent OOM errors

### Fixed

- Python path detection in test scripts for compatibility across environments

## [1.381.0] - 2025-08-28 03:53:01

### Added

- Enhanced multi-agent system for autonomous benefit program implementations
- New agents for issue management, naming coordination, and branch integration
- Improved workflow documentation with @ syntax for agent invocation

### Changed

- Updated agent workflow to establish naming conventions before parallel development
- Modified CI fixer to work with existing draft PRs
- Enhanced test creator and rules engineer to work in separate git worktrees

## [1.380.0] - 2025-08-28 02:26:40

### Added

- Multi-agent system for autonomous code review and implementation
- 13 specialized agents for validation, implementation, and enhancement
- /encode-policy command for implementing new government programs with TDD
- /review-pr command for reviewing and fixing PRs with mandatory agent usage
- Comprehensive documentation for agent coordination and testing

## [1.379.0] - 2025-08-26 19:32:44

### Added

- Add a state non-refundable credits variable.

## [1.378.0] - 2025-08-26 15:31:43

### Added

- Multi-agent development system for accurate program implementation
- Supervisor agent for orchestrating isolated development workflow
- Document collector agent for gathering authoritative sources
- Test creator agent for building tests from documentation
- Rules engineer agent for TDD-based implementation
- Verifier agent for comprehensive validation
- Shared PolicyEngine standards document for consistency

## [1.377.1] - 2025-08-25 19:37:04

### Fixed

- Avoid negative subtractions from acting as additions.

## [1.377.0] - 2025-08-25 18:03:27

### Fixed

- Fixed IL AABD integration tests.

## [1.376.4] - 2025-08-25 13:45:00

### Fixed

- Tenant pays rent variable for HUD utility allowance calculation.

## [1.376.3] - 2025-08-25 13:09:42

### Fixed

- Updated SSI-related test cases.
- Updated SSI-related variables.

## [1.376.2] - 2025-08-25 02:14:31

### Fixed

- Exclude SSI recipients from NC TANF household count.

## [1.376.1] - 2025-08-21 21:00:04

### Fixed

- Fix pre-2024 NY CTC.

## [1.376.0] - 2025-08-21 17:38:20

### Added

- Added 2018 medicaid income limits for parents.

## [1.375.0] - 2025-08-21 08:05:30

### Added

- Georgia 2026 CTC.
- Georgia CDCC Match 2025.

## [1.374.1] - 2025-08-20 14:15:57

### Fixed

- Fix charitable deduction floor amount parameter.
- Fix non-cash charitable deduction ceiling.

## [1.374.0] - 2025-08-20 13:41:01

### Added

- California Alameda County General Assistance Program.

## [1.373.1] - 2025-08-19 21:31:19

### Fixed

- Fix AMT Phaseout Rate.

## [1.373.0] - 2025-08-19 07:41:21

### Added

- Refundable Additional Child Tax Credit (ACTC) for Puerto Rico.

## [1.372.0] - 2025-08-19 07:18:50

### Added

- Unified programmatic extension of all uprating factors through 2100 for long-term policy simulations
- IRS, SNAP, SSA, HHS, CPI-U, Chained CPI-U, and CPI-W now extend dynamically based on growth rates from final years of projections
- Single comprehensive test suite for all uprating extensions
- Cleaner, more maintainable approach that avoids hardcoding future values in YAML files

### Changed

- Updated SSA 2025 value to reflect actual 2.5% COLA announced by SSA
- Refactored all uprating extensions from hardcoded YAML values to programmatic generation

## [1.371.0] - 2025-08-18 14:16:48

### Fixed

- Correct SSI benefit amount for dependent children to use individual rate.
- Fix SSI joint claim determination to properly identify eligible married couples.

## [1.370.2] - 2025-08-18 11:43:57

### Fixed

- Dropped requirement for us-data.

## [1.370.1] - 2025-08-13 01:10:42

### Fixed

- Remove the senior deduction neutralization part of the CRFB SS credit.

## [1.370.0] - 2025-08-12 19:49:31

### Added

- Add the CRFB SS credit to the net income tree.

## [1.369.0] - 2025-08-11 01:53:29

### Added

- Head Start and Early Head Start programs payout.
- Add HHS CPI-U data for 2022 and 2023.

## [1.368.0] - 2025-08-10 22:52:19

### Added

- CRFB Nonrefundable Credit for Social Security Taxes.

## [1.367.0] - 2025-08-08 21:18:49

### Added

- Add new Medicaid immigration restrictions from OBBBA.

## [1.366.2] - 2025-08-07 12:54:07

### Fixed

- Fix Hawley rebate to get impacts in years other than 2025.

## [1.366.1] - 2025-08-07 12:51:20

### Added

- Blind SGA parameter & 2025 value

### Changed

- Updated SSI 2025 non-blind SGA parameter value.
- Updated SSI 2025 student income exclusion amount and cap parameter values.

## [1.366.0] - 2025-08-06 20:43:30

### Added

- 2025 Virginia income tax changes.

## [1.365.2] - 2025-08-06 20:24:41

### Fixed

- Fix Maine Dependent Exemption Tax Credit.

## [1.365.1] - 2025-08-06 20:20:25

### Fixed

- Edit the formula of ucgid_str to return the ucgid hierarchical codes.

## [1.365.0] - 2025-08-04 21:22:30

### Added

- Michigan surtax ballot initiative.

## [1.364.0] - 2025-08-02 00:01:59

### Fixed

- Adjustment in meets_snap_abawd_work_requirements formula.

## [1.363.1] - 2025-08-01 23:41:54

### Fixed

- Cap the North Carolina Subsidized Child Care Assistance Program benefit amount at pre_subsidy_childcare_expense.

## [1.363.0] - 2025-08-01 22:07:50

### Added

- Default to first alphabetical county in state when county is not specified.

## [1.362.1] - 2025-07-31 23:59:46

### Fixed

- Disable Montana married filing separately on same return logic past 2024.

## [1.362.0] - 2025-07-31 23:48:33

### Added

- 2018 medicaid older children income limits.

## [1.361.0] - 2025-07-31 22:20:59

### Added

- Exempt income from children in school from SNAP.

## [1.360.1] - 2025-07-31 22:16:19

### Fixed

- Corrected income tax thresholds for low-income Arkansas tax tables.

## [1.360.0] - 2025-07-31 13:59:29

### Added

- DC General Assistance for Children (GAC).
- DC TANF work requirements.
- DC Program on Work, Employment, and Responsibility (POWER).

### Fixed

- Refactored formulas in accordance with TANF and GAC.

## [1.359.1] - 2025-07-31 12:15:15

### Fixed

- Add build back back to pyproject.toml.

## [1.359.0] - 2025-07-31 09:28:58

### Added

- Vermont tax credit legislation changes

## [1.358.1] - 2025-07-30 23:20:43

### Changed

- Fixed how update_api.py retrieves the version number from pyproject.toml.

## [1.358.0] - 2025-07-30 22:55:21

### Added

- Sen. Hawley tariff rebate reform.

## [1.357.2] - 2025-07-30 10:45:15

### Fixed

- Fix reported SALT unit test.

## [1.357.1] - 2025-07-29 16:49:54

### Added

- Fix broken unit tests introduced through OBBBA parametric changes.

## [1.357.0] - 2025-07-29 13:28:50

### Added

- Update federal tax parameters following passage of HR 1.

## [1.356.0] - 2025-07-29 12:54:00

### Added

- Puerto Rico deductions.

## [1.355.0] - 2025-07-29 11:48:42

### Added

- Move OBBBA structural reforms to benefits to current policy.

## [1.354.0] - 2025-07-29 11:34:28

### Added

- Move OBBBA structural reforms to current policy.

## [1.353.0] - 2025-07-28 20:42:43

### Fixed

- Fix ca_state_supplement_dependent_amount formula.

## [1.352.1] - 2025-07-28 17:17:37

### Changed

- person_count variable.

## [1.352.0] - 2025-07-28 16:41:24

### Added

- ucgid variable.
- household_count variable.
- spm_unit_count variable.
- tax_unit_count variable.

## [1.351.5] - 2025-07-28 12:28:49

### Fixed

- Remove the second earner tax reform.

## [1.351.4] - 2025-07-27 23:15:44

### Fixed

- Remove spm_unit_income_decile test with zero weight.

## [1.351.3] - 2025-07-27 20:47:27

### Fixed

- Fix broken unit tests.

## [1.351.2] - 2025-07-25 16:57:30

### Fixed

- Default itemization turned off for tests.

## [1.351.1] - 2025-07-25 02:23:14

### Added

- Added Documentation page for Medicaid and ACA.

## [1.351.0] - 2025-07-24 22:52:03

### Added

- Update FY2025 HHS SMI parameter.

## [1.350.1] - 2025-07-24 18:37:29

### Fixed

- Move healthcare simulation parameter to the correct simulation folder.

## [1.350.0] - 2025-07-23 13:54:32

### Added

- SNAP self-employment simplified deductions.

## [1.349.3] - 2025-07-23 11:09:36

### Changed

- Improved file naming consistency by renaming generic filenames to match their variable names
- Split files containing multiple variables into separate files following one-variable-per-file standard
- Fixed typos in filenames (e.g., "if_tanf" to "il_tanf" for Illinois)
- Removed space from filename "il _cta_reduced_fare_program.py"

### Fixed

- Fixed household_income_decile test structure to properly place household variables under household entity

## [1.349.2] - 2025-07-23 02:05:22

### Added

- Support for Python 3.13

### Changed

- Updated policyengine-core dependency to >=3.19.0 for Python 3.13 support

## [1.349.1] - 2025-07-22 21:06:21

### Changed

- Update microdf-python dependency to >=1.0.0.

## [1.349.0] - 2025-07-22 20:02:01

### Added

- Puerto Rico earned income credit (EITC).

## [1.348.1] - 2025-07-22 15:55:01

### Added

- Updated microdf-python to 0.4.5.

## [1.348.0] - 2025-07-22 14:20:17

### Added

- California Riverside County Low-Income Home Energy Assistance Program (LIHEAP).

## [1.347.0] - 2025-07-18 21:16:46

### Added

- DC Child Care Subsidy Program (CCSP).

## [1.346.0] - 2025-07-18 17:53:21

### Added

- Added simulation parameter to add healthcare toggle to net income calculations.

## [1.345.0] - 2025-07-18 02:51:20

### Added

- DC Low-Income Home Energy Assistance Program (LIHEAP).

## [1.344.0] - 2025-07-17 20:08:55

### Added

- Maine Dependent Exemption Credit 2025.

## [1.343.0] - 2025-07-16 21:48:52

### Added

- Cap each federal non-refundable credit at its limit based on tax liability.

## [1.342.1] - 2025-07-16 20:15:06

### Fixed

- Remove net investment income from the Alabama federal tax deduction.

## [1.342.0] - 2025-07-16 10:45:47

### Fixed

- Update 2018 CHIP child income limit for KS, KY, ME, NC and ND.

## [1.341.1] - 2025-07-12 15:05:55

### Fixed

- Test efficiency.

## [1.341.0] - 2025-07-12 04:17:24

### Added

- Ohio flat tax 2025-2026.

## [1.340.1] - 2025-07-11 19:23:54

### Added

- Added DACA and TPS as unique immigration statuses, without removing the existing combined status.

## [1.340.0] - 2025-07-11 14:20:30

### Changed

- Itemization choice respects federal not fed+state tax.

## [1.339.1] - 2025-07-11 11:07:35

## [1.339.0] - 2025-07-11 01:14:11

### Added

- Riverside County Sharing Households Assist Riverside's Energy program (SHARE).

## [1.338.0] - 2025-07-09 15:06:36

### Added

- Set default to true for branching to determine itemization choice.

## [1.337.0] - 2025-07-08 18:56:37

### Added

- 2018 maximum income for young children and pregnant people to qualify for medicaid

## [1.336.1] - 2025-07-08 18:03:44

### Fixed

- Add 2009 surviving spouse itemized deduction reduction rate.

## [1.336.0] - 2025-07-08 16:02:27

### Added

- added 2018 maximum family income for adults to qualify for medicaid

## [1.335.0] - 2025-07-07 18:44:33

### Added

- added 2018 maximum family income for infants to qualify for medicaid

## [1.334.0] - 2025-07-03 00:50:54

### Added

- Senate reconciliation bill charitable deduction reform.

## [1.333.0] - 2025-07-02 18:07:05

### Added

- Add Senate Medicaid work requirement reform.
- Consolidate House and Senate Medicaid work requirement reform.

## [1.332.0] - 2025-07-02 17:21:26

### Added

- Align market income sources with IRS gross income sources.

## [1.331.0] - 2025-07-02 13:44:03

### Added

- Move Senate auto loan interest deduction below the line.

## [1.330.0] - 2025-07-01 21:43:21

### Added

- SNAP work requirements.
- Reconciliation SNAP work requirements reform.

## [1.329.0] - 2025-07-01 11:26:13

### Added

- Apply Maryland 2025 Budget Changes.

## [1.328.0] - 2025-06-30 19:04:17

### Added

- Reconciled Medicaid work requirement reform.

## [1.327.6] - 2025-06-30 17:22:33

### Fixed

- Rhode Island 2024 income tax rate update.
- Rhode Island 2024 exemption phase-out start.

## [1.327.5] - 2025-06-30 16:42:51

### Fixed

- Only subtract taxable pension income from Hawaii AGI.
- Hawaii single and separate income tax rates.

## [1.327.4] - 2025-06-30 16:31:07

### Fixed

- Exclude non-mortgage interest from the California itemized deduction AGI limitation.

## [1.327.3] - 2025-06-30 16:07:26

### Fixed

- Nebraska 2024 income tax brackets.

## [1.327.2] - 2025-06-30 14:44:18

### Fixed

- Senate Finance Tip and Overtime income reforms.

## [1.327.1] - 2025-06-30 14:36:28

### Fixed

- Oregon retirement income credit formula.

## [1.327.0] - 2025-06-26 16:53:09

### Added

- Business development company income and expanded QBID calculation tests.

### Changed

- Refactored qualified business income deduction logic with wage and property limitations.

## [1.326.0] - 2025-06-26 14:45:33

### Added

- Additional tax bracket reform.

## [1.325.0] - 2025-06-26 12:13:18

### Added

- Consolidated medicaid and medicaid per capita into medicaid cost.

## [1.324.0] - 2025-06-25 19:13:43

### Added

- Fix Medicaid eligibility rules for senior and disabled.

## [1.323.0] - 2025-06-25 11:14:33

### Changed

- Make WIC monthly.

## [1.322.0] - 2025-06-24 18:26:56

### Added

- New York supplemental income tax recapture base.

## [1.321.1] - 2025-06-23 15:57:50

### Fixed

- Use adjusted gross income instead of taxable income in the Kansas zero tax computation.

## [1.321.0] - 2025-06-20 18:16:25

### Added

- Add the New York inflation rebates as a refundable tax credit.

## [1.320.0] - 2025-06-20 15:28:51

### Added

- Senate Finance Child and Dependent Care Credit.

## [1.319.0] - 2025-06-20 14:44:55

### Added

- Update New York CTC for 2025-2027 based on Senate Bill S.3009-C.

## [1.318.0] - 2025-06-20 00:21:33

### Added

- Exemptions for flat tax on AGI.

## [1.317.0] - 2025-06-20 00:08:06

### Added

- Senate Finance CTC SSN Requirement.

## [1.316.0] - 2025-06-19 23:53:40

### Added

- Senate Finance QBID.

## [1.315.0] - 2025-06-19 14:23:44

### Added

- Senate Finance Overtime income exemption.
- Senate Finance Tip income exemption.

## [1.314.2] - 2025-06-17 15:56:52

### Fixed

- Bug causing some microsimulations to break.

## [1.314.1] - 2025-06-17 13:52:07

### Fixed

- 2023 datasets are passed into the wrong time periods.

## [1.314.0] - 2025-06-16 20:42:21

### Added

- Oklahoma Income Tax Changes 2026.

## [1.313.0] - 2025-06-12 15:51:05

### Added

- New York supplemental income tax changes.

## [1.312.3] - 2025-06-12 13:16:09

### Added

- Integration tests for TANF to verify state implementations work correctly.
- Documentation in CLAUDE.md about period handling and state program refactoring.

### Changed

- Use defined_for and p = parameters(...) more consistently.
- Refactored TANF to sum only state-specific implementations, removing federal calculation.

### Fixed

- TANF tests to correctly require eligibility for receiving benefits.
- Lifeline benefit calculation by changing tuple assignment to addition.
- Demographic TANF eligibility to use period.this_year for age calculation.
- Demographic TANF eligibility to check is_in_secondary_school instead of is_full_time_student for student age limits.

## [1.312.2] - 2025-06-11 22:42:29

### Fixed

- Another ACA issue.

## [1.312.1] - 2025-06-11 22:17:44

### Fixed

- Bug in ACA calculations.

## [1.312.0] - 2025-06-11 19:46:07

### Added

- Add take-up flags for Medicaid, CHIP and ACA PTC.

## [1.311.0] - 2025-06-11 19:21:56

### Fixed

- Fix slcsp_rating_area_la_county parameter.

## [1.310.0] - 2025-06-11 19:06:16

### Added

- SNAP take-up seed variable.

## [1.309.1] - 2025-06-10 13:31:01

### Fixed

- Connecticut period in the head of household tax rate.

## [1.309.0] - 2025-06-09 10:36:28

### Added

- Unit tests for labor supply response variables focusing on negative earnings scenarios
- Tests for substitution elasticity with negative total earnings
- Tests for employment income allocation with negative earnings

### Changed

- Refactored labor supply response module into individual variable files for better organization
- Applied consistent code style patterns across all labor supply response variables
- Improved parameter access patterns and income combination methods

### Fixed

- Fixed negative self-employment income causing counterintuitive labor supply response sign flips
- Labor supply responses now properly handle negative total earnings by clipping to zero

## [1.308.0] - 2025-06-07 20:44:11

### Added

- Massachusetts Low-Income Home Energy Assistance Program (LIHEAP).

## [1.307.1] - 2025-06-07 13:10:54

### Changed

- In microsim contexts, modified county to prefer ZCTA-based counties over FIPS-based counties in all cases, including when FIPS is defined.

## [1.307.0] - 2025-06-06 20:46:21

### Fixed

- Fix DC TANF child care deduction formula.

## [1.306.0] - 2025-06-06 17:42:13

### Added

- Illinois Aid to the Aged, Blind or Disabled (AABD).

## [1.305.0] - 2025-06-05 15:55:00

### Added

- Illinois Temporary Assistance for Needy Families (TANF).

## [1.304.0] - 2025-06-05 13:44:56

### Added

- Update the California State Supplement 2025 values.

## [1.303.0] - 2025-06-05 13:19:06

### Added

- Add default value of 40 to ssi_qualifying_quarters_earnings.

## [1.302.0] - 2025-06-03 13:33:39

### Added

- Net worth variables (to compare imputation method impacts on policy results).

## [1.301.0] - 2025-06-01 08:18:11

### Added

- Illinois Child Care Assistance Program (CCAP).

## [1.300.0] - 2025-05-30 21:36:49

### Added

- Refugee status to the CA TANF and ChildCare eligibility criteria.

## [1.299.1] - 2025-05-30 16:31:37

### Fixed

- Adjust the ACTC additional bracket parameter label / description, and add support for multiple periods.

## [1.299.0] - 2025-05-30 14:18:59

### Added

- Qualified BDC dividend income variable
- Qualified REIT and PTP income variable
- Farm operations income variable
- Variables showing whether income types would be qualified business income (estate, farm operations, farm rent, partnership/S corp, rental, self employment)
- Parameter for sources of QBI deductions (deduction_definition.yaml)
- QBID reconciliation parameters (in_effect, phase_out_rate, use_bdc_income)
- Marginal tax rate including health benefits variable
- Tax code references to income variables where they were missing

### Changed

- marginal_tax_rate and marginal_tax_rate_including_health_benefits now use emp_self_emp_ratio with no logic change

## [1.298.0] - 2025-05-30 06:47:16

### Added

- Additional CTC bracket reform.

## [1.297.2] - 2025-05-28 01:47:22

### Fixed

- auto loan variables uprating path

## [1.297.1] - 2025-05-27 23:07:51

### Changed

- Add uprating for base ACA premiums.

## [1.297.0] - 2025-05-27 22:24:56

### Added

- CalWorks TANF and Child Care immigration status eligibility.

## [1.296.0] - 2025-05-27 21:44:24

### Added

- New York 2026 budget agreement income tax provisions.

## [1.295.1] - 2025-05-27 21:39:46

### Fixed

- Corrected Vermont's per capita Medicaid spending.

## [1.295.0] - 2025-05-27 14:19:05

### Added

- Hours worked last week variable.

## [1.294.0] - 2025-05-27 13:30:38

### Added

- Add uprating for auto loan balance and interest variables.

## [1.293.0] - 2025-05-26 17:53:02

### Added

- Illinois Chicago Transit Authority Programs benefit amount.

## [1.292.0] - 2025-05-25 23:40:18

### Added

- Update WIC values.

## [1.291.0] - 2025-05-23 17:18:54

### Added

- Hours worked last week variable.

## [1.290.0] - 2025-05-23 16:51:32

### Added

- Created a new MTR and Post-transfer income that includes healthcare programs.

## [1.289.1] - 2025-05-22 20:54:55

### Fixed

- Auto Loan ALD formula.

## [1.289.0] - 2025-05-22 17:17:58

### Added

- Amended itemized deduction reform structure.

## [1.288.0] - 2025-05-22 00:32:21

### Added

- Apply identification requirement to CTC under current law for children.

## [1.287.2] - 2025-05-21 13:57:33

### Fixed

- Remove special characters causing imports to fail on Windows.

## [1.287.1] - 2025-05-20 23:30:36

### Fixed

- Add CHIP eligibility to per capita CHIP variable.

## [1.287.0] - 2025-05-20 08:25:19

### Added

- Overtime variables.

## [1.286.0] - 2025-05-20 01:13:06

### Added

- Add enrollment and costs of CHIP, Medicaid and the ACA.

## [1.285.0] - 2025-05-18 22:44:09

### Added

- 2024 Connecticut State Income Tax Updates.

## [1.284.0] - 2025-05-15 17:00:19

### Added

- Populate is_aca_eshi_eligible formula from ASEC inputs.

## [1.283.0] - 2025-05-14 22:19:43

### Added

- Update 2024 Vermont Income Tax Parameters.

## [1.282.2] - 2025-05-14 19:02:37

### Added

- Add new immigration rules to ACA reform.

### Fixed

- Adjust immigration formula on current ACA file.

## [1.282.1] - 2025-05-14 09:24:49

### Fixed

- Deductions in the tip and overtime income exempt reform.

## [1.282.0] - 2025-05-13 21:17:19

### Added

- Reform to require SSN for Lifetime Learning Credit and American Opportunity Credit.

## [1.281.0] - 2025-05-13 19:50:35

### Added

- Senior additional standard deduction phase-out reform.

## [1.280.1] - 2025-05-13 18:27:42

### Added

- Change SALT phase-out start to a smart-indexed from scale parameter.

### Fixed

- Apply SALT phase-out to the cap.

## [1.280.0] - 2025-05-13 18:10:36

### Added

- Auto loan balance variable.

## [1.279.1] - 2025-05-13 17:47:38

### Fixed

- Apply SALT phase-out to each filing status separately.

## [1.279.0] - 2025-05-13 15:09:35

### Added

- Add SSN requirement to reconciliation CTC reform.

## [1.278.0] - 2025-05-13 14:13:35

### Added

- Add SSN requirement to current EITC formula.

## [1.277.0] - 2025-05-13 13:15:11

### Added

- 2024 West Virginia Income Tax Changes.

## [1.276.0] - 2025-05-13 01:46:15

### Added

- 2024 Rhode Island Income Tax Updates.

## [1.275.0] - 2025-05-13 01:41:44

### Added

- Auto loan interest ALD reform.

## [1.274.1] - 2025-05-13 00:55:26

### Fixed

- Change charitable deduction for non-itemizers into an always-on zeroed-out deduction.

## [1.274.0] - 2025-05-13 00:39:59

### Added

- When not branching, compare itemized deductions with pease to all non-itemized deductions.

## [1.273.0] - 2025-05-13 00:26:34

### Added

- Add reform to exempt overtime and tip income as deductions.

## [1.272.1] - 2025-05-12 23:17:00

### Fixed

- Account for pease in the taxable_income_deductions_if_itemizing variable.

## [1.272.0] - 2025-05-12 20:41:49

### Added

- Reconciliation limitation on tax benefit of itemized deductions reform.

## [1.271.0] - 2025-05-12 19:49:10

### Added

- Option to apply a floor to the phased-out SALT deduction reform.

## [1.270.3] - 2025-05-12 18:42:29

### Fixed

- Update CBO projected Exemption parameters for Jan 2025 forecast.

## [1.270.2] - 2025-05-12 13:17:51

### Fixed

- Add itemization choice to taxable income before QBID.

## [1.270.1] - 2025-05-12 11:00:51

### Added

- Statutory sources to some federal tax variables.
- Historical Social Security earnings cap values.

### Changed

- Index SGA by NAWI instead of COLA.

## [1.270.0] - 2025-05-11 20:08:13

### Added

- 2026 Budget reconciliation QBID reform.

## [1.269.2] - 2025-05-10 00:18:36

### Fixed

- Add defined_for = "PR" to Puerto Rico variables.

## [1.269.1] - 2025-05-08 20:04:34

## [1.269.0] - 2025-05-08 18:34:30

### Added

- 2024 Nebraska State Income Tax Updates.

## [1.268.0] - 2025-05-08 18:28:51

### Added

- Illinois Chicago Transit Authority Reduced Fare and Free Ride Programs.

## [1.267.0] - 2025-05-08 18:22:05

### Added

- New York 2025 Inflation Rebates incremental phase out.

## [1.266.0] - 2025-05-07 20:46:30

### Added

- Create independent checks for the EAEDC and TAFDC values.

## [1.265.3] - 2025-05-07 14:14:46

### Changed

- Extended IRS uprating to 2035, inclusive.

## [1.265.2] - 2025-05-06 21:05:56

### Fixed

- Montana income tax uprating.

## [1.265.1] - 2025-05-06 19:13:10

### Added

- Added infant Medicaid ages and income Limits

## [1.265.0] - 2025-05-01 16:22:31

### Added

- Updated senior Medicaid parameters and adjusted variable to use percent of federal poverty.

## [1.264.1] - 2025-05-01 16:15:34

### Changed

- Fix 2024 SNAP parameters.
- Update 2025 SNAP parameters.

## [1.264.0] - 2025-04-30 20:06:54

### Added

- Puerto Rico gross income.

## [1.263.0] - 2025-04-30 20:00:26

### Added

- SNAP SUA for 2025
- SNAP LUA for 2025

## [1.262.1] - 2025-04-29 20:07:23

## [1.262.0] - 2025-04-28 20:12:23

### Added

- 2026-2027 Montana Income Tax Changes.

## [1.261.0] - 2025-04-28 17:09:00

### Added

- Limit reported SALT to the amount that would zero out regular tax liability.
- Create SALT and reported SALT variables.

## [1.260.0] - 2025-04-28 16:42:01

### Added

- Adjust ctc_value when activating fully refundable CTC.

## [1.259.0] - 2025-04-28 16:19:52

### Added

- Include taxable IRA distributions in market income.

## [1.258.4] - 2025-04-26 02:00:39

### Added

- 2025 Annual Update of the HHS Poverty Guidelines.

## [1.258.3] - 2025-04-25 22:07:31

### Fixed

- Default the MA EAEDC living arrangement to "A".
- Fix the MA EAEDC non-financial eligibility formula.

## [1.258.2] - 2025-04-25 19:32:44

### Fixed

- Fixed ACA PTC phase-out rate calculation to properly handle null values in parameter brackets

## [1.258.1] - 2025-04-25 18:05:47

### Fixed

- AFA reform maximum CTC amount adjustment.

## [1.258.0] - 2025-04-25 17:47:11

### Added

- Updated Montana's Tax Code for 2024.

## [1.257.0] - 2025-04-25 15:43:41

### Added

- Updated Delaware state tax code for 2024.

## [1.256.1] - 2025-04-25 14:31:40

### Fixed

- Adjust the SLCSP computation to reflect person-level eligibility.

## [1.256.0] - 2025-04-23 19:49:38

### Changed

- Corrected infant allowance file name in Massachusetts TAFDC program.

## [1.255.0] - 2025-04-22 20:32:13

### Added

- 2024 Arkansas State Income Tax Updates.

## [1.254.0] - 2025-04-19 16:18:12

### Added

- Limit itemized deductions to taxable income.

## [1.253.1] - 2025-04-19 11:11:45

## [1.253.0] - 2025-04-18 23:44:14

### Added

- 2024 New Mexico State Income Tax Updates.

## [1.252.1] - 2025-04-18 13:42:07

### Fixed

- Refactor the Massachusetts state supplement program.

## [1.252.0] - 2025-04-18 13:28:01

### Added

- New York itemized deductions reduction formula.

## [1.251.1] - 2025-04-16 23:27:50

### Added

- Added CHIP as a program seperate from Medicaid.

## [1.251.0] - 2025-04-15 18:10:28

### Added

- AFA 2025 reform.

## [1.250.0] - 2025-04-14 01:13:24

### Added

- Remove the pregnancy condition from LA infant supplement eligibility.

## [1.249.0] - 2025-04-10 21:23:06

### Added

- Remove the speedtest.

## [1.248.2] - 2025-04-10 07:14:19

## [1.248.1] - 2025-04-08 18:07:28

### Fixed

- Create a separate Hawaii itemized deductions reduction threshold to align with the tax forms.

## [1.248.0] - 2025-04-08 14:53:45

### Added

- 2024 Oregon State Income Tax Updates.

## [1.247.1] - 2025-04-08 11:51:57

### Fixed

- Fix the Colorado refundable CTC formula.

## [1.247.0] - 2025-04-07 20:54:03

### Added

- Mississippi retirement income exemption.

## [1.246.0] - 2025-04-07 17:11:50

### Added

- 2024 New Hampshire State Income Tax Updates.

## [1.245.1] - 2025-04-07 17:03:32

### Added

- Fix End Child Poverty Act uprating.

## [1.245.0] - 2025-04-06 13:44:41

### Changed

- DC Temporary Assistance for Needy Families (TANF) program.

## [1.244.1] - 2025-04-06 13:33:02

### Fixed

- Enable MA EAEDC and TAFDC.

## [1.244.0] - 2025-04-04 19:32:12

### Added

- Revert unwanted changes to MA EAEDC and TAFDC.

## [1.243.0] - 2025-04-04 17:04:17

### Added

- Include Massachusetts EAEDC and TAFDC in the net income tree.

## [1.242.1] - 2025-04-04 14:06:57

### Added

- Added 2021-2023 Medicaid spending and enrollment data.

## [1.242.0] - 2025-04-04 11:06:12

### Added

- 2024 Maine State Income Tax Updates.

## [1.241.0] - 2025-04-04 09:27:04

### Added

- Mississippi Income Tax Cut (2027-2030).

## [1.240.5] - 2025-04-03 16:03:51

### Added

- Fix 2025 Utah Income Tax Rate.

## [1.240.4] - 2025-04-03 11:58:58

### Fixed

- Account for the case where only one person is of the eligible immigration status under the LA GR program.

## [1.240.3] - 2025-04-03 08:25:20

### Fixed

- Convert meets_snap_categorical_eligibility to monthly.

## [1.240.2] - 2025-04-02 16:46:53

### Fixed

- Consolidated the different Medicaid parameters.

## [1.240.1] - 2025-04-01 18:27:47

### Added

- Conversion of county FIPS codes to county enum items
- Helper function to convert string county names to enum keys
- Function to download and parse county FIPS dataset from Hugging Face

### Changed

- Modified county variable to depend on FIPS input, then on ZIP code
- Modified county variable to use helper function for conversion from county names to enum keys

## [1.240.0] - 2025-04-01 18:13:56

### Added

- Massachusetts Bay Transportation Authority Income-Eligible Reduced Fare Program eligibility.
- Massachusetts Bay Transportation Authority Senior Charlie Card Program eligibility.
- Massachusetts Bay Transportation Authority Transportation Access Pass (TAP) Charlie Card Program eligibility.

## [1.239.0] - 2025-04-01 16:24:37

### Added

- 2024 Iowa State Income Tax Updates.

## [1.238.0] - 2025-04-01 13:44:29

### Added

- Massachusetts Emergency Aid to the Elderly, Disabled and Children (EAEDC).

## [1.237.0] - 2025-04-01 13:33:21

### Added

- 2025 Utah Income Tax Changes.

## [1.236.0] - 2025-04-01 12:10:52

### Added

- 2024 Louisiana State Income Tax Updates.

## [1.235.0] - 2025-03-31 15:42:14

### Added

- 2024 Washington State Income Tax Updates.

## [1.234.0] - 2025-03-28 18:57:33

### Added

- 2024 Hawaii State Income Tax Updates.

## [1.233.0] - 2025-03-28 17:49:52

### Added

- Convert TANF variables to monthly.

## [1.232.0] - 2025-03-28 12:23:21

### Added

- 2024 Indiana Income Tax Updates.

## [1.231.0] - 2025-03-26 17:10:58

### Added

- 2024 South Carolina State Income Tax Updates.

## [1.230.0] - 2025-03-25 20:22:29

### Added

- Kansas head of household additional exemption.

## [1.229.0] - 2025-03-25 20:17:19

### Added

- 2025 Idaho Grocery Credit.

## [1.228.0] - 2025-03-25 16:34:13

### Added

- Arizona 2024 income tax updates.

## [1.227.1] - 2025-03-25 09:56:10

### Added

- Updated State Spending on Medicaid.

## [1.227.0] - 2025-03-24 21:11:24

### Added

- Massachusetts Transitional Aid to Families with Dependent Children.

## [1.226.1] - 2025-03-24 20:55:29

### Fixed

- Minnesota working family credit phase-in threshold.

## [1.226.0] - 2025-03-24 14:07:04

### Added

- Include California State Supplement eligibility rules and include in the net income tree .

## [1.225.0] - 2025-03-24 11:38:01

### Added

- Oklahoma State Tax Code 2024 Updates.

## [1.224.0] - 2025-03-24 11:01:52

### Added

- 2024 Wisconsin State Income Tax Updates.

## [1.223.0] - 2025-03-20 23:52:06

### Added

- Illinois 2024 income tax updates.

### Fixed

- Illinois child tax credit logic.

## [1.222.0] - 2025-03-20 21:06:04

### Added

- 2023 to 2025 Massachusetts SSI State Supplement Parameters.

## [1.221.0] - 2025-03-20 15:35:49

### Added

- 2024 North Dakota State Income Tax Updates.

## [1.220.4] - 2025-03-20 14:53:50

### Fixed

- Refactor New Mexico itemized deductions.

## [1.220.3] - 2025-03-20 13:20:44

### Fixed

- Fixed SSI spousal deeming logic by adding the FBR differential threshold check required by §416.1163(d)(1). Now the ineligible spouse's income is only deemed if it exceeds the difference between couple and individual FBRs.
- Corrected a multi-argument `max_()` usage in the State Supplement code to use `np.maximum.reduce(...)`, ensuring that single disabled individuals now receive the correct (non-zero) supplement amount.
- Updated `ssi_category` so that disabled individuals are categorized properly (no longer `'NONE'`), fixing a scenario where the category check returned zero for disabled recipients.
- Revised the Massachusetts FULL_COST integration test to align with our current offset logic for large leftover incomes (previously returned an unexpected zero).

## [1.220.2] - 2025-03-20 12:28:46

### Added

- Added Maryland Tax Code Updates for 2024.

## [1.220.1] - 2025-03-20 12:19:03

### Fixed

- Remove the mistakenly added tax-dependent limit from the NC SCCA program as it is not required.

## [1.220.0] - 2025-03-19 21:49:56

### Added

- Minnesota 2024 state income tax updates.

## [1.219.2] - 2025-03-19 20:55:15

### Fixed

- Remove SSI from unearned income sources for NC TANF.

## [1.219.1] - 2025-03-19 09:32:35

### Fixed

- Rename capital_gains_before_response to long_term_capital_gains_before_response as it is unclear whether it might include/allocate short term.

## [1.219.0] - 2025-03-19 09:20:57

### Fixed

- Fixed Texas and Maine rating areas and corresponding SLCSP.

## [1.218.0] - 2025-03-19 07:54:52

### Added

- Missouri state tax code 2024 updates.

## [1.217.1] - 2025-03-18 07:50:27

### Fixed

- Idaho 2024 income tax rate.

## [1.217.0] - 2025-03-17 21:48:20

### Added

- Virginia state tax code 2024 updates.
- Replace inactive statutory links in the Virginia tax code.
- Update description of Virginia itemized deduction limits.

## [1.216.0] - 2025-03-17 21:43:27

### Added

- New York and Vermont ACA family tier ratings.

## [1.215.0] - 2025-03-17 21:18:41

### Added

- 2024 Mississippi State Income Tax Updates.

## [1.214.0] - 2025-03-17 09:50:22

### Added

- Move branch_to_determine_itemization to gov/simulation folder.

## [1.213.1] - 2025-03-14 00:28:04

### Fixed

- Changed reform to tax employer payroll taxes from a parametric to a structural reform to avoid double-counting.

## [1.213.0] - 2025-03-13 15:42:03

### Added

- 2024 Alabama State Income Tax Updates.

## [1.212.0] - 2025-03-12 18:28:39

### Added

- 2024 Kentucky State Income Tax Updates.

## [1.211.0] - 2025-03-12 15:09:34

### Added

- 2024 Idaho State Income Tax Updates.

## [1.210.0] - 2025-03-11 21:57:12

### Fixed

- Fixed California Rating Area 16's ACA premium.

## [1.209.2] - 2025-03-11 15:56:15

### Fixed

- Minnesota social security subtraction reduction.

## [1.209.1] - 2025-03-11 12:24:12

### Fixed

- Colorado credit returns NaNs in 2025 and beyond.
- Added test for NaNs in 2025 and beyond.

## [1.209.0] - 2025-03-10 15:29:09

### Added

- 2025 Idaho income tax cut.

## [1.208.0] - 2025-03-10 12:25:03

### Added

- 2024 Michigan State Income Tax Updates.

## [1.207.5] - 2025-03-08 12:59:39

### Fixed

- Typo in the Los Angeles County general relief housing subsidy parameters.

## [1.207.4] - 2025-03-07 19:23:38

### Added

- Adjust label for young child basic income age parameter.

## [1.207.3] - 2025-03-07 00:26:43

### Changed

- Adjust the Infant age group definition for North Carolina SCCA program.

## [1.207.2] - 2025-03-06 14:07:16

### Fixed

- Alabama retirement exemption computation.

## [1.207.1] - 2025-03-06 13:36:02

### Fixed

- Remove Colorado SNAP net income test.

## [1.207.0] - 2025-03-05 14:11:36

### Added

- Implemented North Carolina Subsidized Child Care Assistance (SCCA) program and entry eligibility calculations.

## [1.206.0] - 2025-03-04 23:26:22

### Added

- Utah state tax code 2024 updates.

## [1.205.0] - 2025-03-03 23:06:08

### Added

- Modified reform for counting employer side payroll taxes in employees' IRS gross income so that Social Security and Medicare can be included separately.

## [1.204.1] - 2025-03-01 23:09:07

### Fixed

- {'Hide program takeup parameters from the web UI by setting economy': 'false in their metadata'}

## [1.204.0] - 2025-03-01 15:17:51

### Added

- Employer side Social Security and Medicare payroll tax.
- Reform for counting employer side payroll taxes in employees' IRS gross income.

## [1.203.2] - 2025-02-28 14:57:36

### Fixed

- Louisiana federal tax deduction reduction.

## [1.203.1] - 2025-02-28 14:09:09

### Fixed

- Cap the FISC Act AGI floor at 0.

## [1.203.0] - 2025-02-27 08:40:40

### Added

- Ohio state tax code 2025 updates.

## [1.202.2] - 2025-02-24 23:14:08

### Added

- CLAUDE.md with development guidelines and common code patterns

### Fixed

- Delete old ACA SLCSP files
- Expanded Variables Related to LA county SLCSP
- Fix array comparison in the LA expectant parent payment eligibility formula

## [1.202.1] - 2025-02-24 13:59:24

### Fixed

- Floor the income bracket at 1 in the state_sales_tax variable.

## [1.202.0] - 2025-02-20 19:47:27

### Added

- 2024 Massachusetts State Income Tax Updates.

## [1.201.0] - 2025-02-20 15:41:40

### Added

- Nationwide (except NY and VT) ACA for 2025.

## [1.200.2] - 2025-02-20 15:09:55

### Fixed

- Correct AMT single exemption amount values.

## [1.200.1] - 2025-02-20 13:23:33

### Fixed

- FISC act in effect parameter type.

## [1.200.0] - 2025-02-20 03:56:06

### Added

- New York Pension exclusion Variable.
- New York Subtraction List Parameter.
- Added test for New York pension exclusion variable.

## [1.199.0] - 2025-02-19 20:13:32

### Added

- Family Income Supplemental Credit Act reform.

## [1.198.1] - 2025-02-19 20:05:31

### Fixed

- Apply miscellaneous deduction floor.
- Add miscellaneous deduction to the AMT Income calculation.

## [1.198.0] - 2025-02-18 23:22:33

### Added

- DC 2024 Income Tax Updates.

## [1.197.1] - 2025-02-18 22:33:47

### Added

- Add personal exemptions to the AMT Income calculation.

## [1.197.0] - 2025-02-17 23:53:42

### Changed

- Uprate medical expense categories by CMS MOOP per capita projections.

## [1.196.1] - 2025-02-14 20:39:21

### Fixed

- Set the bottom bracket to -.inf under the New York Inflation Rebates reform.

## [1.196.0] - 2025-02-14 19:34:59

### Added

- Kentucky income tax rate 2026.

## [1.195.1] - 2025-02-13 21:40:47

### Added

- update the CSFP income limits

## [1.195.0] - 2025-02-13 01:08:09

### Added

- Rename interest_expense to deductible_interest_expense.

## [1.194.0] - 2025-02-13 01:01:20

### Added

- Colorado 2024 tax form references.
- 2023 and 2024 Colorado Income Qualified Senior Housing Credit.
- 2024 Colorado ABLE Account Cap.
- 2023 and 2024 Colorado CollegeInvest Maximum Amount.
- 2024 Colorado State Sales Tax Refund.

## [1.193.0] - 2025-02-13 00:37:01

### Added

- Kansas State Tax Code 2024 Updates.

## [1.192.2] - 2025-02-12 20:02:57

## [1.192.1] - 2025-02-11 18:25:27

### Fixed

- Create a non_deductible_mortgage_interest variable.
- Sum deductible and non-deductible interest in the mortgage_interest variable.

## [1.192.0] - 2025-02-11 16:25:15

### Added

- Apply itemized deduction limitations.

## [1.191.0] - 2025-02-10 21:41:56

### Added

- CBO uprating factors for all tax parameters through 2035.

## [1.190.0] - 2025-02-07 21:44:34

### Added

- 2024 North Carolina Income Tax Updates.

## [1.189.0] - 2025-02-06 20:58:56

### Added

- Pennsylvania 2024 income tax updates.

## [1.188.0] - 2025-02-06 10:21:40

### Added

- Refactor the Alternative Minimum Tax (AMT) logic.

## [1.187.3] - 2025-02-05 18:19:06

### Fixed

- Adds 2025 Federal Poverty Guidelines.

## [1.187.2] - 2025-02-05 00:41:13

## [1.187.1] - 2025-02-04 16:24:45

### Fixed

- Revert previous commit.

## [1.187.0] - 2025-02-03 22:12:04

### Added

- January 2025 CBO economic and demographic outlooks.

## [1.186.0] - 2025-01-31 15:42:23

### Added

- Change is_widowed to is_surviving_spouse.

## [1.185.0] - 2025-01-31 14:12:32

### Added

- Georgia State Tax Code 2024 Updates.

## [1.184.0] - 2025-01-29 20:49:54

### Added

- New York City 2024 tax form references.

## [1.183.1] - 2025-01-29 15:14:24

### Fixed

- Iowa income tax structure on and after 2023.

## [1.183.0] - 2025-01-29 01:21:20

### Added

- New York 2024 tax form references.

## [1.182.2] - 2025-01-28 13:45:56

### Fixed

- California itemized deduction limits 2024.
- California AMT parameters 2024.
- California 2024 tax form references.

## [1.182.1] - 2025-01-27 21:39:20

### Fixed

- Invalid value encountered when dividing income_effect by original_earnings and dividing substitution_effect by original_earnings in weekly hours worked calculation

## [1.182.0] - 2025-01-27 12:51:08

### Added

- NYC school tax credit phase out reform.

## [1.181.0] - 2025-01-24 16:56:04

### Added

- Optional State Sales Tax Rates.

## [1.180.4] - 2025-01-24 16:12:31

## [1.180.3] - 2025-01-24 16:08:29

### Fixed

- Include the New York 2025 Inflation Rebates in the net income tree.

## [1.180.2] - 2025-01-23 16:58:25

### Fixed

- Invalid value when dividing employment_income by total_earnings in marginal tax rate calculation.

## [1.180.1] - 2025-01-22 06:23:40

### Fixed

- Limit DC PTC to filers that take it up in the reform.

## [1.180.0] - 2025-01-21 20:24:31

### Added

- 2024 California YCTC and Foster Youth Credit parameters.

## [1.179.0] - 2025-01-21 05:05:10

### Added

- 2025 New York Inflation Rebates.

## [1.178.0] - 2025-01-21 04:58:51

### Added

- Maryland standard deduction values 2024.

## [1.177.0] - 2025-01-20 15:53:06

### Added

- Limit the SALT deduction to property taxes reform.

## [1.176.3] - 2025-01-20 05:43:12

### Fixed

- Apply the 5 year forward check to the SALT phase out reform.

## [1.176.2] - 2025-01-18 00:44:16

### Fixed

- DC property tax credit phase-out calculation.

## [1.176.1] - 2025-01-17 14:54:51

### Fixed

- DC property tax credit reform 5 year forward check.

## [1.176.0] - 2025-01-17 04:08:48

### Added

- Puerto Rico low income credit.
- Puerto Rico compensatory low income credit.

## [1.175.0] - 2025-01-16 21:12:09

### Added

- Missouri 2024 and 2025 top income tax rate.
- Missouri 2024 working family tax credit match.

## [1.174.1] - 2025-01-16 20:40:42

### Fixed

- Limit CAPI to households with eligible aged or disabled filers.

## [1.174.0] - 2025-01-15 21:19:28

### Added

- Colorado income tax rate 2024.

## [1.173.0] - 2025-01-13 19:10:03

### Added

- References for New Jersey 2024 state income tax.

## [1.172.1] - 2025-01-13 17:48:43

### Fixed

- 2024 Connecticut income tax rates for HOH and surviving spouses.

## [1.172.0] - 2025-01-13 01:59:31

### Added

- DC property tax credit reform.

## [1.171.0] - 2025-01-10 11:34:59

### Added

- DC property tax credit take up.

## [1.170.2] - 2025-01-10 05:35:35

### Fixed

- Only apply the Virginia rebate to the 2023 tax year.

## [1.170.1] - 2025-01-09 21:40:41

### Added

- Montana top income tax rate 2024.

## [1.170.0] - 2025-01-09 16:55:35

### Added

- 2024 DC keep child care affordable tax credit max benefit and thresholds.
- DC EITC match delay to 2029.

## [1.169.0] - 2025-01-08 23:32:39

### Added

- State-level variables in taxsim.

## [1.168.1] - 2025-01-06 18:47:40

### Fixed

- NYC income tax rates.

## [1.168.0] - 2025-01-06 15:50:44

### Added

- New Jersey medical expense deduction.

## [1.167.2] - 2025-01-06 05:03:19

### Fixed

- Uncap New York real estate tax deduction.
- Cap New York college tuition expenses credit and deduction per student.

## [1.167.1] - 2025-01-03 16:28:36

### Fixed

- Iowa alternate tax eligibility.

## [1.167.0] - 2024-12-28 02:48:55

### Added

- 2024 DC property tax credit maximum benefit and thresholds

## [1.166.0] - 2024-12-27 21:44:15

### Added

- Abolish SNAP net income test reform.
- Abolish SNAP deductions reform.

## [1.165.0] - 2024-12-26 12:59:32

### Added

- SSI qualified non-citizen eligibility.

## [1.164.0] - 2024-12-24 21:20:18

### Added

- Expanded CTC reform including a reformed phase-in structure.

## [1.163.1] - 2024-12-24 18:42:26

### Fixed

- Illinois income tax before non-refundable credits variable format.

## [1.163.0] - 2024-12-24 15:53:04

### Added

- 2026 Estate Tax Credit Exemption amount.

## [1.162.3] - 2024-12-24 12:46:05

### Fixed

- Indiana National Guard and Reserve Pay Deduction 2023.

## [1.162.2] - 2024-12-23 19:54:14

### Fixed

- Adjust the EPP max pregnancy month value.

## [1.162.1] - 2024-12-20 16:50:32

### Added

- 2
- 0
- 2
- 5
-  
- S
- S
- I
- ,
-  
- A
- N
- D
- -
- C
- S
- ,
-  
- a
- n
- d
-  
- O
- A
- P
-  
- v
- a
- l
- u
- e
- s

## [1.162.0] - 2024-12-18 02:31:13

### Added

- Add non-refundable credits to state dependent exemption reform.

## [1.161.3] - 2024-12-18 02:17:13

### Fixed

- New York Working Families Tax Credit parameter structure.
- New York exemptions child definition.

## [1.161.2] - 2024-12-15 23:08:57

### Fixed

- NYWFTC EITC older children eligibility.

## [1.161.1] - 2024-12-13 23:43:04

### Added

- Capability to select custom start time for simulations; this is a patch for structural reforms that occur at non-default time periods.

## [1.161.0] - 2024-12-12 05:36:14

### Added

- Nebraska military retirement benefit exclusion.

## [1.160.0] - 2024-12-05 16:48:14

### Added

- Second earner tax reform.

## [1.159.0] - 2024-12-05 16:42:58

### Added

- Add multiple state exemptions to the repeal of state dependent exemptions reform.

## [1.158.0] - 2024-12-05 15:58:14

### Added

- Montana property tax rebate.

## [1.157.0] - 2024-12-05 15:47:47

### Added

- Remove CBO elasticities toggle.

## [1.156.0] - 2024-12-04 21:38:01

### Added

- Apply the TCJA mortgage value limits under the mortgage interest deduction.

## [1.155.1] - 2024-12-04 19:11:45

### Fixed

- Remove the SNAP child support deduction from the net income computation if applied to gross income.

## [1.155.0] - 2024-12-03 20:23:24

### Added

- Add the Arizona charitable contributions credit to the net income tree.

## [1.154.2] - 2024-12-03 20:14:27

### Changed

- Upgraded minimum policyengine-core version
- Allowed more flexibility in policyengine-us-data version

## [1.154.1] - 2024-12-01 16:39:30

### Fixed

- Arkansas 2023 low income tax table parameters.

## [1.154.0] - 2024-11-30 18:08:00

### Added

- Louisiana 2025 standard deduction structure.

## [1.153.0] - 2024-11-25 23:01:42

### Added

- Louisiana 2025 flat income tax rate.
- Louisiana 2025 retirement income exemption increase.

## [1.152.0] - 2024-11-25 22:04:48

### Added

- Montana 2023 income tax rebate.

## [1.151.0] - 2024-11-25 21:52:13

### Added

- Apply the phase-in to the CTC when computing the New York empire state credit.

## [1.150.1] - 2024-11-25 12:08:59

### Fixed

- Montana 2023 / 2024 EITC match.

## [1.150.0] - 2024-11-21 03:44:18

### Added

- Reform to repeal state dependent exemptions.

## [1.149.0] - 2024-11-21 03:30:46

### Added

- Delaware 2022 relief rebate.

## [1.148.0] - 2024-11-21 02:32:20

### Added

- CTC supplement for oldest child reform.
- Child index variable.

## [1.147.0] - 2024-11-19 23:38:18

### Added

- SALT phase-out reform separate rate for joint filers.

## [1.146.2] - 2024-11-19 21:32:57

### Added

- New test to cliff_evaluated to demonstrate differences between adults and children in given household.

### Changed

- Changed formula for cliff_evaluated to use new marginal tax rate adults parameter.
- Updated cliff_gap test to use new marginal tax rate adults parameter.

## [1.146.1] - 2024-11-19 16:41:43

### Added

- Monthly age variable.

### Fixed

- Los Angeles Infant Supplement and Expectant Parent Payment age threshold.

## [1.146.0] - 2024-11-19 13:15:26

### Changed

- US-Data to 1.13.

## [1.145.0] - 2024-11-18 13:26:09

### Fixed

- Cliff variables.

## [1.144.0] - 2024-11-18 02:11:15

### Added

- SALT deduction phase-out reform.

## [1.143.0] - 2024-11-18 01:37:58

### Added

- Montana 2023 income tax rule updates.

## [1.142.5] - 2024-11-16 20:55:48

### Added

- Populate va_agi_person and add the Virginia spouse tax adjustment to the net income tree.

## [1.142.4] - 2024-11-16 20:47:40

### Fixed

- Remove the child tax rebate from the list of 2023 rhode island refundable credits.

## [1.142.3] - 2024-11-16 20:18:42

### Added

- Add the 2023 Arkansas inflation relief credit amount and avoid attributing the amount twice for joint filers filing separately.

## [1.142.2] - 2024-11-15 19:21:17

### Fixed

- Refactor the New York Working Families Tax Credit.

## [1.142.1] - 2024-11-14 20:12:06

### Fixed

- Mississippi missing 2023 income tax bracket thresholds.

## [1.142.0] - 2024-11-14 17:44:55

### Added

- Georgia 2024 income tax rate update.

## [1.141.0] - 2024-11-13 16:46:23

### Added

- Los Angeles County expectant parent payment.
- Los Angeles County infant supplement.

## [1.140.1] - 2024-11-11 04:47:50

### Fixed

- Iowa Income Tax Rates 2023-2026.

## [1.140.0] - 2024-11-11 04:40:19

### Fixed

- NJ EITC correctly calculates federal EITC entitlement.

## [1.139.2] - 2024-11-10 18:07:53

### Added

- Test for meets_school_meal_categorical_eligibility with vectorized inputs.

### Fixed

- Corrected meets_school_meal_categorical_eligilibity to properly calculate eligibility for vectorized inputs.

## [1.139.1] - 2024-11-08 23:52:56

### Added

- Label to Alaska tax param folder

## [1.139.0] - 2024-11-07 11:43:28

### Added

- Update EITC joint bonus for childless filers.

## [1.138.0] - 2024-11-05 21:37:21

### Added

- SNAP 2024 SUA for Colorado

## [1.137.4] - 2024-11-04 12:17:46

### Fixed

- Qualified business defaults to true.

## [1.137.3] - 2024-11-01 16:53:33

### Fixed

- Colorado 2023 sales tax refund.

## [1.137.2] - 2024-11-01 10:27:40

### Fixed

- Branch improvements.

## [1.137.1] - 2024-10-31 18:57:07

### Fixed

- remove uprating for SNAP variables that don't change

## [1.137.0] - 2024-10-30 18:47:11

### Added

- California Medicaid Former Foster Youth Program.

## [1.136.2] - 2024-10-30 02:19:31

### Changed

- Altered handling of federal params in VA reduced itemized deductions

## [1.136.1] - 2024-10-29 19:55:24

### Changed

- Updated policyengine-us-data to 0.11.1
- Updated microdf-python to 0.4.3

## [1.136.0] - 2024-10-29 13:25:05

### Added

- Capital gains tax responses.

## [1.135.0] - 2024-10-28 21:33:47

### Added

- Remaining 2025 IRS tax posted parameter updates.

## [1.134.0] - 2024-10-28 20:09:23

### Added

- DC Child Tax Credit.

## [1.133.0] - 2024-10-27 22:00:19

### Added

- Separate tip income and overtime income from the main tax exempt reforms structure.

## [1.132.0] - 2024-10-24 03:58:00

### Added

- Trump tip income tax exempt.

## [1.131.0] - 2024-10-23 22:18:23

### Added

- 2025 income and capital gains thresholds.

## [1.130.0] - 2024-10-23 20:51:51

### Added

- End ACP effective 2024-06-01.

## [1.129.3] - 2024-10-21 20:37:15

### Fixed

- Changed weekly_hours_worked to weekly_hours_worked_before_lsr in SNAP formula to avoid circular dependency.

## [1.129.2] - 2024-10-21 20:22:41

### Changed

- Updated required version of policyengine-core

## [1.129.1] - 2024-10-21 19:39:15

### Fixed

- Pregnant people counted as 2 for Medicaid FPG percent

## [1.129.0] - 2024-10-17 19:59:12

### Added

- Biden NIIT label and description change.

## [1.128.0] - 2024-10-16 12:20:25

### Added

- Michigan 2024 income tax rate update.

## [1.127.0] - 2024-10-15 19:32:53

### Added

- Georgia 2024 dependent exemption amount update.

## [1.126.0] - 2024-10-15 18:57:14

### Added

- Chained CPI 2035.

## [1.125.0] - 2024-10-15 16:32:32

### Added

- Exclude students from the SNAP unit with certain exceptions.

## [1.124.0] - 2024-10-15 16:26:25

### Added

- IN county taxes.

## [1.123.0] - 2024-10-15 10:18:53

### Added

- 2024 tax rate, CDCC match, standard deduction and personal exemption amount in Kansas..

## [1.122.0] - 2024-10-15 03:15:23

### Added

- Kansas disabled veteran exemptions.

## [1.121.0] - 2024-10-15 03:05:54

### Added

- Idaho 2024 income tax rate and brackets.

## [1.120.0] - 2024-10-15 00:23:23

### Added

- California Income Tax Thresholds 2024.

## [1.119.0] - 2024-10-14 20:55:12

### Added

- California Standard Deduction, Personal/Dependent Exemption Credits and Renter AGI Cap 2024.

## [1.118.0] - 2024-10-14 20:30:24

### Added

- Kentucky Standard Deduction 2024 & 2025.

## [1.117.0] - 2024-10-14 19:22:35

### Added

- Harris capital gains tax reform.

## [1.116.0] - 2024-10-14 19:08:02

### Added

- Missouri 2024 income tax rate and brackets.

## [1.115.0] - 2024-10-09 15:10:16

## [1.114.0] - 2024-10-09 11:09:17

## [1.113.0] - 2024-10-09 04:16:32

### Added

- Minnesota 2024 standard deduction limitations update.

## [1.112.0] - 2024-10-08 14:36:53

### Added

- Minnesota 2024 base and additional standard deduction amount updates.

## [1.111.0] - 2024-10-08 14:25:53

### Added

- Added NC SNAP utility allowances for FY 2025.

### Fixed

- Corrected NC SNAP utility allowance parameters start date.

## [1.110.0] - 2024-10-07 13:04:35

## [1.109.0] - 2024-10-06 10:30:21

### Added

- EITC takeup by number of children.

## [1.108.0] - 2024-10-05 12:11:34

### Added

- Minnesota 2024 income tax bracekts.

## [1.107.0] - 2024-10-05 07:43:35

### Added

- Typo in CalWORKs exempt parameter.

## [1.106.0] - 2024-10-04 16:51:40

### Added

- Parameterize the age in is_person_demographic_tanf_eligible.

## [1.105.2] - 2024-10-02 17:49:23

### Added

- Always use the SUA for CO.

## [1.105.1] - 2024-09-30 22:09:41

### Changed

- Moved loading of abolitions parameters earlier in initialization process

## [1.105.0] - 2024-09-30 17:03:10

### Added

- North Carolina military retirement deduction.

## [1.104.0] - 2024-09-30 16:54:45

### Added

- 2023 Medicaid income limit updates.

## [1.103.0] - 2024-09-29 23:26:45

### Added

- Oklahoma military retirement benefit exclusion.
- Oklahoma AGI subtractions list.

## [1.102.0] - 2024-09-29 22:51:45

### Changed

- PolicyEngine-US-Data bumped to 1.8

## [1.101.0] - 2024-09-29 04:49:39

### Added

- Child Tax Credit phase-in variable.

### Fixed

- Child Tax Credit value variable.
- Pinned policyengine-core version.

## [1.100.0] - 2024-09-28 02:35:09

### Added

- North Carolina rate changes for 2024 on.
- 2024 Rhode Island EITC match.

### Fixed

- NYC tax credit parameter formatting.

## [1.99.1] - 2024-09-27 20:22:56

### Fixed

- Update the Hawaii SNAP net income test application.

## [1.99.0] - 2024-09-27 20:12:23

### Fixed

- Remove lifeline variable from spm_unit_broadband_subsidy.
- Modified tests for spm_unit_broadband_subsidy.

## [1.98.0] - 2024-09-27 20:05:18

### Added

- 2024 Kentucky income tax rate reduction.

## [1.97.0] - 2024-09-27 19:50:33

### Added

- New Family Security Act version.

## [1.96.0] - 2024-09-27 19:42:19

### Added

- Alaska Permanent Fund Dividend and One-time Energy Relief Payments.

## [1.95.0] - 2024-09-27 19:10:57

### Added

- 2024 CalFresh (SNAP) standard medical deduction amount increase.

## [1.94.0] - 2024-09-27 19:02:03

### Added

- Use adjusted gross income in withheld state income tax.
- Separate takes_up_snap_if_eligible variable from snap variable.

## [1.93.0] - 2024-09-25 17:55:53

### Added

- Add post TCJA income tax rates.

## [1.92.1] - 2024-09-25 11:53:57

### Changed

- US data version to 1.6.0.

## [1.92.0] - 2024-09-25 00:47:29

### Changed

- Made Maine dependent exemption credit refundable in 2024.

## [1.91.0] - 2024-09-23 22:24:38

### Added

- Include 17 year olds in the NYWFTC as younger children.

## [1.90.0] - 2024-09-23 19:44:39

### Added

- Remove total_income and net_income.

## [1.89.0] - 2024-09-23 13:43:10

### Changed

- PE-US-Data bumped to 1.5.1.

## [1.88.0] - 2024-09-23 09:43:51

### Added

- Tenure type.
- Uprating for rent and property taxes.
- Household reference person flag.

## [1.87.0] - 2024-09-21 01:56:21

### Added

- New Mexico armed forces retirement pay exemption.

## [1.86.0] - 2024-09-21 01:08:08

### Added

- Wisconsin 2024 CDCC match value.

## [1.85.4] - 2024-09-20 15:00:03

### Added

- Speedtests to PRs.

## [1.85.3] - 2024-09-19 17:53:36

### Fixed

- Add defined_for metadata for all state level variables.

## [1.85.2] - 2024-09-19 16:01:11

## [1.85.1] - 2024-09-19 15:49:59

### Changed

- Medicaid national parameters run off a CSV, cutting runtime by ~8%.

## [1.85.0] - 2024-09-19 02:32:58

### Added

- Nebraska child care subsidy.

## [1.84.0] - 2024-09-19 02:19:49

### Added

- 2025 CalWORKs payment standards increase.

## [1.83.1] - 2024-09-19 02:12:02

## [1.83.0] - 2024-09-19 02:03:16

### Added

- 2025 CalWORKs maximum resource limit update.

## [1.82.0] - 2024-09-19 01:11:12

### Added

- Calculation logic for North Carolina SNAP standard and limited utility allowance by household size amount.

## [1.81.0] - 2024-09-18 18:16:20

### Changed

- Corrected connection with us-data repository

## [1.80.1] - 2024-09-17 12:08:35

### Fixed

- Adjust the kiddie tax logic in the AMT calculation.

## [1.80.0] - 2024-09-17 03:02:20

### Added

- Apply the federal standard and itemized deductions in Iowa from 2023 on.

## [1.79.3] - 2024-09-16 16:11:42

### Fixed

- Wisconsin 2nd tax bracket for single and hoh in 2023.

## [1.79.2] - 2024-09-16 14:57:51

### Fixed

- Add switch to basic income phase-in.

## [1.79.1] - 2024-09-14 00:18:02

### Added

- Loading of policyengine-us-data from PyPI

### Fixed

- Divided tests within GitHub Actions to avoid resource issues

## [1.79.0] - 2024-09-12 17:10:41

### Added

- Test for additional standard deduction variable.

## [1.78.1] - 2024-09-12 04:48:22

### Added

- Updated CO TANF grant standard

## [1.78.0] - 2024-09-10 22:10:39

### Added

- Update SNAP values for 2025.

## [1.77.0] - 2024-09-10 17:15:06

### Added

- Utah additional dependent exemption starting in 2023.

## [1.76.3] - 2024-09-09 20:03:22

### Fixed

- Separate the CTC and EITC under the FSA 2.0.

## [1.76.2] - 2024-09-09 19:58:03

### Fixed

- Fix CSFP income limit

## [1.76.1] - 2024-09-09 16:40:19

## [1.76.0] - 2024-09-07 00:01:09

### Changed

- Separated data from main repo.

## [1.75.1] - 2024-09-06 20:25:29

### Added

- Commodity Supplemental Food Program

## [1.75.0] - 2024-09-06 16:56:54

### Fixed

- Refactor the Utah income tax tree.
- Remove ut_taxpayer_credit from the non-refundable credits list.

## [1.74.0] - 2024-09-06 03:17:09

### Added

- Arkansas 2024 tax rate.

## [1.73.0] - 2024-09-05 23:56:03

### Added

- Implemented North Carolina TANF need standard and eligibility calculations.

## [1.72.2] - 2024-09-05 23:49:18

### Fixed

- Minnesota pension income subtraction parameter value.

## [1.72.1] - 2024-09-05 12:33:59

### Changed

- Update policyengine-core to 3.6.5

## [1.72.0] - 2024-09-04 10:39:53

### Added

- 2024 Medicaid income limit updates for North Carolina.

## [1.71.1] - 2024-09-03 23:46:01

### Fixed

- Minor bugs and deconstruct MOOP variables in CPS.

## [1.71.0] - 2024-09-03 22:33:44

### Added

- Apply ALD to alimony expense, not income in the above the line deductions.
- Divorce status to cps.py.

## [1.70.0] - 2024-09-03 22:29:43

### Added

- Change reform parameters to default to 0.

## [1.69.1] - 2024-09-03 21:50:50

### Fixed

- Five year forward check in the Repeal dependent exemptions reform.

## [1.69.0] - 2024-09-02 11:22:31

### Added

- Infant calibration and uprating.

## [1.68.0] - 2024-09-01 18:17:57

### Added

- Family Security Act 2.0 CTC amount per child and pregnancy credit structure.

## [1.67.0] - 2024-08-31 18:22:12

### Added

- Family Security Act 2.0 provisions.

## [1.66.0] - 2024-08-31 16:36:48

### Added

- Repeal dependent exemption reform.

## [1.65.1] - 2024-08-29 23:49:17

### Fixed

- Increase Hawaii Military Reserve or Hawaii National Guard Duty Pay Cap.
- Rhode Island 2023 military retirement pay subtraction.

## [1.65.0] - 2024-08-29 22:06:21

### Added

- New York supplemental tax incremental benefit repeal for 2028

## [1.64.0] - 2024-08-29 15:00:53

### Added

- CARES act charity deduction provision for non-itemizers.

## [1.63.0] - 2024-08-26 22:09:35

### Added

- Mississippi child and dependent care credit.

## [1.62.0] - 2024-08-26 21:37:42

### Added

- Oregon WFHDC household income variable.

## [1.61.2] - 2024-08-26 14:19:06

## [1.61.1] - 2024-08-25 22:50:32

### Fixed

- Oregon rebate reform typo.

## [1.61.0] - 2024-08-23 15:56:12

### Added

- Oregon Rebate state tax exempt reform.

## [1.60.0] - 2024-08-22 23:31:20

### Added

- Separate out SSI eligibility from the general uncapped_ssi file.

## [1.59.0] - 2024-08-22 15:03:28

### Added

- Denver property tax relief.

## [1.58.0] - 2024-08-22 00:24:36

### Added

- IRS VITA Program Eligibility.

## [1.57.1] - 2024-08-21 15:12:46

### Fixed

- Minnesota standard and itemized deduction reduction structure.

## [1.57.0] - 2024-08-20 01:56:19

### Added

- 2024 Nebraska tax rules update.

## [1.56.1] - 2024-08-19 18:40:57

### Fixed

- Bug in Harris Rent Relief Act for low earners.

## [1.56.0] - 2024-08-19 15:50:20

### Added

- Add head_start and early_head_start variables to household_benefits parameter.

## [1.55.0] - 2024-08-18 16:54:38

### Added

- Personal Credit reform.

## [1.54.4] - 2024-08-18 16:32:45

### Fixed

- Minnesota Bill HF1938 impact fix.

## [1.54.3] - 2024-08-17 22:15:46

### Fixed

- Limit American Family Act baby bonus reform to CTC-eligible children.
- Make AFA baby bonus and head of household repeal work after 2024.

## [1.54.2] - 2024-08-17 18:47:58

### Fixed

- Mixed scalar and vectorized operations in mn_social_security_subtraction.

## [1.54.1] - 2024-08-17 16:48:52

## [1.54.0] - 2024-08-17 15:50:59

### Added

- Reform repeal Minnesota Bill HF1938.

## [1.53.0] - 2024-08-17 13:51:13

### Added

- Refactor the `household_benefits` and `household_state_benefits` variables to include a list parameter.

## [1.52.0] - 2024-08-16 15:31:16

### Added

- Infant calibration.

## [1.51.1] - 2024-08-16 11:45:37

## [1.51.0] - 2024-08-16 11:39:35

### Added

- Use un-reduced income for calculating the excess of the rent relief credit.

## [1.50.0] - 2024-08-13 16:02:31

### Added

- Flat tax on gross income.

## [1.49.0] - 2024-08-13 14:42:06

### Fixed

- Inaccurate docstring in loss.py

## [1.48.0] - 2024-08-13 03:08:12

### Added

- Update to codecov/codecov-action@v4, actions/setup-python@v5, and actions/checkout@v4.

## [1.47.0] - 2024-08-12 16:32:53

### Added

- Rent relief tax credit.

## [1.46.0] - 2024-08-12 15:37:43

### Added

- New York additional Empire State Tax Credit.

## [1.45.2] - 2024-08-10 19:54:58

### Fixed

- Inclusion of unneeded packages in pyproject.toml install_requires list.

## [1.45.1] - 2024-08-10 11:09:59

### Fixed

- Refactor the alternative minimum tax files.
- Include capital gains tax in the final alternative minimum tax calculation.

## [1.45.0] - 2024-08-10 03:56:39

### Added

- Support for Python 3.12.

## [1.44.1] - 2024-08-08 18:06:51

### Fixed

- Restriction on out-dated version of policyengine-core.

## [1.44.0] - 2024-08-08 15:22:20

### Added

- Nebraska refundable child tax credit.
- Remove duplicate childcare expenses variable.

## [1.43.1] - 2024-08-06 21:26:16

### Added

- California TANF resources variable inputs.

## [1.43.0] - 2024-08-06 18:44:12

### Added

- Revised State Median Income (SMI) Ceilings 2024

## [1.42.1] - 2024-08-06 17:30:53

### Fixed

- Adjust the income_tax_before_refundable_credits variable to be neutralized when abolishing federal income tax.

## [1.42.0] - 2024-08-06 16:57:19

### Added

- North Carolina use tax.

## [1.41.0] - 2024-08-05 21:40:16

### Added

- Head Start and Early Head Start programs eligibility.

## [1.40.1] - 2024-08-05 00:52:28

### Added

- Consistent unit usage in list parameters.

## [1.40.0] - 2024-08-02 17:55:58

### Added

- Indiana additional exemption amount for adopted children.

## [1.39.0] - 2024-08-02 03:31:58

### Added

- BOOST act middle class tax credit.

## [1.38.0] - 2024-08-01 15:51:55

### Added

- July 2024 CalWorks vehicle value increase.

## [1.37.0] - 2024-08-01 13:55:37

### Added

- Remove the parameter caching from the state variables.

## [1.36.0] - 2024-08-01 13:25:55

### Added

- California & Oregon higher Lifeline benefit amount.

## [1.35.0] - 2024-07-31 07:15:11

### Added

- Decouple the WFTC child age eligibility from the NY exemptions child age threshold.

## [1.34.7] - 2024-07-30 20:20:10

### Fixed

- Add the Child benefit component to the ECPA reform.

## [1.34.6] - 2024-07-30 20:06:02

### Fixed

- Minor CTC social security parameter formatting.

## [1.34.5] - 2024-07-30 16:30:17

### Fixed

- Structure End Child Poverty Act as a reform.

## [1.34.4] - 2024-07-30 05:34:09

### Fixed

- Add the flat tax variable in the relevant net income tree computations.
- Index general household and state level parameters.

## [1.34.3] - 2024-07-30 00:23:32

### Fixed

- Exclude childless filers from the NY WFTC EITC reduction.

## [1.34.2] - 2024-07-29 20:47:46

### Fixed

- Optimize for the Hawaii deduction.

## [1.34.1] - 2024-07-26 02:54:51

### Fixed

- Limit the older children under the Working Families Tax Credit above 18 years.

## [1.34.0] - 2024-07-25 22:43:01

### Added

- 2023 Montana Tax Rules.

## [1.33.1] - 2024-07-25 13:01:20

### Fixed

- Remove the adds function from the reported_state_income_tax reform file.

## [1.33.0] - 2024-07-25 12:45:43

### Added

- 2023 Washington Tax Rules.

## [1.32.0] - 2024-07-25 04:22:15

### Added

- 2023 Indiana income tax updates.

## [1.31.4] - 2024-07-25 02:41:53

### Fixed

- Disabeld the exhaustive_parameter_dependencies metadata in household_refundable_state_tax_credits as it was not working with state reforms.

## [1.31.3] - 2024-07-24 20:47:17

### Added

- Restructure Nebraska variables and tests.

## [1.31.2] - 2024-07-24 20:10:44

### Fixed

- Cap the Pell Grant amount at the cost of attendance.

## [1.31.1] - 2024-07-24 20:06:00

### Fixed

- DC CTC parameter period function.

## [1.31.0] - 2024-07-24 01:38:48

### Added

- 2023 Nebraska income tax values.

## [1.30.1] - 2024-07-24 01:33:28

### Fixed

- Adjust the DC CTC formatting.

## [1.30.0] - 2024-07-24 00:03:46

### Added

- Tax Counseling for the Elderly eligibility.

## [1.29.0] - 2024-07-23 21:52:58

### Added

- SSI blind or disabled working student earned income exemption.

## [1.28.0] - 2024-07-23 04:22:45

### Added

- Update 2023 SNAP medical deductions.

## [1.27.0] - 2024-07-23 03:17:03

### Added

- Separate WIC eligibility variable.

## [1.26.2] - 2024-07-22 20:45:34

### Added

- Pell Grant Student Aid Index.

## [1.26.1] - 2024-07-22 18:07:41

### Added

- Refactor social security taxes for refundable CTC calculation.

## [1.26.0] - 2024-07-22 07:26:38

### Fixed

- Formatting adjustments to the Middle Class Tax Credit.
- Added pell grants to the earned income definitions for the Middle Class Tax Credit.

## [1.25.2] - 2024-07-21 16:10:11

### Added

- Fix 2018 surviving spouse AMT exemption value.

## [1.25.1] - 2024-07-21 16:01:23

### Added

- 2019 Kamala Harris LIFT proposal.

## [1.25.0] - 2024-07-21 02:11:13

### Added

- NYSERDA Drive Clean program.

## [1.24.1] - 2024-07-20 17:07:53

### Fixed

- Change add_variable to update_variable function.

## [1.24.0] - 2024-07-19 20:13:51

### Added

- Maryland state SNAP minimum benefits.

## [1.23.1] - 2024-07-19 00:40:56

### Fixed

- 2020 Single income tax bracket.

## [1.23.0] - 2024-07-18 23:21:40

### Added

- Remove NY Child Tax Credit age minimum for 2023.

## [1.22.1] - 2024-07-18 19:53:37

### Fixed

- Adjust the ctc_qualifying_child to reflect the age requirement.

## [1.22.0] - 2024-07-17 18:24:10

### Added

- UBI marriage bonus structure.

## [1.21.0] - 2024-07-14 16:03:45

### Added

- DC Child Tax Credit.
- DC Child Tax Credit reform.

## [1.20.0] - 2024-07-12 16:05:37

### Added

- New Jersey SNAP minimum allotment.

## [1.19.0] - 2024-07-12 10:11:42

### Added

- Estate tax.

## [1.18.0] - 2024-07-12 03:51:02

### Added

- Update SNAP income utility expense deduction amounts.

## [1.17.1] - 2024-07-11 16:05:44

### Changed

- Updated version of tables.

## [1.17.0] - 2024-07-10 19:28:55

### Added

- DC disability income exclusion.

## [1.16.3] - 2024-07-10 16:44:14

### Added

- Expand free school categorical eligibility to foster, homeless, migrant, and runaway children.

## [1.16.2] - 2024-07-09 12:45:04

### Fixed

- 2018 federal EITC parameter values.

## [1.16.1] - 2024-07-09 02:52:07

### Fixed

- 2023 EITC joint bonus parameter value.

## [1.16.0] - 2024-07-08 13:14:25

### Added

- New York State Working Families Tax Credit reform.

## [1.15.0] - 2024-07-08 11:55:38

### Added

- 2023 New York tax rules.

## [1.14.0] - 2024-07-07 23:49:09

### Added

- Halve joint EITC phase out rate reform.

## [1.13.0] - 2024-07-03 19:51:24

### Added

- Change MS charitable contributions credit from WIDOW to SURVIVING_SPOUSE.

## [1.12.0] - 2024-07-02 21:36:44

### Added

- New York State Geothermal Energy System Credit.

## [1.11.0] - 2024-07-02 18:45:27

### Added

- Student loan above the line deduction.

## [1.10.0] - 2024-07-02 17:35:57

### Added

- Mississippi 2023, 2024, and 2025 tax rates.
- Mississippi charitable contributions credit.

## [1.9.0] - 2024-07-02 12:50:48

### Added

- DC Additional SNAP minimum allotment.

## [1.8.0] - 2024-07-02 02:10:58

### Added

- Maryland 2023 income tax updates.

## [1.7.0] - 2024-07-02 00:42:34

### Added

- Maine 2023 tax rules.
- Maine tax parameters uprating.
- Refactor Maine property tax fairness credit.

## [1.6.0] - 2024-07-02 00:35:30

### Added

- Moving DC SNAP temporary local benefit code.

## [1.5.2] - 2024-07-02 00:30:47

### Fixed

- Change the parameter input in the CT rebate reduction start from WIDOW to SURVIVING_SPOUSE.

## [1.5.1] - 2024-07-01 20:57:08

### Fixed

- Oklahoma EITC refundability.

## [1.5.0] - 2024-07-01 13:54:35

### Added

- Montgomery County Local EITC.

## [1.4.0] - 2024-06-28 03:25:40

### Added

- 2023 Illinois policy parameter updates.

## [1.3.0] - 2024-06-27 11:42:31

### Added

- Connecticut 2022 temporary child tax rebate.

## [1.2.0] - 2024-06-27 03:27:43

### Added

- Update the SNAP uprating based on the June 2024 CBO forecast.

## [1.1.0] - 2024-06-26 17:53:48

### Added

- Add the New York Residential Solar Tax to the net income tree.

## [1.0.0] - 2024-06-26 17:11:51

### Added

- Support for Python 3.11.

## [0.796.1] - 2024-06-26 00:53:07

### Added

- Move rounding metadata to individual breakdown parameters.

## [0.796.0] - 2024-06-25 02:39:47

### Changed

- Update CPI-U and CPI-W parameters based on the CBO June 2024 Projections.

## [0.795.0] - 2024-06-25 01:14:35

### Added

- Hawaii standard deduction increases.
- Hawaii tax bracket increases.

## [0.794.2] - 2024-06-21 18:32:22

### Fixed

- Limit DC SNAP minimum allotment to eligible applicants.

## [0.794.1] - 2024-06-21 16:07:00

### Fixed

- Remove unneeded personal_interest_expense variable.

## [0.794.0] - 2024-06-20 15:16:19

### Added

- New York Solar Energy Systems Equipment Credit.

## [0.793.0] - 2024-06-20 14:58:39

### Added

- Add 2023 Minnesota Tax Rules.

## [0.792.0] - 2024-06-20 01:35:16

### Added

- North Dakota 2023 tax rules.
- North Dakota taxes legal code references.
- North Dakota tax parameters uprating.

## [0.791.0] - 2024-06-19 16:51:13

### Added

- Projections from June 2024 CBO baseline.

## [0.790.0] - 2024-06-18 12:58:34

### Added

- Variables used by Tax-Calculator but not PolicyEngine in the IRS PUF.

## [0.789.0] - 2024-06-14 09:40:28

### Added

- San Francisco working families tax credit.

## [0.788.0] - 2024-06-12 15:18:35

### Added

- Colorado EITC match increase beginning in 2024, recently legislated.

## [0.787.0] - 2024-06-11 20:39:03

### Fixed

- Fix New Jersey property tax credit income eligibility logic

## [0.786.0] - 2024-06-11 15:00:02

### Added

- Utah child tax credit.
- 2023 Utah earned income tax credit match increase.

## [0.785.2] - 2024-06-11 12:11:14

### Fixed

- Adjust the Minnesota phase-out rate to reflect the legal code.

## [0.785.1] - 2024-06-10 21:18:51

### Fixed

- Adjust the state income tax to include tax before refundable credits and refundable credits.
- Create a state withheld income tax variable.

## [0.785.0] - 2024-06-10 16:50:58

### Added

- Adjust the New Mexico refundable credits parameter files.

## [0.784.0] - 2024-06-10 16:45:35

### Added

- Minnesota child and working families tax credits.

### Fixed

- Minnesota working families tax credit parameter structure.

## [0.783.0] - 2024-06-08 01:49:40

### Added

- Colorado family affordability tax credit.

## [0.782.0] - 2024-06-07 20:27:00

### Added

- Rename medicaid_income to medicaid_magi.

## [0.781.0] - 2024-06-07 16:21:49

### Added

- Add Oregon state uprating.

## [0.780.2] - 2024-06-07 13:52:30

### Fixed

- Zero out the taxable social security base income thresholds for separate filers who cohabitated.

## [0.780.1] - 2024-06-07 01:04:14

### Fixed

- Arkansas income tax rates.

## [0.780.0] - 2024-06-05 17:25:11

### Added

- Illinois Child Tax Credit Reform.

## [0.779.2] - 2024-06-04 21:01:00

### Fixed

- Add New Mexico and New Jersey credits to the net income tree.

## [0.779.1] - 2024-06-04 00:24:56

### Fixed

- Round Arkansas deduction allocation fraction to nearest whole percent.

## [0.779.0] - 2024-06-03 17:08:14

### Added

- Remove Social Security from the Montana additions parameter.
- Pin core to <2.22.

## [0.778.0] - 2024-05-31 11:59:03

### Added

- Add Montana taxable social security benefits.
- Fix Montana agi formula.

## [0.777.7] - 2024-05-30 13:22:45

### Fixed

- Arkansas tax unit itemizes decision based on the federal itemization.
- Create a separate Virginia deductions variable.

## [0.777.6] - 2024-05-26 01:22:36

### Fixed

- Add health insurance premiums to SNAP excess medical expense deduction.

## [0.777.5] - 2024-05-24 19:15:18

### Fixed

- Self-employment income not available after initial microdata year.

## [0.777.4] - 2024-05-24 13:34:27

### Fixed

- Randomness in baseline tax results across model runs.

## [0.777.3] - 2024-05-24 12:51:32

### Fixed

- Bug causing State taxes to not have effects in microsimulations.

## [0.777.2] - 2024-05-22 17:28:57

### Fixed

- Adjust the Los Angeles income types to exclude basic income.

## [0.777.1] - 2024-05-21 16:34:59

### Added

- Automatic version updating for household API

## [0.777.0] - 2024-05-18 09:25:41

### Added

- Weekly hours worked.

## [0.776.0] - 2024-05-16 23:47:24

### Added

- Retirement Savings Contributions Credit (Saver’s Credit).

## [0.775.2] - 2024-05-16 22:53:29

### Fixed

- Uncap real estate taxes in the Virginia itemized deduction logic.

## [0.775.1] - 2024-05-15 02:01:54

### Fixed

- Adjust the Alabama legal code references.

## [0.775.0] - 2024-05-14 21:12:56

### Added

- Income disregard for CHP+

## [0.774.0] - 2024-05-14 16:51:18

### Added

- Update core to 2.21.5.

## [0.773.0] - 2024-05-14 14:58:17

### Added

- Backfill empty changelog entries.

## [0.772.0] - 2024-05-14 14:53:14

### Added

- Add venv and .venv to .gitignore.

## [0.771.0] - 2024-05-14 14:16:18

### Added

- 2023 Missouri tax rules.

## [0.770.1] - 2024-05-14 13:17:04

### Fixed

- Increase the Arkansas capital gains loss cap parameter value.

## [0.770.0] - 2024-05-10 15:49:10

### Added

- Hawaii 2023 income tax parameters.

## [0.769.0] - 2024-05-09 13:03:58

### Added

- Create distinct Louisiana CDCC refundable and non-refundable variables.

## [0.768.1] - 2024-05-09 11:37:29

### Added

- Ability for users to provide the PUF data input files.

## [0.768.0] - 2024-05-09 02:48:07

### Added

- 2023 Vermont Tax Rules.

## [0.767.0] - 2024-05-08 15:28:13

### Added

- CBO elasticities for labor supply.
- Self-employment income responses.

## [0.766.0] - 2024-05-07 18:56:59

### Added

- Make the Louisiana EITC and CDCC refundable.

## [0.765.0] - 2024-05-07 15:23:31

### Added

- Alabama 2023 tax rules.

## [0.764.0] - 2024-05-07 12:04:33

### Added

- 2023 Massachusetts Tax Rules.

## [0.763.0] - 2024-05-07 01:17:04

### Added

- Other housing costs beyond rent for SNAP.

## [0.762.0] - 2024-05-06 23:33:21

### Added

- Bump core to 2.20.0.

## [0.761.0] - 2024-05-06 17:53:18

### Fixed

- Countable income now includes the spouse's income when both the head and spouse are eligible.

## [0.760.0] - 2024-05-06 15:07:09

### Added

- Macro impact caching for key variables.

## [0.759.1] - 2024-05-06 01:19:28

### Fixed

- Allocate the Mississippi itemized deductions optimally between spouses.

## [0.759.0] - 2024-05-06 01:15:16

### Added

- Allocate the Montana dependent exemptions after the application of the deductions and exemptions.

## [0.758.2] - 2024-05-05 21:59:45

### Fixed

- Refactor the Louisianna exempt income variable to use the federal tax deduction.

## [0.758.1] - 2024-05-05 20:28:59

### Fixed

- Performance improvements in labor supply responses.

## [0.758.0] - 2024-05-05 17:39:50

### Added

- Create a lives_in_vehicle variable to determine whether a homeless person is using their vehicle as shelter.

## [0.757.1] - 2024-05-05 12:40:28

### Fixed

- Changed parameters - `unit:years` , `unit:age` to `unit:year`

## [0.757.0] - 2024-05-02 17:30:29

### Added

- New Jersey 2023 income tax updates.

## [0.756.0] - 2024-05-02 09:02:21

### Added

- Include 403b_contributions in pre_tax_contributions.

## [0.755.0] - 2024-04-30 02:07:09

### Added

- 2023 SNAP utility allowances for Colorado

## [0.754.0] - 2024-04-29 16:34:36

### Added

- 2023 Ohio Tax Rules.

## [0.753.0] - 2024-04-29 12:59:19

### Added

- SNAP BBCE Limit Updates.

## [0.752.1] - 2024-04-26 00:39:06

### Fixed

- Reduce the Louisiana exempt income in 2021.

## [0.752.0] - 2024-04-25 19:55:16

### Added

- 2023 Idaho Tax Rules.

## [0.751.0] - 2024-04-25 19:41:13

### Added

- 2023 Utah Tax Rules.

## [0.750.4] - 2024-04-25 18:37:03

### Added

- 2023 Virginia Tax Rules.

## [0.750.3] - 2024-04-24 17:35:42

### Added

- Illinois metadata clean-up.
- Read me files.
- Removed per-vehicle payment files.

## [0.750.2] - 2024-04-24 17:29:04

### Fixed

- Prorate the Montana federal income tax deduction based on Montana AGI.

## [0.750.1] - 2024-04-24 04:49:34

### Fixed

- Add Mississippi tax unit itemizes variable.

## [0.750.0] - 2024-04-23 18:20:42

### Added

- Adjust the Missouri deductions metadata.

## [0.749.1] - 2024-04-23 17:20:45

### Fixed

- Reduce the Arkansas taxable long term capital gains by the short term capital losses.

## [0.749.0] - 2024-04-23 16:42:53

### Added

- Change the Colorado family affordability credit file name.

## [0.748.1] - 2024-04-23 06:46:02

### Fixed

- skip_existing in PyPI publish workflow

## [0.748.0] - 2024-04-23 02:11:03

### Added

- 2023 Kentucky tax rules.

## [0.747.0] - 2024-04-23 01:42:03

### Added

- 2023 West Virginia tax rules.

## [0.746.0] - 2024-04-23 01:31:48

### Added

- 2023 Louisiana tax rules.

## [0.745.0] - 2024-04-22 23:34:33

### Added

- 2023 Rhode Island Tax Rules.

## [0.744.1] - 2024-04-22 23:01:24

### Fixed

- Include the Mississippi real estate tax deduction.

## [0.744.0] - 2024-04-22 21:11:00

### Added

- IRS PUF variables under their original names.

## [0.743.1] - 2024-04-19 14:52:52

### Fixed

- Attribute the standard and itemized deductions in Montana to each spouse respectively.

## [0.743.0] - 2024-04-19 05:38:25

### Fixed

- New York household credit calculation.

## [0.742.2] - 2024-04-19 05:22:04

### Fixed

- Remove the Mississippi married filing combined logic.

## [0.742.1] - 2024-04-17 20:43:19

### Fixed

- Consolidated state level additions variables across all state models

## [0.742.0] - 2024-04-17 16:41:57

### Added

- Use CBO projection for personal exemption.

## [0.741.1] - 2024-04-17 16:09:32

### Fixed

- Arkansas capital gains tax calculations.

## [0.741.0] - 2024-04-16 18:05:04

### Added

- 2023 Oklahoma Tax Rules.

## [0.740.0] - 2024-04-16 17:55:38

### Added

- DC "Give SNAP A Raise" program.

## [0.739.0] - 2024-04-16 00:34:07

### Added

- 2023 DC Tax Rules.

## [0.738.0] - 2024-04-16 00:09:30

### Fixed

- Mississippi taxable income.

## [0.737.1] - 2024-04-15 19:08:43

### Added

- Add Old Age Pension grant standard for 2024.

## [0.737.0] - 2024-04-15 14:20:43

### Added

- Enable remaining state income tax models and include in the net income tree.

## [0.736.0] - 2024-04-14 21:21:29

### Added

- 2023 New Hampshire tax rules.

## [0.735.0] - 2024-04-14 20:10:18

### Added

- Colorado HB24-1311 Family Affordability Tax Credit.

## [0.734.1] - 2024-04-14 17:20:33

### Fixed

- Delaware itemized deduction decision logic.

## [0.734.0] - 2024-04-13 17:39:21

### Added

- Adjust the NY Empire State Child Credit to take into account the full ctc amounts.

## [0.733.1] - 2024-04-12 20:36:40

### Fixed

- Delaware _joint AGI and deductions variable attribution.

## [0.733.0] - 2024-04-12 20:25:53

### Added

- Iowa 2023-2026 tax rates.
- 2023 Iowa pension income exclusion logic.
- 2023 Iowa alternative minimum tax logic.
- Disable married filing separately on the same return in Iowa past 2023.

## [0.732.0] - 2024-04-12 20:20:03

### Added

- Include Maine to the list of modelled policies.

## [0.731.0] - 2024-04-12 14:55:04

### Added

- 2023 NYC tax rules.

## [0.730.1] - 2024-04-11 20:46:15

### Fixed

- Tax only half of long-term capital gains in Arkansas.

## [0.730.0] - 2024-04-11 18:12:49

### Added

- Michigan Expanded Deduction for Retirement and Pension Benefits.

## [0.729.1] - 2024-04-11 17:58:58

### Fixed

- Delaware itemized deductions logic.

## [0.729.0] - 2024-04-11 17:53:36

### Added

- Allocate the Delaware itemized deductions based on federal AGI.

## [0.728.0] - 2024-04-11 12:31:09

### Added

- Separate out eligibility variables for NYC STC to allow for more flexible policy modeling.

## [0.727.2] - 2024-04-11 02:29:17

### Fixed

- Floor irs_employment_income at zero.

## [0.727.1] - 2024-04-09 02:59:20

### Fixed

- Adjust the Delaware elderly or disabled exclusion to represent the case where married couples file jointly.

## [0.727.0] - 2024-04-08 03:49:34

### Added

- Fix New Mexico low income comprehensive tax rebate calculations.

## [0.726.0] - 2024-04-08 03:44:57

### Added

- Remove premium_tax_credit from household net income tree.

## [0.725.0] - 2024-04-05 00:05:29

### Added

- Arizona Cash Assistance (TANF) child eligibility.

## [0.724.0] - 2024-04-04 23:53:10

### Added

- Enable the Kentucky income tax model and include in the net income tree.

## [0.723.0] - 2024-04-04 22:18:15

### Added

- Enable the Michigan income tax model and include in the net income tree.

## [0.722.2] - 2024-04-04 16:13:37

### Fixed

- Adjust the widow filing status to surviving spouse in the gov.contrib.biden.budget_2025.capital_gains.income_threshold file.

## [0.722.1] - 2024-04-04 03:29:14

### Fixed

- Kentucky tax unit itemizes deductions logic.

## [0.722.0] - 2024-04-02 21:40:33

### Added

- Rename widow to surviving spouse.

## [0.721.1] - 2024-04-02 15:56:44

### Fixed

- Fix Virginia low-income credit calculation.
- Fix Virginia itemized deduction calculation.

## [0.721.0] - 2024-04-01 22:07:43

### Added

- 2023 Kansas Tax Rules.

## [0.720.0] - 2024-04-01 00:10:04

### Added

- Delaware 2023 income tax parameters.

## [0.719.1] - 2024-04-01 00:02:30

### Fixed

- Add taxable social security to the list of Delaware exclusions.

## [0.719.0] - 2024-03-31 22:26:12

### Added

- 2023 New Mexico Tax Rules.

## [0.718.0] - 2024-03-29 22:09:50

### Added

- Include the ky_cdcc to the net income tree.

## [0.717.0] - 2024-03-27 17:03:02

### Added

- Oregon 2023 parameter values.

## [0.716.2] - 2024-03-26 21:46:35

### Fixed

- Change LA EZ-SAVE to monthly and lag the poverty line.

## [0.716.1] - 2024-03-26 14:30:48

### Fixed

- Adjust the Michigan household resources to exclude QBI.

## [0.716.0] - 2024-03-25 22:46:18

### Added

- Enable the Connecticut income tax model and include in the net income tree.

## [0.715.0] - 2024-03-25 18:10:17

### Added

- Biden reform to tax LTCG and qualified dividends as ordinary income for high-income filers.

## [0.714.0] - 2024-03-25 15:54:18

### Fixed

- Maryland earned income tax credit.

## [0.713.3] - 2024-03-25 15:14:47

### Fixed

- Bug in filing status logic causing tax unit spouses to appear in separate returns.

## [0.713.2] - 2024-03-24 03:38:17

### Added

- Longer history and source for Social Security benefits target.

## [0.713.1] - 2024-03-22 18:58:11

## [0.713.0] - 2024-03-22 11:49:33

## [0.712.0] - 2024-03-22 01:44:40

### Added

- Enable Ohio income tax model and include in the net income tree.

## [0.711.6] - 2024-03-20 22:53:10

### Fixed

- Add the Connecticut EITC to the list of refundable credits.

## [0.711.5] - 2024-03-20 21:17:09

### Fixed

- Reduce the itemized deductions in Idaho by the SALT amount.

## [0.711.4] - 2024-03-20 19:56:27

### Fixed

- Make Arkansas childcare expense credit non-refundable.

## [0.711.3] - 2024-03-20 19:07:38

### Fixed

- Adjust the Kentucky pension income exclusion to not count pension twice.

## [0.711.2] - 2024-03-20 13:32:09

### Fixed

- Among joint filers, limit the Delaware elderly or disabled exclusion to filers with both head and spouse eligible.

## [0.711.1] - 2024-03-20 04:55:01

### Fixed

- Include the self employment deduction to the list of Michigan additions.
- Remove the self employment income from the list of household resources.
- Subtract the above the line deductions from the household resources.

## [0.711.0] - 2024-03-20 00:27:02

### Added

- 2023 North Carolina Tax Rules.

## [0.710.1] - 2024-03-19 14:53:23

### Added

- 2023 Michigan Tax Rules.

## [0.710.0] - 2024-03-19 14:27:50

### Added

- Calibration of returns by filing status.

## [0.709.0] - 2024-03-19 03:00:29

### Added

- 2023 Connecticut tax rules.

## [0.708.8] - 2024-03-19 02:52:32

### Fixed

- Allocate the Montana dependent exemptions optimally if the filing status is married filing separately.

## [0.708.7] - 2024-03-18 18:52:52

### Fixed

- Adjust the Calworks reimbursement variables to represent monthly values.

## [0.708.6] - 2024-03-17 18:48:55

### Fixed

- Remove the qualified business income deduction from the retirement credit eligibility calculation.

## [0.708.5] - 2024-03-17 15:13:36

### Added

- A defined_for statement to ca_calworks_child_care for faster execution.
- Intermediate variables for state child care subsidies.

## [0.708.4] - 2024-03-16 03:02:17

### Changed

- Break filing_status out into multiple variables.
- Simplify and test reform to repeal head of household filing status.

## [0.708.3] - 2024-03-15 21:19:02

### Fixed

- Adjust the remove_head_of_household reform to reflect the new filing_status.py logic.

## [0.708.2] - 2024-03-15 14:48:22

### Fixed

- Remove long-term capital gains from the list of Virginia subtractions.

## [0.708.1] - 2024-03-15 14:43:16

### Added

- PSL_catalog.json.

## [0.708.0] - 2024-03-15 13:29:27

### Added

- 2023 California CPI.

## [0.707.0] - 2024-03-15 12:03:13

### Added

- Update 2023 California income tax parameters.

## [0.706.0] - 2024-03-15 04:21:11

### Added

- Tuition and fees deduction.

## [0.705.0] - 2024-03-15 03:47:15

### Added

- Change the start date of SNAP uprating.

## [0.704.0] - 2024-03-15 02:24:03

### Added

- Connecticut property tax credit.

## [0.703.0] - 2024-03-14 17:21:34

### Added

- Uprate the Biden Budget Medicare and NIIT proposal thresholds.
- Cap the NIIT increase threshold at investment income.

## [0.702.0] - 2024-03-14 15:33:17

### Added

- Arizona 2023 income tax parameters.
- Arizona filing status variable.

## [0.701.0] - 2024-03-14 15:00:02

### Added

- 2023 Massachusetts Senior Circuit Breaker Credit Parameters

## [0.700.0] - 2024-03-14 13:14:33

### Added

- 2025 Budget proposal to impose an the additional Medicare tax rate and NIIT rate for high-income tax payers.

## [0.699.2] - 2024-03-14 12:29:44

### Fixed

- Utah at-home parent credit refundability and format.

## [0.699.1] - 2024-03-14 11:55:42

### Fixed

- Make the EZ save program household level and use pre-subsidy electricity expenses.

## [0.699.0] - 2024-03-13 20:24:41

### Added

- Arkansas parameter update for 2023

## [0.698.0] - 2024-03-13 15:48:05

### Added

- Los Angeles County EZ Save program.

## [0.697.2] - 2024-03-12 20:39:56

### Fixed

- Make the Connecticut personal tax credit brackets inclusive.

## [0.697.1] - 2024-03-12 15:15:31

### Fixed

- Arkansas exempt gross income components.

## [0.697.0] - 2024-03-12 02:25:22

### Added

- Retirement distributions as unearned income for SNAP, school meals, and SSI.

## [0.696.2] - 2024-03-11 23:01:08

### Fixed

- Kentucky family size tax credit.

## [0.696.1] - 2024-03-11 05:47:32

### Added

- README file to the Idaho tax parameters.

## [0.696.0] - 2024-03-10 20:31:23

### Added

- SSI and Social Security as income sources for LA County General Relief.

## [0.695.3] - 2024-03-10 19:53:56

### Fixed

- Add short term capital gains to the Michigan household resources.

## [0.695.2] - 2024-03-10 15:34:07

### Changed

- Bump policyengine-core to address uprating issue.

## [0.695.1] - 2024-03-08 21:27:20

### Fixed

- Attribute the Montana exemptions to each spouse respectively.

## [0.695.0] - 2024-03-08 03:32:43

### Fixed

- Add South Carolina 2023 income tax rules

## [0.694.0] - 2024-03-08 01:19:52

### Added

- California investment interest expense deduction.

## [0.693.1] - 2024-03-07 19:52:18

### Fixed

- Replace state income tax with estimated withholding for all states in income tax used for SALT deduction.

## [0.693.0] - 2024-03-07 16:44:16

### Changed

- California foster youth tax credit.

## [0.692.0] - 2024-03-07 15:52:31

### Added

- Colorado 2023 income tax updates.

## [0.691.1] - 2024-03-06 23:17:06

### Fixed

- Limit WIDOW filing status to widowed head with child dependents.

## [0.691.0] - 2024-03-06 21:11:12

### Added

- Limit the CDCC relevant expense deduction to 2020 amounts in Virginia.

## [0.690.0] - 2024-03-06 11:19:30

### Changed

- Calibration improvements.

## [0.689.1] - 2024-03-05 20:13:22

### Fixed

- Subtract the QBID from Idaho AGI.

## [0.689.0] - 2024-03-05 05:56:46

### Fixed

- Fix 'make install' in Makefile.

## [0.688.5] - 2024-03-05 04:27:45

### Fixed

- Remove rent from the list of Mississippi income sources.

## [0.688.4] - 2024-03-05 00:57:54

### Fixed

- Add taxable security to the list of Louisiana exemptions from AGI.

## [0.688.3] - 2024-03-05 00:49:48

### Fixed

- Remove not used haircut parameters.

## [0.688.2] - 2024-03-04 19:38:02

### Fixed

- Remove qualified_business_income_deduction_person from the list of Ohio deductions.

## [0.688.1] - 2024-03-02 18:37:00

### Fixed

- Populate Social Security dependents and survivors benefits as zero in cps.py.
- Remove uprating from Social Security dependents and survivors benefits.
- Split up SPM unit pre-subsidy childcare expenses into individual expenses.

## [0.688.0] - 2024-03-02 11:09:14

### Added

- List of Louisiana non refundable credits in a parameter file

## [0.687.0] - 2024-03-01 17:12:59

### Fixed

- Add 2024 Georgia income tax values.

## [0.686.2] - 2024-03-01 13:39:44

### Fixed

- Refactor the Utah tax rate yaml file.

## [0.686.1] - 2024-03-01 01:53:48

### Fixed

- Minnesota Working Family Credit eligibility logic.

## [0.686.0] - 2024-02-29 02:00:39

### Added

- 2023 Wisconsin income tax parameters.

## [0.685.1] - 2024-02-28 19:05:54

### Added

- Decompose snap_utility_allowance into three variables for SUA, LUA, and IUA.

## [0.685.0] - 2024-02-28 17:28:50

### Added

- Create state withheld income tax variables for all states which cause a circular reference.

## [0.684.0] - 2024-02-28 10:24:15

### Added

- CBO uprating factors for all tax parameters through 2034.

## [0.683.1] - 2024-02-27 22:54:30

### Fixed

- Replaced data download URLs for CPS and Enhanced CPS files.

## [0.683.0] - 2024-02-27 22:50:14

### Added

- Retirement income from CPS.

### Changed

- Improvements to calibration routine.

## [0.682.1] - 2024-02-26 21:59:44

### Fixed

- Limit the Idaho Grocery Credit to households not enrolled in SNAP.

## [0.682.0] - 2024-02-26 20:57:25

### Added

- Update the CalWORKs Child Care payment standard with the 2022 rates.

## [0.681.1] - 2024-02-26 20:50:21

### Fixed

- Add employee payroll tax to the reported state income tax reform.

## [0.681.0] - 2024-02-25 23:55:29

### Added

- California alternative minimum tax calculations.

## [0.680.0] - 2024-02-24 01:13:23

### Added

- Enable Idaho income tax model and include in the net income tree.

## [0.679.1] - 2024-02-24 00:03:16

### Added

- Include social security, SSI and TANF in the HUD annual income variable.

## [0.679.0] - 2024-02-23 06:10:17

### Added

- Georgia 2024 Standard Deduction Parameters.

## [0.678.2] - 2024-02-22 16:58:33

### Fixed

- Adjust the ct_social_security_benefit_adjustment variable to reflect the worksheet in the tax forms.

## [0.678.1] - 2024-02-22 15:35:37

### Fixed

- Remove formula from household_tax_before_refundable_credits and household_refundable_tax_credits.

## [0.678.0] - 2024-02-22 15:29:21

### Added

- Pennsylvania Child and Dependent Care Tax Credit.

## [0.677.0] - 2024-02-21 17:20:43

### Added

- Arizona property tax credit.

## [0.676.1] - 2024-02-21 14:48:48

### Fixed

- Apply the Louisiana exemption amount to the bottom tax bracket.

## [0.676.0] - 2024-02-21 12:23:33

### Added

- SNAP uprating (approximated by CPI-U).

## [0.675.0] - 2024-02-21 01:41:58

### Added

- Remove vectorization from the mt_head_deductions_exemptions_indiv variable.

## [0.674.0] - 2024-02-21 01:11:31

### Added

- Use adds for household_refundable_tax_credits and household_tax_before_refundable_credits.

## [0.673.0] - 2024-02-20 22:09:07

### Added

- Add pre-subsidy electricity, care, and childcare expenses.

## [0.672.1] - 2024-02-20 17:45:08

### Added

- Alternate senior renter computation of the Michigan homestead property tax credit.

## [0.672.0] - 2024-02-20 16:32:04

### Added

- Georgia 2023 Individual Income Tax Parameters.

## [0.671.1] - 2024-02-20 14:34:59

### Fixed

- Ohio retirement credit eligiblity and applicable pension income.
- Use Ohio modified income in various credits.

## [0.671.0] - 2024-02-20 05:54:45

### Added

- Poverty guideline uprating based on 12mo average CPI-U.

## [0.670.0] - 2024-02-20 05:06:07

### Added

- 2023 school meal values.
- School meal CPI uprating.

## [0.669.1] - 2024-02-20 03:35:22

### Fixed

- Adjust the Montana head deductions exemptions variable.

## [0.669.0] - 2024-02-20 00:59:09

### Added

- Enable the West Virginia state income tax model and add it to the net income tree.

## [0.668.1] - 2024-02-19 23:39:26

### Added

- Virginia child and dependent care expenses deduction.

## [0.668.0] - 2024-02-19 23:30:53

### Fixed

- Update 2024 Maximum Taxable Earnings Each Year.

## [0.667.2] - 2024-02-19 22:58:16

### Fixed

- Include pension income in the Mississippi AGI calculation.

## [0.667.1] - 2024-02-19 17:00:50

### Fixed

- Remove pension income from the MS AGI computation.

## [0.667.0] - 2024-02-19 16:36:06

### Changed

- Uprate OASDI and SSI by CPI-W.

## [0.666.1] - 2024-02-19 00:12:47

### Added

- Add the wv_homestead_excess_property_tax_credit to the state income tree.

## [0.666.0] - 2024-02-18 23:58:28

### Added

- Disabled the cdcc cap increase in 2021 for the id_household_and_dependent_care_expense_deduction.

## [0.665.0] - 2024-02-18 21:25:48

### Added

- Use income tax before non refundable credit as a comparison in the Delaware files separately variable.

## [0.664.0] - 2024-02-18 19:52:14

### Added

- Allocate the Montana deductions and exemptions optimally to the head and spouse if filing separately.

## [0.663.0] - 2024-02-18 17:45:25

### Added

- Enable the Vermont state income tax model and add it to the net income tree.

## [0.662.0] - 2024-02-18 16:36:02

### Added

- Non-chained CPI trend and forecast.

### Changed

- Uprate benefits using non-chained CPI.

## [0.661.2] - 2024-02-17 21:13:13

### Changed

- Assign households with negative income to the -1 decile.

## [0.661.1] - 2024-02-17 04:50:37

### Fixed

- Reduce the adjusted_net_capital_gain by the qualified dividend income in the vt_capital_gains_exclusion calcualtion.

## [0.661.0] - 2024-02-17 02:46:56

### Added

- AMT capital gains rates and child exemption parameters through 2024.
- AMT references.

## [0.660.0] - 2024-02-17 00:04:29

### Added

- Add Delaware married combined separate filing status.

## [0.659.0] - 2024-02-16 21:13:27

### Added

- Add Kentucky married combined separate filing status.

## [0.658.1] - 2024-02-16 04:54:04

### Fixed

- Limiting the Ohio senior citizen credit to one amount.

## [0.658.0] - 2024-02-15 17:38:14

### Added

- Pennsylvania 2023 income tax references.

## [0.657.0] - 2024-02-15 17:10:46

### Added

- Formula for the CT subtractions variable.

## [0.656.1] - 2024-02-14 18:00:30

### Fixed

- New York supplemental tax calculation.

## [0.656.0] - 2024-02-14 17:44:19

### Added

- Projections from Feb 2024 CBO baseline.

## [0.655.2] - 2024-02-13 23:39:19

### Fixed

- Oregon federal tax liability subtractions.

## [0.655.1] - 2024-02-13 18:10:07

### Fixed

- Remove the low income table calculation from the married filing separate scenario.

## [0.655.0] - 2024-02-13 18:04:02

### Added

- Virginia filing requirement variable.

## [0.654.2] - 2024-02-13 17:31:59

### Fixed

- Refactoring Colorado child-care assistance parent fee code.

## [0.654.1] - 2024-02-13 16:17:14

### Fixed

- SNAP individual utility allowances should filter to utility expenses the household incurred.

## [0.654.0] - 2024-02-13 16:00:56

### Added

- Update California SNAP parameters.

## [0.653.0] - 2024-02-12 20:55:26

### Added

- Add the homestead property tax credit to the list of refundable credits.

## [0.652.1] - 2024-02-12 18:35:09

### Fixed

- Create person-level subtractions in WV.

## [0.652.0] - 2024-02-12 03:09:26

### Added

- Michigan homestead property tax credit.

## [0.651.4] - 2024-02-12 03:02:41

### Fixed

- Adjust the Arkansas files separately formula to rely on ar_income_tax_before_non_refundable_credits comparisons.

## [0.651.3] - 2024-02-12 02:59:35

### Fixed

- Virginia age deduction calculation and taxunit level subtractions.

## [0.651.2] - 2024-02-12 01:03:25

### Fixed

- Subtract pre-tax contributions from taxable wages and salaries.

## [0.651.1] - 2024-02-11 00:35:31

### Fixed

- Arkansas low income tax variables.

## [0.651.0] - 2024-02-09 21:57:38

### Added

- Add tests to the household_refundable_tax_credits and household_tax_before_refundable_credits vars.

## [0.650.0] - 2024-02-09 14:32:01

### Added

- Populate ca_tanf_other_unearned_income.

## [0.649.0] - 2024-02-09 14:20:13

### Added

- Vermont renter credit.

## [0.648.4] - 2024-02-09 01:35:14

### Fixed

- Fix the ar_low_income_tax_joint calculation.

## [0.648.3] - 2024-02-08 21:27:43

### Fixed

- Refactored household_refundable_tax_credits and household_tax_before_refundable_credits to remove erroneous variable overwrite. household_tax_before_refundable_credits to remove erroneous variable overwrite

## [0.648.2] - 2024-02-08 18:50:37

### Fixed

- Adjusting references to Colorado Child Care Assistance Program files.

## [0.648.1] - 2024-02-08 15:55:48

### Added

- Enable the Hawaii state income tax model and add it to the net income tree.

## [0.648.0] - 2024-02-07 21:15:22

### Added

- Remove redundant formula/adds+subtracts combos.

## [0.647.1] - 2024-02-07 21:07:12

### Fixed

- Adjust the list in the oh_partial_non_refundable_credits variable.

## [0.647.0] - 2024-02-07 21:00:05

### Added

- Montana married filing separately on same form logic.

## [0.646.1] - 2024-02-07 20:51:32

### Fixed

- Avoid negative values of non_refundable_ctc.

## [0.646.0] - 2024-02-07 17:44:33

### Added

- Ohio lump sum distribution credit.

## [0.645.0] - 2024-02-07 16:40:25

### Added

- Pin policyengine-core below 2.14.

## [0.644.0] - 2024-02-06 17:23:36

### Added

- Enhanced CPS now has weights and imputations for 2024 and 2025.

## [0.643.0] - 2024-02-06 16:07:06

### Added

- Connecticut social security benefit adjustment.

## [0.642.0] - 2024-02-06 01:09:24

### Added

- Enable South Carolina state income tax model and add it to the net income tree.

## [0.641.1] - 2024-02-05 19:46:09

### Fixed

- South Carolina state tax addback.

## [0.641.0] - 2024-02-05 18:36:12

### Added

- Enable Rhode Island state income tax model and add it to the net income tree.

## [0.640.1] - 2024-02-04 22:04:16

### Fixed

- Remove capital_gains_excluded_from_taxable_income from the Rhode Island property tax credit income sources.

## [0.640.0] - 2024-02-04 20:07:05

### Added

- Married filing separately logic to the Mississippi income tax.

## [0.639.0] - 2024-02-03 01:21:48

### Added

- Idaho household and dependent care expense deduction.

## [0.638.1] - 2024-02-03 01:00:25

### Fixed

- Add the exemption amount to the senior citizen credit income calculation.

## [0.638.0] - 2024-02-02 13:15:58

### Added

- Add Idaho net capital gain deduction to the income tree.

## [0.637.6] - 2024-02-02 06:52:55

### Fixed

- Add the exemption credits to the list of non-refundable credits.

## [0.637.5] - 2024-02-01 23:29:41

### Fixed

- Oregon WFHDC variable consolidation.

## [0.637.4] - 2024-02-01 20:49:24

### Fixed

- Ohio senior citizen credit.

## [0.637.3] - 2024-02-01 18:04:08

### Fixed

- Pre subsidy rent variable.

## [0.637.2] - 2024-02-01 03:21:37

### Fixed

- Ohio joint filing credit.
- Ohio person level adjusted gross income.

## [0.637.1] - 2024-01-31 01:48:14

### Fixed

- Rhode Island retirement income subtraction calculation.

## [0.637.0] - 2024-01-31 00:26:07

### Added

- Hawaii renter credit calculation.

## [0.636.2] - 2024-01-30 20:13:53

### Fixed

- Oregon working family household and dependent care credit calculation.

## [0.636.1] - 2024-01-30 04:21:54

### Fixed

- Rhode Island property tax credit maximum amount and eligibility criteria.

## [0.636.0] - 2024-01-29 23:18:35

### Added

- California CalWORKs vehicle value limit.

## [0.635.1] - 2024-01-29 18:47:44

### Fixed

- Georgia ga_income_tax_before_refundable_credits label.

## [0.635.0] - 2024-01-29 18:12:34

### Changed

- Improved CPS previous year imputations.

## [0.634.4] - 2024-01-29 04:29:46

### Added

- 2024 federal poverty guidelines.

## [0.634.3] - 2024-01-29 01:13:40

### Fixed

- Removed duplicate NIIT addition from Louisiana federal tax deduction.

## [0.634.2] - 2024-01-29 01:05:00

### Fixed

- Idaho permanent building fund tax calculation.

## [0.634.1] - 2024-01-29 01:00:09

### Fixed

- Adjust the adds function in the hi_subtractions variable.

## [0.634.0] - 2024-01-28 19:06:09

### Added

- Enable Georgia state income tax computation.

## [0.633.4] - 2024-01-28 05:48:37

### Fixed

- Georgia itemized deduction calculation.

## [0.633.3] - 2024-01-28 03:52:36

### Fixed

- CA TANF monthly applicant income disregards.

## [0.633.2] - 2024-01-27 19:26:08

### Fixed

- Added remaining components to SPM net income.
- Inflation-index SPM-related variables.

## [0.633.1] - 2024-01-26 16:34:55

### Fixed

- LA General relief computation to include withholding rules.

## [0.633.0] - 2024-01-26 14:10:01

### Added

- Broadband subsidies from CPS.

## [0.632.0] - 2024-01-25 20:08:04

### Added

- SSI Substantial Gainful Activity

## [0.631.6] - 2024-01-25 18:46:12

### Fixed

- South Carolina two-wage-earner credit.

## [0.631.5] - 2024-01-25 17:01:06

### Fixed

- Rhode Island property tax calculation.

## [0.631.4] - 2024-01-25 14:45:34

### Fixed

- Georgia retirement subtraction income sources.

## [0.631.3] - 2024-01-25 14:18:33

### Fixed

- Idaho CTC refundability status.

## [0.631.2] - 2024-01-25 02:26:10

### Fixed

- Hawaii EITC refundability.

## [0.631.1] - 2024-01-25 00:40:23

### Fixed

- Virginia taxable income formula.

## [0.631.0] - 2024-01-23 11:52:39

### Added

- Parameter for using reported SNAP values.

## [0.630.0] - 2024-01-23 02:11:13

### Added

- Arkansas low income tax table.

## [0.629.2] - 2024-01-22 16:31:45

### Fixed

- Cap SNAP excess shelter deduction after applying utility allowance.

## [0.629.1] - 2024-01-22 16:28:34

### Fixed

- Michigan home heating credit.

## [0.629.0] - 2024-01-21 02:02:28

### Added

- Arkansas married filing separately logic.

## [0.628.0] - 2024-01-20 23:25:12

### Added

- Enable the Arizona state income tax calculation.

## [0.627.1] - 2024-01-20 17:09:14

### Fixed

- Utah taxpayer credit.

## [0.627.0] - 2024-01-20 12:57:40

### Added

- Medicaid state immigration status eligibility.

## [0.626.0] - 2024-01-19 23:23:38

### Added

- Louisiana federal tax deduction.

## [0.625.1] - 2024-01-19 05:05:00

### Fixed

- Michigan disability exemptions.

## [0.625.0] - 2024-01-18 23:25:24

### Added

- Consolidate Oregon AGI logic according to the model standards.

## [0.624.0] - 2024-01-18 12:46:05

### Added

- Virginia earned income tax credit.

## [0.623.0] - 2024-01-17 14:40:43

### Added

- CBO inflation projections.

## [0.622.1] - 2024-01-17 13:34:14

### Fixed

- Bug causing the Wyden-Smith CTC to not create in 2024.

## [0.622.0] - 2024-01-16 22:26:28

### Added

- Virginia itemized deductions.

## [0.621.0] - 2024-01-16 21:49:29

### Added

- Prior-year earnings imputation.
- Wyden-Smith CTC lookback provision.

## [0.620.3] - 2024-01-15 11:19:42

### Fixed

- West Virginia family tax credit.

## [0.620.2] - 2024-01-14 22:52:58

### Added

- Ohio adoption credit person level variable.

## [0.620.1] - 2024-01-14 19:23:50

### Fixed

- Idaho income tax rates.

## [0.620.0] - 2024-01-14 18:21:30

### Added

- Georgia non-refundable credits structure.

## [0.619.0] - 2024-01-14 03:06:31

### Added

- Add Alabama income tax to the modelled_policies.yaml file.

## [0.618.3] - 2024-01-13 22:01:49

### Fixed

- Immigration rules for CalWORKS Child Care program.

## [0.618.2] - 2024-01-13 21:11:58

### Fixed

- 2021 Rhode Island income tax brackets.

## [0.618.1] - 2024-01-12 19:56:01

### Fixed

- Virginia age deduction AGI.

## [0.618.0] - 2024-01-12 19:50:01

### Added

- Add Alabama to the net income tree.

## [0.617.2] - 2024-01-12 17:36:51

### Fixed

- Ohio adoption credit variable.

## [0.617.1] - 2024-01-12 17:18:32

### Fixed

- Hawaii taxable income formula.

## [0.617.0] - 2024-01-12 13:06:44

### Added

- Arizona 529 college savings plans subtraction.

## [0.616.0] - 2024-01-12 13:03:39

### Added

- Enable Alabama income tax structure.

## [0.615.0] - 2024-01-11 16:21:57

### Added

- Oregon working family household and dependent care credit.

## [0.614.0] - 2024-01-11 13:23:48

### Added

- Reform to phase in ACTC on a per-child basis.

## [0.613.0] - 2024-01-11 11:56:03

### Added

- Virginia spouse tax adjustment.

## [0.612.0] - 2024-01-11 10:29:17

### Added

- Ohio unreimbursed medical care expense deduction.

## [0.611.0] - 2024-01-11 08:34:23

### Added

- Fix Hawaii disabled exemption formula.

## [0.610.1] - 2024-01-10 11:27:40

### Fixed

- California CalWORKS TANF monthly income variables.

## [0.610.0] - 2024-01-10 01:10:28

### Added

- Michigan home heating credit.

## [0.609.1] - 2024-01-09 23:52:23

### Fixed

- Massachusetts 2023 rent deduction cap increase.

## [0.609.0] - 2024-01-07 22:34:28

### Added

- Idaho permanent building fund tax.

## [0.608.0] - 2024-01-07 19:10:57

### Added

- Louisiana itemized deductions.

## [0.607.0] - 2024-01-06 17:47:15

### Added

- Louisiana exemptions.

## [0.606.1] - 2024-01-06 15:23:54

### Fixed

- Removed extraneous add/subtract pairs in income_tax calculation logic.

## [0.606.0] - 2024-01-06 15:19:01

### Added

- Kentucky itemized deductions.

## [0.605.0] - 2024-01-06 13:51:28

### Added

- Montana elderly homeowner/renter credit.

## [0.604.2] - 2024-01-05 14:55:37

### Fixed

- West Virginia senior citizen or disability deduction source.

## [0.604.1] - 2024-01-04 18:24:35

### Fixed

- Arizona deductions formula.

## [0.604.0] - 2024-01-04 04:49:41

### Added

- Vermont retirement income exemption.

## [0.603.3] - 2024-01-04 01:12:31

### Fixed

- South Carolina taxable income calculation.

## [0.603.2] - 2024-01-04 01:03:25

### Fixed

- Rhode Island exemptions formula.

## [0.603.1] - 2024-01-03 22:49:51

### Fixed

- Defined CalWORKS income limit as annual.

## [0.603.0] - 2024-01-03 17:40:03

### Added

- Georgia retirement income exclusions.
- Georgia military retirement income exclusion.

## [0.602.1] - 2024-01-03 17:35:14

### Fixed

- Fix Virginia military benefits subtraction formula.

## [0.602.0] - 2024-01-03 15:31:42

### Added

- Hawaii alternative tax on capital gains.

## [0.601.2] - 2024-01-03 07:08:43

### Fixed

- 2023 Massachusetts short term capital gains.

## [0.601.1] - 2023-12-30 00:25:33

### Fixed

- Parameter computing Ohio partial non-refundable credits.

## [0.601.0] - 2023-12-29 01:48:49

### Added

- West Virginia homestead excess property tax credit.
- West Virginia gross household income.

## [0.600.1] - 2023-12-28 21:41:40

### Fixed

- Bug causing cliffs to not be calculated in SNAP.

## [0.600.0] - 2023-12-28 20:25:42

### Fixed

- is_ssi_disabled always uses the microdata.

## [0.599.0] - 2023-12-28 00:52:05

### Added

- Hawaii itemized deduction.

## [0.598.0] - 2023-12-28 00:29:20

### Added

- Populate AMI and PHA payment standard for LA County.

## [0.597.2] - 2023-12-27 01:17:17

### Fixed

- Add hdf5 to conda environment to avoid installation errors.

## [0.597.1] - 2023-12-25 00:14:47

### Added

- README.md to aca parameter folder.

## [0.597.0] - 2023-12-24 23:34:48

### Added

- Ohio joint filing credit.

## [0.596.0] - 2023-12-24 23:11:31

### Added

- West Virginia senior citizen or disability deduction.

## [0.595.3] - 2023-12-24 22:19:24

### Fixed

- Michigan retirement deduction calculation.

## [0.595.2] - 2023-12-24 01:05:33

### Fixed

- Pension income allocated at the lowest possible level.
- Bug in LSR branching setup.

## [0.595.1] - 2023-12-23 01:36:50

### Fixed

- Massachusetts 2023 EITC rate.

## [0.595.0] - 2023-12-22 16:24:22

### Added

- Disability-based UBI.

## [0.594.0] - 2023-12-22 09:59:02

### Added

- Rhode Island adjusted gross income modifications.

## [0.593.0] - 2023-12-22 05:01:15

### Added

- Arkansas retirement or disability benefits exemption.

## [0.592.0] - 2023-12-22 04:42:23

### Fixed

- South Carolina net capital gain deduction.

## [0.591.1] - 2023-12-22 01:04:14

### Fixed

- Adjust the az_aged_exemption variable formula to calculate eligibility through a defined_for attribute.

## [0.591.0] - 2023-12-21 19:05:34

### Added

- West Virginia social security benefits subtraction.

## [0.590.0] - 2023-12-21 19:02:40

### Added

- Montana disability income subtraction.

## [0.589.1] - 2023-12-21 18:46:53

### Fixed

- New York supplemental tax calculation.

## [0.589.0] - 2023-12-21 18:40:08

### Added

- Idaho aged and disabled deduction.

## [0.588.2] - 2023-12-21 18:09:07

### Fixed

- Utah social security benefits credit variable.
- Utah earned income tax credit variable.

## [0.588.1] - 2023-12-21 18:04:33

### Fixed

- Alabama itemized deduction.

## [0.588.0] - 2023-12-21 17:24:36

### Added

- Virginia Adjusted Gross Income.

## [0.587.0] - 2023-12-21 17:14:33

### Added

- Ohio Exemption Credit.
- Ohio Personal Exemptions.

## [0.586.2] - 2023-12-21 12:39:42

### Added

- Test for no-reform microsim impacts.

## [0.586.1] - 2023-12-21 07:13:29

### Fixed

- Arizona itemized deductions.

## [0.586.0] - 2023-12-20 22:28:46

### Added

- SSI 2024 updated amounts

## [0.585.2] - 2023-12-20 12:59:03

### Fixed

- Alabama itemized deductions.

## [0.585.1] - 2023-12-20 10:56:22

### Fixed

- Test failures in automated variable tests.

## [0.585.0] - 2023-12-19 11:31:05

### Added

- Income and substitution elasticities of labor supply.

## [0.584.3] - 2023-12-18 20:13:09

### Fixed

- Alabama capital gains inclusion in AGI.

## [0.584.2] - 2023-12-18 16:33:00

### Fixed

- Parameterized 25% of the Alternative Minimum Tax calculation.

## [0.584.1] - 2023-12-18 04:09:27

### Fixed

- Import all FilingStatus values when repealing head of household.

## [0.584.0] - 2023-12-18 01:50:30

### Added

- Reform for repealing head of household filing status, as Senator Romney proposed in his Family Security Act.

## [0.583.3] - 2023-12-17 23:52:20

### Fixed

- Alabama federal tax deduction.

## [0.583.2] - 2023-12-16 18:54:42

### Fixed

- Bump policyengine-core to capture random microsimulation bug fixes.

## [0.583.1] - 2023-12-16 18:18:33

### Fixed

- Set WIC take-up deterministically for individual simulations.

## [0.583.0] - 2023-12-16 03:36:40

### Added

- Massachusetts 2023 child and dependent tax credit rules.

## [0.582.2] - 2023-12-15 19:35:40

### Added

- Alabama dependent exemption.

## [0.582.1] - 2023-12-15 17:16:18

### Fixed

- Michigan standard deduction calculation.

## [0.582.0] - 2023-12-15 16:27:51

### Added

- Illinois 2022 personal exemption amount.

## [0.581.1] - 2023-12-15 14:43:19

### Fixed

- Alabama standard deduction.

## [0.581.0] - 2023-12-15 14:37:23

### Added

- Montana social security benefit adjustment.

## [0.580.1] - 2023-12-15 14:22:33

### Fixed

- Connecticut pension subtraction.

## [0.580.0] - 2023-12-15 12:21:47

### Added

- Alabama income tax variable formula.

## [0.579.1] - 2023-12-14 19:03:15

### Fixed

- Maine child care credit format.

## [0.579.0] - 2023-12-14 18:51:52

### Added

- Alabama adjusted gross income.

## [0.578.0] - 2023-12-14 18:21:47

### Added

- Idaho retirement benefit deductions.

## [0.577.0] - 2023-12-14 17:57:39

### Added

- Montana federal income tax deduction.

## [0.576.1] - 2023-12-13 23:57:10

### Fixed

- Arizona AGI long-term capital gains subtraction.

## [0.576.0] - 2023-12-13 23:49:32

### Added

- Idaho 2023 income tax rate.

## [0.575.0] - 2023-12-12 19:14:28

### Fixed

- Connecticut alternative minimum tax.

## [0.574.1] - 2023-12-12 19:08:33

### Fixed

- South Carolina senior exemption.

## [0.574.0] - 2023-12-12 16:17:08

### Added

- California CalWORKs.

## [0.573.0] - 2023-12-12 04:40:40

### Added

- California CARE and FERA integration tests.

## [0.572.0] - 2023-12-11 16:19:00

### Added

- Arkansas itemized deductions.

## [0.571.2] - 2023-12-11 12:15:20

### Fixed

- Tax abolition bug.

## [0.571.1] - 2023-12-11 04:51:50

### Fixed

- Invalid Montana EITC rate YAML.

## [0.571.0] - 2023-12-11 03:04:06

### Added

- Virginia taxable income.

## [0.570.4] - 2023-12-11 02:21:11

### Fixed

- Montana 2023 earned income tax credit rate.

## [0.570.3] - 2023-12-11 02:10:02

### Fixed

- Los Angeles county General Relief disability eligibility.

## [0.570.2] - 2023-12-11 01:41:43

### Fixed

- Arizona adjusted gross income subtractions.

## [0.570.1] - 2023-12-11 01:32:26

### Fixed

- Montana income tax brackets and rates.

## [0.570.0] - 2023-12-10 19:11:01

### Added

- Montana child tax credit.

## [0.569.0] - 2023-12-10 00:10:48

### Added

- Montana child and dependent care expense deduction.

## [0.568.0] - 2023-12-09 23:29:06

### Added

- Montana taxable income.

## [0.567.0] - 2023-12-09 21:58:18

### Added

- Add formulas for Arizona income tax credits.

## [0.566.0] - 2023-12-09 21:15:31

### Added

- Michigan income tax variable formula.

## [0.565.0] - 2023-12-08 21:11:34

### Changed

- Backdate Alabama parameter values to 2021.

## [0.564.1] - 2023-12-08 11:43:18

### Fixed

- Michigan Miscellaneous subtractions section 22 income.

## [0.564.0] - 2023-12-07 11:59:21

### Added

- Arizona exemptions.

## [0.563.1] - 2023-12-07 03:33:31

### Fixed

- 2021 South Carolina tax bracket parameters.

## [0.563.0] - 2023-12-06 19:28:36

### Added

- Montana old age subtraction.

## [0.562.0] - 2023-12-06 18:10:30

### Added

- Kentucky personal tax credits.

## [0.561.1] - 2023-12-06 18:01:17

### Fixed

- Remove Maine index file.

## [0.561.0] - 2023-12-06 17:41:47

### Added

- Connecticut additions and subtractions.

## [0.560.0] - 2023-12-06 17:21:04

### Changed

- Colorado EITC to 50% for 2023 due to new legislation.

## [0.559.0] - 2023-12-05 18:11:49

### Added

- Michigan additions and subtractions.

## [0.558.1] - 2023-12-05 16:37:05

### Fixed

- Bug in LA general relief.

## [0.558.0] - 2023-12-05 14:34:03

### Added

- Vermont charitable contributions credit.

## [0.557.0] - 2023-12-05 01:54:33

### Added

- General Relief Program (GR) - Los Angeles County.

## [0.556.0] - 2023-12-04 15:27:14

### Added

- Arkansas personal tax credits.

## [0.555.1] - 2023-12-04 14:52:43

### Fixed

- Military retirement pay variable.

## [0.555.0] - 2023-12-04 12:21:44

### Added

- Michigan standard deduction and pension benefit.

## [0.554.1] - 2023-12-04 06:37:53

### Fixed

- Fix NYC School Tax Credit Rate Reduction Amount Income Limit parameter label.

## [0.554.0] - 2023-12-04 00:58:18

### Added

- Montana tuition subtraction.

## [0.553.1] - 2023-12-03 05:10:35

### Fixed

- Basic income taxability bool unit.

## [0.553.0] - 2023-12-03 04:41:43

### Added

- Add formula for the ky_taxable_income variable.

## [0.552.2] - 2023-12-02 19:32:01

### Changed

- Moved DC in alphabetical order.

## [0.552.1] - 2023-12-02 17:16:11

### Fixed

- South Carolina young child deduction and tax rate.

## [0.552.0] - 2023-12-01 21:12:49

### Added

- Add Hawaii income tax calculation logic.

## [0.551.0] - 2023-12-01 08:38:03

### Added

- Vermont minimum income tax.

## [0.550.0] - 2023-12-01 08:12:56

### Added

- Hawaii military reserve or national guard duty pay exclusion.

## [0.549.0] - 2023-12-01 08:10:00

### Fixed

- Updated Virginia 2021 parameter values.

## [0.548.0] - 2023-12-01 05:02:13

### Added

- Alabama federal income tax deduction.

## [0.547.0] - 2023-12-01 04:21:59

### Fixed

- South Carolina young child exemption.

## [0.546.1] - 2023-11-30 18:10:45

### Fixed

- Relocate some ACA parameters to clarify their role.
- Rename one ACA variable to clarify its role.

## [0.546.0] - 2023-11-30 02:27:14

### Added

- Montana itemized deductions.

## [0.545.0] - 2023-11-30 02:19:29

### Added

- Delaware itemized deductions.

## [0.544.0] - 2023-11-30 02:16:16

### Added

- Idaho grocery credit.

## [0.543.0] - 2023-11-29 21:19:00

### Added

- Improved ACA premium tax credit for California.

## [0.542.0] - 2023-11-29 20:52:16

### Added

- South Carolina income tax.

## [0.541.1] - 2023-11-28 18:49:38

### Fixed

- Clean up years in system.py.
- Update default computation year to 2023.

## [0.541.0] - 2023-11-28 18:30:28

### Changed

- Fix definition of income used to calculate Maine fairness credits.

## [0.540.0] - 2023-11-28 11:23:21

### Fixed

- Bug preventing reforms from working with a Core update.

## [0.539.0] - 2023-11-27 23:23:24

### Added

- Vermont elderly or permanently totally disabled tax credit.

## [0.538.2] - 2023-11-27 22:53:52

### Fixed

- Downgrade policyengine-core to fix Microsimulation bug.

## [0.538.1] - 2023-11-26 14:23:47

### Fixed

- Hawaii CDCC min head spouse earned variable.

## [0.538.0] - 2023-11-23 18:53:34

### Added

- South Carolina dependent exemption.
- South Carolina subtractions.
- South Carolina additions.

## [0.537.1] - 2023-11-22 01:31:58

### Fixed

- Ohio senior citizen credit formula.

## [0.537.0] - 2023-11-22 00:37:55

### Added

- Ohio lump sum retirement credit.

## [0.536.1] - 2023-11-20 23:32:21

### Fixed

- Fix UT retirement credit birth year parameter.

## [0.536.0] - 2023-11-20 14:46:37

### Changed

- Add missing 2021 Utah parameter values.
- Utah retirement credit fixed.

## [0.535.1] - 2023-11-17 21:05:55

### Added

- Twelve new CalEITC integration tests.

## [0.535.0] - 2023-11-17 17:46:39

### Added

- Hawaii child and dependent care expenses tax credit.

## [0.534.0] - 2023-11-15 20:45:57

### Added

- Replicated Child and Dependent Care Expenses Credit to include California limitations.

## [0.533.1] - 2023-11-15 20:42:44

### Fixed

- Duplicate Ohio income tax parameter name deductions.

## [0.533.0] - 2023-11-15 19:02:07

### Added

- Ohio AGI additions and deductions parameters and variables.

## [0.532.0] - 2023-11-15 06:28:33

### Added

- Kentucky tuition tax credit.

## [0.531.0] - 2023-11-15 06:22:47

### Added

- Montana senior interest income exclusion.

## [0.530.1] - 2023-11-14 23:03:24

### Fixed

- The temporary presence of `earned_income_tax_credit` by removing it, leaving the `eitc` variable as the sole representation of the federal Earned Income Credit.

## [0.530.0] - 2023-11-14 20:34:35

### Added

- Ohio 529 plan deduction.

## [0.529.0] - 2023-11-13 21:25:39

### Added

- Rhode Island exemptions.

## [0.528.0] - 2023-11-13 15:13:28

### Added

- Kentucky adjusted gross income.

## [0.527.0] - 2023-11-12 00:23:31

### Added

- 2024 income tax brackets.

## [0.526.0] - 2023-11-10 15:59:43

### Added

- Hawaii exemptions.

## [0.525.0] - 2023-11-10 15:51:59

### Added

- West Virginia low-income earned income exclusion.

## [0.524.0] - 2023-11-09 16:00:28

### Added

- Maryland hundred year subtraction.

## [0.523.1] - 2023-11-09 01:19:56

### Fixed

- Disable Maine Tax.

## [0.523.0] - 2023-11-09 00:11:58

### Added

- Alabama itemized deductions.

## [0.522.0] - 2023-11-08 21:44:31

### Added

- South Carolina retirement deduction.
- South Carolina military retirement deduction.

## [0.521.0] - 2023-11-08 01:44:09

### Added

- Idaho non-refundable credits file.

## [0.520.0] - 2023-11-07 23:06:52

### Fixed

- 2021 Maine income tax parameters.

## [0.519.0] - 2023-11-06 22:47:48

### Added

- West Virginia low-income family tax credit.

## [0.518.5] - 2023-11-06 15:27:19

### Fixed

- Re-added earned_income_tax_credit variable alias.

## [0.518.4] - 2023-11-05 21:04:11

### Fixed

- Presence of unneeded taxcalc-related logic in the `system.py` module.

## [0.518.3] - 2023-11-04 21:16:41

### Fixed

- pell_grant_efc now can not be negative

## [0.518.2] - 2023-11-04 21:02:59

### Fixed

- Remove obsolete taxcalc-related alias variable names.
- Rename `earned_income_tax_credit` to `eitc` to be more consistent with variable names for other federal credits.

## [0.518.1] - 2023-11-03 20:53:44

### Fixed

- ZIP code bug for households with axes.

## [0.518.0] - 2023-11-03 20:30:48

### Fixed

- ZIP codes are sampled from the state, and axes-containing simulations don't vary the ZIP code.

## [0.517.0] - 2023-11-03 20:12:54

### Added

- The `net_capital_gains` variable (formerly `c23650`).
- The `gov/irs/capital_gains/loss_limit.yaml` parameter file.
- The `loss_limited_net_capital_gains` variable (formerly `c01000`) that uses the `loss_limit` parameter.

## [0.516.3] - 2023-11-03 04:08:02

### Fixed

- Added USD metadata to co_ccap_subsidy.

## [0.516.2] - 2023-11-02 22:14:02

### Fixed

- CCAP fix for multi-child households (previously had index errors).

## [0.516.1] - 2023-11-02 20:44:02

### Fixed

- Automatically set entry process to true for CCAP.

## [0.516.0] - 2023-11-02 17:49:15

### Added

- Arizona military retirement subtraction.

## [0.515.0] - 2023-11-02 01:02:06

### Added

- Idaho capital gains deduction.

## [0.514.3] - 2023-11-01 21:47:32

### Fixed

- Remove obsolete variables from the `gov/irs/taxcalc/sources.py` module.
- Remove obsolete variables from the `gov/irs/taxcalc/outputs.py` module.

## [0.514.2] - 2023-11-01 18:48:50

### Fixed

- Various bugs in Colorado CCAP.

## [0.514.1] - 2023-11-01 11:27:38

### Fixed

- Colorado CCAP bug with individual simulations.

## [0.514.0] - 2023-11-01 02:15:09

### Added

- Colorado child care assistance program (CCCAP).

## [0.513.3] - 2023-10-31 22:16:07

### Fixed

- Remove obsolete xtot variable left over from original taxcalc development.

## [0.513.2] - 2023-10-31 20:32:49

### Fixed

- Renamed `exemptions` variable to `exemptions_count`.
- Renamed `c04600` variable to `exemptions`.

## [0.513.1] - 2023-10-31 15:33:49

### Fixed

- Location of `state_and_local_sales_or_income_tax` variable module.
- Presence of unused `filer_e18400` variable.

## [0.513.0] - 2023-10-30 12:33:37

### Added

- Eliminate cap on Maryland childless EITC amount beginning in 2023.

## [0.512.0] - 2023-10-28 17:35:45

### Added

- Reform for the Taxable Earnings for Social Security Payroll Taxes, including an upper threshold and increasing the taxable amount.

## [0.511.0] - 2023-10-28 16:48:11

### Added

- Oklahoma income tax to net income tree.

## [0.510.0] - 2023-10-23 15:52:44

### Added

- West Virginia subtractions.

## [0.509.0] - 2023-10-22 21:46:44

### Added

- Delaware income tree.

## [0.508.4] - 2023-10-20 22:40:37

### Fixed

- Formula for tax_unit_medicaid_income_level variable.

## [0.508.3] - 2023-10-20 04:10:36

### Fixed

- Integrated year-specific Poverty Tracker variables.

## [0.508.2] - 2023-10-19 19:21:03

### Fixed

- Louisiana military pay exclusion folder structure.

## [0.508.1] - 2023-10-19 17:00:51

### Fixed

- Change co_chp parameters to be at or before 2023-01-01

## [0.508.0] - 2023-10-19 13:58:32

### Fixed

- Added Kentucky pension income exclusion.

## [0.507.1] - 2023-10-18 22:44:35

### Fixed

- Add missing 2021 Idaho 5.5% income tax bracket.

## [0.507.0] - 2023-10-18 20:13:39

### Added

- Seven empty state ??_income_tax.py variables.
- All states to the state_income_taxes.py adds list.

## [0.506.1] - 2023-10-17 22:47:08

### Fixed

- Adjust Georgia variable folder structure.

## [0.506.0] - 2023-10-17 14:53:55

### Added

- Georgia deductions.

## [0.505.0] - 2023-10-16 19:13:31

### Added

- Delaware pension exclusion.

## [0.504.0] - 2023-10-16 18:16:36

### Added

- Connecticut pension or annuity income subtraction.

## [0.503.1] - 2023-10-15 23:47:31

### Fixed

- Formula for tax_unit_medicaid_income_level variable.

## [0.503.0] - 2023-10-15 22:06:59

### Added

- Vermont child tax credit.

## [0.502.1] - 2023-10-14 14:11:49

### Fixed

- Definition of Medicaid/CHIP/ACA-related modified adjusted gross income (MAGI).

## [0.502.0] - 2023-10-13 16:13:43

### Added

- Vermont child and dependent care credit.

## [0.501.1] - 2023-10-12 22:02:21

### Fixed

- Move maine adjusted gross income folder.

## [0.501.0] - 2023-10-12 19:53:13

### Added

- Maine sales tax fairness credits.
- Maine property tax fairness credits.

## [0.500.0] - 2023-10-11 13:37:15

### Added

- Tax unit head or spouse varibale.

## [0.499.0] - 2023-10-10 23:24:10

### Added

- Hawaii subtractions.

## [0.498.0] - 2023-10-10 16:55:30

### Added

- Connecticut military retirement subtraction.

## [0.497.2] - 2023-10-07 11:55:34

### Fixed

- Missing tests of cliff_gap and cliff_evaluated variables.

## [0.497.1] - 2023-10-07 11:49:55

### Fixed

- Missing unit tests and delta parameter for marginal_tax_rate variable.

## [0.497.0] - 2023-10-06 23:43:31

### Added

- Mississippi adjusted gross income.

## [0.496.0] - 2023-10-06 23:26:28

### Added

- West Virginia senior citizens tax credit.
- West Virginia homestead exemption.

## [0.495.0] - 2023-10-06 23:18:37

### Added

- Vermont capital gain exclusion.

## [0.494.1] - 2023-10-06 18:37:54

### Fixed

- Update Colorado TABOR parameters for 2023.

## [0.494.0] - 2023-10-05 14:43:50

### Fixed

- SNAP now uses the previous October's FPG.

## [0.493.1] - 2023-10-05 01:05:40

### Fixed

- Georgia investment in 529 plan deduction variable name adjustment.

## [0.493.0] - 2023-10-04 21:03:41

### Added

- Arizona increased standard deduction for charitable contributions.

## [0.492.0] - 2023-10-04 04:44:55

### Added

- Montana net capital gain credit.

## [0.491.0] - 2023-10-04 02:24:19

### Added

- South Carolina net capital gain deduction.

## [0.490.0] - 2023-10-04 01:21:16

### Added

- Arizona long-term capital gains subtraction.

## [0.489.1] - 2023-10-04 01:08:56

### Fixed

- Deductions subtracted from id_taxable_income.

## [0.489.0] - 2023-10-03 14:18:18

### Added

- Georgia adjusted gross income structure.

## [0.488.1] - 2023-10-03 04:26:23

### Fixed

- Add unemployment compensation to list of benefits.

## [0.488.0] - 2023-10-02 22:45:10

### Added

- West Virginia low-income family tax credit.

## [0.487.0] - 2023-10-02 12:59:39

### Added

- Vermont interest from u.s. obligation & student loan interest agi subtraction.

## [0.486.0] - 2023-10-02 00:05:46

### Added

- SNAP 2023 parameters.

## [0.485.0] - 2023-09-29 22:17:41

### Added

- Vermont medical expense deduction.

## [0.484.0] - 2023-09-29 21:46:02

### Added

- Idaho partial subtractions.

## [0.483.0] - 2023-09-29 05:35:10

### Added

- Ohio adoption credit.

## [0.482.2] - 2023-09-28 19:35:20

### Fixed

- North Carolina income tree patch.

## [0.482.1] - 2023-09-28 17:28:07

### Fixed

- Add Louisiana index file.
- Remove Missouri index file.

## [0.482.0] - 2023-09-27 21:57:34

### Added

- Connecticut state tuition subtraction.

## [0.481.0] - 2023-09-27 18:22:39

### Added

- Arkansas income tax exemptions.

## [0.480.0] - 2023-09-27 17:44:45

### Added

- Idaho deductions.

## [0.479.1] - 2023-09-25 21:27:04

### Fixed

- Remove tax exempt form 4972 lump sum distribution variable.

## [0.479.0] - 2023-09-25 17:18:37

### Added

- DC single-joint tax threshold ratio reform switch.

## [0.478.0] - 2023-09-24 17:57:29

### Added

- Arizona itemized deduction.

## [0.477.0] - 2023-09-24 17:33:25

### Added

- Arizona pension exclusion.

## [0.476.1] - 2023-09-24 05:33:57

### Fixed

- North Carolina index files.
- North Carolina missing legislative references.

## [0.476.0] - 2023-09-24 03:22:24

### Added

- Vermont earned income tax credit.

## [0.475.0] - 2023-09-23 21:48:12

### Added

- A non_mortgage_interest variable.
- A formula for interest_expense variable that adds mortgage_interest and non_mortgage_interest variables.

## [0.474.0] - 2023-09-22 19:30:12

### Added

- Arkansas inflation relief income-tax credit.

## [0.473.0] - 2023-09-22 19:22:49

### Added

- North Carolina itemized deductions.
- North Carolina income tree.

## [0.472.0] - 2023-09-22 10:21:41

### Added

- Population by state to calibration routines.

## [0.471.1] - 2023-09-21 12:36:13

### Fixed

- Remove two unused variables in variables/gov/irs/taxcalc/deductions/standard directory.

## [0.471.0] - 2023-09-21 12:28:34

### Added

- Arkansas child and dependent care credit.

## [0.470.1] - 2023-09-20 17:44:51

### Fixed

- Colorado income tax model formatting.

## [0.470.0] - 2023-09-19 14:45:39

### Added

- Kentucky family size tax credit.

## [0.469.0] - 2023-09-15 19:38:29

### Added

- Child Health Plan Plus

## [0.468.0] - 2023-09-15 04:34:13

### Added

- Louisiana military pay exclusion.

## [0.467.0] - 2023-09-15 04:21:57

### Added

- Pell Grant automatic 0 EFC and marginal tax rate brackets from 2009 to 2023.

## [0.466.1] - 2023-09-14 19:23:32

### Fixed

- Unfocused scope of the test coverage report.

## [0.466.0] - 2023-09-14 19:17:47

### Added

- Mississippi income tax schedule.

## [0.465.3] - 2023-09-14 19:11:54

### Fixed

- Moved NJ tax index.yaml file from NJ to NJDHS.

## [0.465.2] - 2023-09-14 17:41:30

### Added

- Documentation page with example on income distributions.

## [0.465.1] - 2023-09-13 13:17:04

### Fixed

- Documentation dependency errors.

## [0.465.0] - 2023-09-12 23:29:59

### Added

- Rhode Island property tax credit.

## [0.464.1] - 2023-09-12 22:51:02

### Fixed

- Colorado CTC and EITC changes for 2024 enacted in House Bill 23-1112.
- Colorado CTC logic.

## [0.464.0] - 2023-09-12 21:49:59

### Added

- Added PovertyTracker microdata.

## [0.463.0] - 2023-09-12 16:15:02

### Changed

- CPS updated to 2022 from 2021.

## [0.462.3] - 2023-09-08 00:44:17

### Added

- Add Colorado to the household_state_income_tax variable.

## [0.462.2] - 2023-09-07 16:31:01

### Fixed

- Removed Colorado tax index.yaml file.

## [0.462.1] - 2023-09-07 14:51:52

### Fixed

- Rename module to be same as the name of the variable it contains.

## [0.462.0] - 2023-09-07 12:43:44

### Added

- Colorado state income tax addback.

## [0.461.1] - 2023-09-06 18:19:32

### Fixed

- Replace several arcane variable names with more descriptive names.

## [0.461.0] - 2023-09-06 15:59:55

### Added

- Arizona dependent tax credit.

## [0.460.1] - 2023-09-06 12:32:42

### Fixed

- Moved regular_tax_before_credits formula into the alternative_income_tax.py module, which is the only place it is used.

## [0.460.0] - 2023-09-05 16:48:36

### Added

- Rhode Island standard deduction phaseout.

## [0.459.0] - 2023-09-04 23:28:52

### Added

- Delaware itemized deductions.

## [0.458.2] - 2023-09-04 20:59:54

### Fixed

- Georgia standard deduction file directory.

## [0.458.1] - 2023-09-04 20:23:16

### Fixed

- Absence of federal Alternative Minimum Tax in capped_cdcc formula.
- Code fragmentation in Colorado child care expense credit calculations.
- Implausible allocation of total care expenses to Colorado eligible children.

## [0.458.0] - 2023-09-04 16:05:48

### Added

- Ohio Retirement Income Credit.

## [0.457.0] - 2023-09-04 03:10:10

### Added

- Louisiana school readiness tax credit.

## [0.456.0] - 2023-09-04 00:58:13

### Added

- Georgia standard deduction.

## [0.455.0] - 2023-09-03 04:25:25

### Added

- Vermont AGI Additions.

## [0.454.0] - 2023-09-03 02:06:23

### Added

- Federal capped cdcc for Colorado low income cdcc calculation.

## [0.453.0] - 2023-09-02 21:41:03

### Added

- Several North Carolina deduction variables to allow integration testing.

## [0.452.1] - 2023-09-02 15:57:13

### Fixed

- Presence of an unused Colorado income tax variable.
- Presence of unneeded Colorado EITC calculations.

## [0.452.0] - 2023-09-02 01:22:31

### Added

- Connecticut earned income tax credit.

## [0.451.0] - 2023-09-01 16:37:16

### Added

- Colorado pension subtraction income sources.

## [0.450.0] - 2023-08-31 12:12:22

### Added

- Colorado sales tax refund.

## [0.449.0] - 2023-08-30 02:00:19

### Added

- Mississippi itemized deductions.

## [0.448.0] - 2023-08-30 01:35:56

### Added

- Delaware elderly or disabled income exclusion.

## [0.447.1] - 2023-08-29 23:00:41

### Fixed

- North Carolina income tax rate for 2022.

## [0.447.0] - 2023-08-29 20:14:03

### Added

- Several placeholder Georgia income-related variables to allow integration testing.

## [0.446.0] - 2023-08-29 19:55:49

### Added

- Colorado additions.
- Colorado state income tax model.

## [0.445.0] - 2023-08-29 19:46:48

### Added

- Montana exemptions.

## [0.444.0] - 2023-08-29 15:29:09

### Added

- Placeholder Colorado taxable income additions and subtractions variables.
- Colorado taxable income formula.

### Fixed

- Colorado income tax rates for 2021 and 2022.

## [0.443.0] - 2023-08-26 18:43:41

### Added

- Colorado subtractions.

## [0.442.0] - 2023-08-25 02:22:42

### Added

- Placeholder Connecticut AGI additions and subtractions variables.

### Fixed

- Connecticut add_back/start parameter value for single filers.

## [0.441.0] - 2023-08-24 18:24:21

### Added

- Colorado low-income child care expenses credit.

## [0.440.0] - 2023-08-24 18:09:56

### Added

- Maryland Senior Tax Credit.

## [0.439.1] - 2023-08-23 18:48:27

### Fixed

- Inaccurate Vermont income tax rates.

## [0.439.0] - 2023-08-23 12:28:50

### Added

- Colorado income qualified senior housing income tax credit.

## [0.438.0] - 2023-08-22 18:21:25

### Added

- Arizona family tax credit.

## [0.437.1] - 2023-08-21 20:28:33

### Fixed

- 2023 Maryland CTC fix.

## [0.437.0] - 2023-08-21 11:38:54

### Added

- Adjust the connecticut personal credit rate file.

## [0.436.0] - 2023-08-21 04:31:08

### Added

- Hawaii low income household renters tax credit.

## [0.435.0] - 2023-08-21 01:17:10

### Added

- Colorado child tax credit.

## [0.434.0] - 2023-08-20 21:15:46

### Added

- Connecticut credit based on AGI

## [0.433.0] - 2023-08-20 20:35:47

### Added

- Louisiana EITC.
- Louisiana main rates.
- Louisiana CDCC.

## [0.432.0] - 2023-08-20 17:05:13

### Added

- Legal code references and historical parameters for DC Keep Child Care Affordable Tax Credit.

## [0.431.3] - 2023-08-20 04:42:13

### Fixed

- Avoid divide by zero in Pell Grant EFC formula.

## [0.431.2] - 2023-08-19 17:31:51

### Fixed

- Removed unused no_salt_income_tax variable.

## [0.431.1] - 2023-08-19 05:01:28

### Added

- README and index.yaml files to Department of Education and other parameter folders.

## [0.431.0] - 2023-08-19 04:39:37

### Added

- Indiana AGI tax rate for 2023.

### Changed

- Labels and descriptions for Indiana tax parameters.
- Use real_estate_taxes variable for Indiana homeowner's property tax deduction.

## [0.430.0] - 2023-08-18 23:46:07

### Added

- Pell Grant

## [0.429.1] - 2023-08-18 22:43:37

### Fixed

- Calculation of Oregon federal income tax subtraction.

## [0.429.0] - 2023-08-18 21:35:17

### Added

- Connecticut personal income tax schedule.
- Connecticut personal exemption.

## [0.428.1] - 2023-08-18 20:08:04

### Added

- 2023 Maryland CTC parameters.
- Maryland refundable CTC.

## [0.428.0] - 2023-08-18 15:03:20

### Added

- Indiana in_income_tax variable
- Indiana decoupled EITC variables and parameters

## [0.427.1] - 2023-08-18 14:46:22

### Fixed

- Calculation of Oregon retirement income credit.

## [0.427.0] - 2023-08-18 03:57:15

### Added

- West Virginia public pension subtraction.

## [0.426.0] - 2023-08-17 18:53:59

### Added

- Contributed reforms to the DC Keep Child Care Affordable Tax Credit.

## [0.425.1] - 2023-08-17 18:12:58

### Fixed

- Misallocation of state refundable tax credit-affecting reforms' revenues.

## [0.425.0] - 2023-08-17 15:19:18

### Added

- Oregon retirement credit.

## [0.424.1] - 2023-08-17 05:29:22

### Fixed

- New Jersey property tax deduction/credit logic.

## [0.424.0] - 2023-08-15 18:19:47

### Added

- Hawaii Food/Excise Tax Credit.

## [0.423.2] - 2023-08-15 17:21:08

### Added

- New Jersey total income variable (allowing simplification of exclusion formulas).

## [0.423.1] - 2023-08-13 16:18:26

### Fixed

- New Jersey 2021 income tax parameter values.

## [0.423.0] - 2023-08-11 17:35:41

### Added

- North Carolina child credit.

## [0.422.0] - 2023-08-10 01:19:35

### Added

- Add New Jersey pension/retirement and other retirement income exclusions.

## [0.421.0] - 2023-08-10 01:08:32

### Added

- South Carolina State Tax Addback.

## [0.420.1] - 2023-08-10 01:01:50

### Changed

- Eliminated the use of the term subtractions in the New Mexico metadata.

## [0.420.0] - 2023-08-09 23:56:01

### Added

- Arkansas Personal Income Tax Schedule.

## [0.419.0] - 2023-08-09 23:21:44

### Added

- Vermont main income tax rate.

## [0.418.0] - 2023-08-09 18:49:35

### Added

- Idaho income tax schedule.

## [0.417.3] - 2023-08-09 14:01:59

### Fixed

- DeLauro contrib parameter README.

## [0.417.2] - 2023-08-09 12:23:11

### Added

- Kentucky 2021 income tax rate.

## [0.417.1] - 2023-08-08 23:41:51

### Fixed

- Make DC married filing separately on same return option a bool instead of list.

## [0.417.0] - 2023-08-08 21:04:05

### Added

- District of Columbia (DC) income tax policy parameter that controls whether married joint taxpayers have the option to compute DC taxes separately.

## [0.416.2] - 2023-08-08 17:03:08

### Fixed

- Household state income tax variable respects reported state tax switch.

## [0.416.1] - 2023-08-08 16:22:12

### Fixed

- Incorrect Missouri itemized deduction logic.

## [0.416.0] - 2023-08-08 04:31:30

### Added

- Oregon Child Tax Credit.

## [0.415.0] - 2023-08-08 01:03:41

### Added

- Georgia exemptions.

## [0.414.0] - 2023-08-08 01:00:06

### Added

- Michigan earned income tax credit.

## [0.413.0] - 2023-08-08 00:47:11

### Added

- Arizona increased excise tax credit.

## [0.412.0] - 2023-08-08 00:37:25

### Added

- Georgia low income credits.

## [0.411.0] - 2023-08-07 22:34:47

### Added

- Kentucky household and dependent care service credit.

## [0.410.2] - 2023-08-07 18:19:00

### Changed

- Hide Idaho and Arkansas parameter folders.

## [0.410.1] - 2023-08-07 01:18:18

### Changed

- Adjusted the page references in pdf files for the New Mexico income tax programs.

## [0.410.0] - 2023-08-06 22:29:59

### Added

- Idaho child tax credit.

## [0.409.3] - 2023-08-06 17:03:06

### Fixed

- Lack of documentation on Maryland itemized deduction rule.

## [0.409.2] - 2023-08-06 15:41:27

### Fixed

- Nebraska itemized deduction rule.

## [0.409.1] - 2023-08-05 20:37:53

### Fixed

- Oklahoma itemized deduction rule.

## [0.409.0] - 2023-08-05 03:01:43

### Added

- Montana Standard Deduction.

## [0.408.0] - 2023-08-04 21:19:33

### Added

- Arkansas standard deduction.

## [0.407.1] - 2023-08-04 20:07:35

## [0.407.0] - 2023-08-03 06:11:59

### Added

- South Carolina two wage earner credit.

## [0.406.0] - 2023-08-03 05:43:23

### Added

- Michigan Exemptions.

## [0.405.0] - 2023-08-03 05:20:50

### Added

- Check/improve reference for New Mexico AGI subtractions.

## [0.404.0] - 2023-08-03 01:17:19

### Added

- Delaware additional standard deduction.
- Fixed aged personal credit structure.

## [0.403.3] - 2023-08-02 18:03:26

### Fixed

- New Mexico child day care credit.

## [0.403.2] - 2023-08-02 13:58:43

### Fixed

- Equivalised household income is household income-based rather than SPM income-based.

## [0.403.1] - 2023-08-02 03:34:56

### Changed

- Spelled out acronyms in parameter folder README files.

## [0.403.0] - 2023-08-02 01:18:20

### Added

- Vermont standard deductions.

## [0.402.0] - 2023-08-01 01:30:32

### Added

- Mississippi total exemptions.

## [0.401.5] - 2023-07-31 22:39:09

### Fixed

- Base New Mexico deduction for certain dependents on total dependents, rather than child dependents.

## [0.401.4] - 2023-07-31 17:25:46

### Added

- More recently completed state income tax models to modelled_policies.yaml.

## [0.401.3] - 2023-07-31 16:55:39

### Added

- README files to tax credit parameters.

## [0.401.2] - 2023-07-31 15:59:35

### Fixed

- Include New Mexico deduction for certain dependents in New Mexico deductions.

## [0.401.1] - 2023-07-30 16:30:59

### Fixed

- Add blind and aged exemptions for New Mexico low income comprehensive tax rebate.

## [0.401.0] - 2023-07-28 15:22:00

### Added

- Tie NM EITC age eligibility to federal rules except for 18-24 inclusion.

## [0.400.0] - 2023-07-28 02:36:06

### Added

- New Mexico income tax parameter visibility.

## [0.399.0] - 2023-07-28 02:18:59

### Added

- New Jersey income tax to net income tree.

## [0.398.0] - 2023-07-28 01:51:38

### Added

- 2023 New Jersey Child Tax Credit update.

## [0.397.0] - 2023-07-28 00:48:34

### Added

- Colorado child care expense credit.

## [0.396.0] - 2023-07-27 14:50:30

### Added

- Arizona personal income tax schedule.

## [0.395.0] - 2023-07-27 14:02:37

### Added

- Rhode Island EITC.

## [0.394.0] - 2023-07-27 12:55:39

### Added

- Rhode Island Credit for child and dependent care.

## [0.393.0] - 2023-07-27 04:39:54

### Added

- Colorado Personal Income Tax Schedule.

## [0.392.0] - 2023-07-26 20:48:21

### Added

- Delaware additional personal credits.

## [0.391.0] - 2023-07-26 20:32:28

### Added

- New Mexico AGI and Additions.
- Add New Mexico to income tree.

## [0.390.1] - 2023-07-26 16:45:19

### Fixed

- Error-prone {short,long}_term_capital_losses variables by removing them.

## [0.390.0] - 2023-07-26 16:33:04

### Added

- household_state_income_tax variable to solve circular dependencies.

## [0.389.1] - 2023-07-25 16:31:29

### Fixed

- Fragmentation of circular-logic error avoidance.

## [0.389.0] - 2023-07-25 14:08:11

### Added

- Kentucky standard deduction.

## [0.388.0] - 2023-07-25 12:39:07

### Added

- New Mexico child day care credit.

## [0.387.1] - 2023-07-24 17:23:30

### Added

- Display of DC parameters.

## [0.387.0] - 2023-07-24 16:39:00

### Added

- New Mexico deduction for certain dependents.
- New Mexico 2021 income tax rebate.
- New Mexico additional 2021 income tax rebate.
- New Mexico supplemental 2021 income tax rebate.

## [0.386.0] - 2023-07-22 01:49:59

### Added

- New Mexico child income tax credit.

## [0.385.0] - 2023-07-21 22:19:18

### Added

- New Mexico social security income exemption.

## [0.384.0] - 2023-07-21 21:42:08

### Added

- New Mexico net capital gain deduction.

## [0.383.0] - 2023-07-21 21:17:52

### Added

- New Mexico unreimbursed medical expense credit.
- New Mexico unreimbursed medical expense exemption.

## [0.382.0] - 2023-07-21 15:45:32

### Added

- New Mexico hundred year exemption.

## [0.381.0] - 2023-07-21 13:49:06

### Added

- New Mexico Medical Care Expense Deduction.

## [0.380.0] - 2023-07-21 03:54:46

### Added

- New Mexico low income comprehensive tax rebate.

## [0.379.0] - 2023-07-21 03:12:51

### Added

- New Mexico low- and middle-income exemption.

## [0.378.0] - 2023-07-21 03:03:35

### Added

- PA TANF pregnancy eligibility.

## [0.377.1] - 2023-07-20 19:24:35

### Fixed

- State income tax itemized deduction code duplication.

## [0.377.0] - 2023-07-20 19:12:53

### Added

- Vermont personal exemption.

## [0.376.0] - 2023-07-20 18:58:58

### Added

- Virginia total exemptions.

## [0.375.0] - 2023-07-20 18:55:01

### Added

- New Mexico blind and aged exemption.

## [0.374.0] - 2023-07-20 18:45:21

### Added

- New Mexico property tax rebate.

## [0.373.0] - 2023-07-20 13:31:37

### Added

- New Mexico working families credit.

## [0.372.0] - 2023-07-19 19:22:25

### Added

- Added Ohio Child Care and Dependent Care Credit.
- Added Ohio Senior Citizen Credit.

## [0.371.0] - 2023-07-19 15:52:37

### Added

- Wisconsin state income tax.

## [0.370.1] - 2023-07-19 13:13:44

### Fixed

- DC property tax credit corner cases with negative federal AGI.

## [0.370.0] - 2023-07-18 22:26:55

### Added

- New Mexico Itemized Deductions.

## [0.369.0] - 2023-07-18 20:46:28

### Added

- District of Columbia (DC) state income tax.

## [0.368.1] - 2023-07-17 23:07:18

### Fixed

- DC TANF parameter values and references.

## [0.368.0] - 2023-07-17 21:01:41

### Added

- Reform for the 2023 American Family Act, including a baby bonus.

## [0.367.0] - 2023-07-16 21:14:44

### Added

- Delaware personal credits.

## [0.366.0] - 2023-07-16 15:14:02

### Added

- Delaware EITC.

## [0.365.0] - 2023-07-15 13:12:33

### Added

- Hawaii EITC.

## [0.364.1] - 2023-07-14 04:26:18

### Added

- Updated Maine parameters to include 2021 tax year values.

## [0.364.0] - 2023-07-13 21:30:09

### Added

- Delaware standard deduction.

## [0.363.0] - 2023-07-13 20:28:21

### Added

- New Mexico Personal Income Tax Schedule.

## [0.362.0] - 2023-07-13 05:06:26

### Added

- Ohio Non public school credit.

## [0.361.0] - 2023-07-12 14:08:34

### Added

- New Hampshire income tax to net income tree.

## [0.360.1] - 2023-07-12 11:35:25

### Added

- Change Maine pre-phaseout standard deduction to equal the federal standard deduction.

## [0.360.0] - 2023-07-10 21:27:49

### Added

- Scott Winship EITC reform.

## [0.359.1] - 2023-07-10 18:16:02

### Fixed

- Array divide-by-zero warnings in household/spmunit income decile variable tests by moving the tests.

## [0.359.0] - 2023-07-10 12:24:29

### Added

- Integrate Maine income tax into net income.

## [0.358.1] - 2023-07-10 00:57:09

### Added

- Renamed ssbenefits.yaml to taxable_social_security.yaml

## [0.358.0] - 2023-07-08 15:17:06

### Added

- Add logic for Maine itemized deductions.

## [0.357.2] - 2023-07-08 14:58:40

### Fixed

- Use eitc_relevant_investment_income variable in eitc_eligible formula to eliminate code duplication.

## [0.357.1] - 2023-07-06 18:49:09

### Added

- Metadata to incomplete parameter subtrees indicating they don't affect economy and household.

## [0.357.0] - 2023-07-06 04:52:15

### Added

- Pennsylvania TANF age eligibility.

## [0.356.0] - 2023-07-04 12:42:02

### Added

- Virginia military benefit subtraction.

## [0.355.0] - 2023-07-04 12:33:34

### Added

- Pennsylvania TANF resource limit.

## [0.354.0] - 2023-07-04 02:35:17

### Added

- Vermont taxable income.

## [0.353.0] - 2023-07-04 00:59:54

### Added

- 2021 NH exemption parameter values.

## [0.352.0] - 2023-07-04 00:13:18

### Added

- Subtraction of exemptions in calculation of NH taxable income.

### Fixed

- Calculation of NH old-age exemption amount.

## [0.351.0] - 2023-07-03 22:17:34

### Added

- New Hampshire Exemptions.

## [0.350.1] - 2023-07-03 15:11:47

### Fixed

- Array divide-by-zero warnings in hud_income_level formula.

## [0.350.0] - 2023-07-03 04:00:22

### Added

- South Carolina CDCC.

## [0.349.0] - 2023-07-03 03:53:37

### Added

- Indiana unified elderly tax credit.

## [0.348.2] - 2023-07-03 03:49:40

### Fixed

- Lowercase Age variable.

## [0.348.1] - 2023-07-03 03:23:08

### Fixed

- Updated Colorado SNAP parameters.
- Deduct child support from SNAP net income in all states.
- Deduct child support from SNAP gross income in certain states previously deducted from net income only.

## [0.348.0] - 2023-07-03 01:54:59

### Added

- South Carolina Senior Exemption.

## [0.347.1] - 2023-07-03 01:44:43

### Fixed

- Array divide-by-zero warnings in residential_efficiency_electrification_rebate formula.

## [0.347.0] - 2023-07-03 01:41:44

### Added

- South Carolina Earned Income Tax Credit.

## [0.346.4] - 2023-07-03 01:28:34

### Fixed

- Array divide-by-zero warnings in ssi_unearned_income_deemed_from_ineligible_parent formula.

## [0.346.3] - 2023-07-03 01:25:42

### Fixed

- Array divide-by-zero warnings in tax_unit_childcare_expenses formula.

## [0.346.2] - 2023-07-01 20:40:02

### Fixed

- Array divide-by-zero warnings in NYC local income tax code.

## [0.346.1] - 2023-07-01 18:42:32

### Fixed

- Array divide-by-zero warning in IA income tax code.

## [0.346.0] - 2023-06-30 02:00:30

### Added

- Ohio Earned Income Tax Credit.

## [0.345.12] - 2023-06-29 20:40:02

### Fixed

- Numpy array divide warning in taxable_social_security.py module.

## [0.345.11] - 2023-06-29 20:36:18

### Fixed

- Numpy array divide warning in ma_limited_income_tax_credit module.

## [0.345.10] - 2023-06-29 20:29:05

### Fixed

- Numpy array divide warning in md_two_income_subtraction module.

## [0.345.9] - 2023-06-29 20:21:22

### Fixed

- Numpy array divide warning in mo_pension_and_ss_or_ssd_deduction_section_b module.

## [0.345.8] - 2023-06-29 20:14:24

### Fixed

- Numpy array divide warning in mo_pension_and_ss_or_ssd_deduction_section_c module.

## [0.345.7] - 2023-06-29 20:05:36

### Fixed

- Numpy array divide warning in mo_taxable_income module.

## [0.345.6] - 2023-06-29 19:57:47

### Fixed

- Numpy array divide warnings in mo_qualified_health_insurance_premiums module.

## [0.345.5] - 2023-06-29 19:28:53

### Fixed

- Numpy array divide warnings in mo_net_state_income_taxes module.

## [0.345.4] - 2023-06-29 19:20:39

### Fixed

- Numpy array divide warning in ok_child_care_child_tax_credit module.

## [0.345.3] - 2023-06-29 19:17:23

### Fixed

- Presence of unnecessary 'import numpy' and 'import warn' statements by removing them.

## [0.345.2] - 2023-06-29 19:14:10

### Fixed

- Numpy array divide warning in ok_eitc module.

## [0.345.1] - 2023-06-29 16:17:02

### Fixed

- Add Iowa income tax to net income tree.
- Add readmes to state parameter folders.

## [0.345.0] - 2023-06-29 13:51:42

### Fixed

- Montana EITC.

## [0.344.0] - 2023-06-29 13:46:58

### Added

- Missing 2021 NH state income tax rate.

## [0.343.0] - 2023-06-29 09:40:04

### Changed

- Added scipy as explicit dependency and fixed version to downgraded 1.10.1

## [0.342.0] - 2023-06-28 02:08:31

### Added

- Mississippi personal standard deduction.

## [0.341.0] - 2023-06-26 02:49:08

### Added

- Georgia dependent care credit.

## [0.340.0] - 2023-06-26 00:25:29

### Added

- Mississippi aged and blind exemptions.

## [0.339.1] - 2023-06-24 19:55:52

### Fixed

- Incorrect allocation of tax-unit real estate taxes to persons in Iowa AMT logic.

## [0.339.0] - 2023-06-23 17:41:32

### Added

- Delaware cdcc.

## [0.338.0] - 2023-06-23 02:46:38

### Added

- Virginia Age Deduction

## [0.337.1] - 2023-06-22 00:40:11

### Fixed

- Missing rental_income as source of Iowa gross income.

## [0.337.0] - 2023-06-20 21:40:43

### Added

- Georgia personal income tax rate schedule.

## [0.336.0] - 2023-06-20 21:15:16

### Added

- New Hampshire Education Tax Credit.

## [0.335.1] - 2023-06-18 20:18:56

### Fixed

- Iowa exemption credit logic for head-of-household filing units.

## [0.335.0] - 2023-06-12 15:05:19

### Fixed

- West Virginia tax rate schedule.

## [0.334.0] - 2023-06-08 22:01:14

### Added

- Working Families Tax Cut Act parameters.

## [0.333.1] - 2023-06-08 15:10:11

### Added

- Federal AGI by income source.

## [0.333.0] - 2023-06-06 15:49:45

### Added

- Vermont AGI.

## [0.332.0] - 2023-06-05 02:11:50

### Changed

- Delaware personal income tax rate.

## [0.331.1] - 2023-05-31 23:59:55

### Fixed

- Missing taxable_social_security in list of NJ AGI subtractions relative to federal AGI.

## [0.331.0] - 2023-05-31 23:56:45

### Added

- Rhode Island Standard Deduction.

## [0.330.1] - 2023-05-31 02:23:18

### Fixed

- Add six states to list used by state_income_tax formula.

## [0.330.0] - 2023-05-30 16:14:28

### Added

- Old Age Pension

## [0.329.4] - 2023-05-30 06:23:37

### Fixed

- Incorrect logic in federal tax_unit_itemizes formula.

## [0.329.3] - 2023-05-29 00:20:03

### Fixed

- A bug causing itemization to be too frequently chosen.

## [0.329.2] - 2023-05-28 17:06:47

### Fixed

- Divide by zero in NYC CDCC.

## [0.329.1] - 2023-05-27 18:05:33

### Fixed

- Divide-by-zero error in ia_prorate_fraction.

## [0.329.0] - 2023-05-27 16:33:26

### Added

- New Hampshire income tax schedule.

## [0.328.0] - 2023-05-27 15:54:35

### Added

- Iowa state income tax.

## [0.327.0] - 2023-05-27 05:42:06

### Added

- Montana personal income tax schedule.

## [0.326.0] - 2023-05-27 05:39:37

### Added

- North Carolina income tax schedule.

## [0.325.0] - 2023-05-27 05:06:06

### Added

- Adjust New Jersey property tax deduction/credit for separate but cohabitating.

## [0.324.0] - 2023-05-27 04:37:24

### Added

- Python 3.10 support.

## [0.323.0] - 2023-05-26 02:04:07

### Added

- New Jersey income tax formula.

## [0.322.0] - 2023-05-25 19:14:24

### Added

- Colorado SSI State Supplement

## [0.321.0] - 2023-05-25 05:21:32

### Added

- Kentucky income tax rate.

## [0.320.1] - 2023-05-23 07:48:13

### Changed

- Core bump.

## [0.320.0] - 2023-05-23 04:13:36

### Added

- Michigan income tax rate.

## [0.319.0] - 2023-05-22 16:56:40

### Added

- New Jersey property tax deduction or credit.

## [0.318.0] - 2023-05-21 02:07:26

### Added

- Rhode Island personal income tax schedule.

## [0.317.1] - 2023-05-18 14:42:51

### Added

- Federal and state AGI calibration data for tax year 2020.
- AGI and income tax statistics for high-income taxpayers by top 1%, 5%, and 10% of returns for tax year 2020.

## [0.317.0] - 2023-05-16 03:46:12

### Added

- Switch to branch to determine itemization.

## [0.316.1] - 2023-05-16 02:34:19

## [0.316.0] - 2023-05-10 22:25:05

### Changed

- Itemization decisions now use deduction size, not liability change for speed.
- Added defined_fors for optimisation.

## [0.315.0] - 2023-05-10 02:34:49

### Added

- Virginia federal state employees subtraction, empty state_or_federal_salary variable file.

## [0.314.1] - 2023-05-05 02:49:29

### Added

- Legal reference for Nebraska CDCC, EITC, AGI reduction by SSB, and extra standard deduction.

## [0.314.0] - 2023-05-04 19:37:30

### Added

- New Jersey main income tax.

## [0.313.1] - 2023-05-04 15:28:04

### Added

- Federal payroll tax

## [0.313.0] - 2023-05-04 00:04:47

### Added

- Update Kansas Legal Reference for AGI and CDCC.

## [0.312.0] - 2023-05-03 23:46:50

### Added

- Mississippi regular exemption.

## [0.311.0] - 2023-05-03 21:35:09

### Added

- Mississippi dependents allowance

## [0.310.2] - 2023-05-03 19:02:41

### Added

- Legal code reference for North Nakota Tax Credits

## [0.310.1] - 2023-05-01 03:21:40

### Fixed

- Removed Maryland refundable EITC match drop from 45% to 28%, reflecting recent legislation.

## [0.310.0] - 2023-04-30 15:12:21

### Added

- Virginia disability income subtraction.

## [0.309.0] - 2023-04-28 20:10:09

### Added

- New Jersey TANF gross earned income.

## [0.308.0] - 2023-04-28 19:05:33

### Added

- Maine AGI Subtractions.

## [0.307.0] - 2023-04-28 03:08:20

### Added

- Modify description

## [0.306.0] - 2023-04-28 03:02:45

### Added

- New Jersey TANF Gross Unearned Income.

## [0.305.0] - 2023-04-28 02:57:49

### Fixed

- New Jersey TANF maximum allowable income.

## [0.304.0] - 2023-04-28 02:43:27

### Fixed

- NJ TANF maximum benefit.

## [0.303.1] - 2023-04-27 11:28:42

### Fixed

- Reorganised local level area variables.

## [0.303.0] - 2023-04-27 01:54:06

### Added

- New Jersey EITC and New Jersey EITC eligiblity (different age parameters).

## [0.302.0] - 2023-04-26 12:07:09

### Added

- Self-employment tax abolition switch.

### Fixed

- Some OK households had NaN net income.

## [0.301.2] - 2023-04-26 02:13:48

### Added

- Change NYC CDCC age restriction unit from currency to year.

## [0.301.1] - 2023-04-25 04:39:43

### Added

- Edited NYC EITC variable label.

## [0.301.0] - 2023-04-24 21:15:38

### Added

- Populate is_nyc from the CPS.

### Changed

- Rename fips to state_fips.

## [0.300.4] - 2023-04-24 16:18:02

### Added

- Legal code reference for Kansas Tax Credits

## [0.300.3] - 2023-04-24 16:01:05

### Added

- Legal reference for NE CDCC and EITC.

## [0.300.2] - 2023-04-24 15:57:07

### Added

- Legislative reference for North Dakota income tax rates.

## [0.300.1] - 2023-04-24 11:58:18

### Fixed

- NYC CDCC qualifying childcare share does not return NaN.

## [0.300.0] - 2023-04-24 05:59:47

### Added

- Hawaii rate structure.

## [0.299.0] - 2023-04-22 05:13:27

### Added

- Merged 3 onboarding materials into one file for future references.

## [0.298.0] - 2023-04-22 00:43:40

### Added

- New Jersey TANF maximum allowable income.

## [0.297.0] - 2023-04-21 15:52:35

### Added

- DC TANF to net income tree.
- README files for new states.

## [0.296.0] - 2023-04-20 19:07:10

### Added

- DC TANF program.

## [0.295.1] - 2023-04-20 15:28:54

### Changed

- 2021 SSI and TANF data by federal and state level.

## [0.295.0] - 2023-04-17 15:44:00

### Added

- Maine standard, itemized, and overall deduction.

## [0.294.0] - 2023-04-16 23:56:05

### Added

- NJ child tax credit.

## [0.293.1] - 2023-04-16 15:33:21

### Changed

- Fixed README.md display on PyPI.

## [0.293.0] - 2023-04-16 10:06:18

### Fixed

- Removed a microdata test that was failing due to download requirements.

## [0.292.0] - 2023-04-15 18:19:59

### Added

- Utah SS Benefits Credit.
- Utah retirement credit.
- Utah EITC.
- Utah at-home parent credit.

## [0.291.0] - 2023-04-15 10:49:00

### Added

- CPS racial category.
- Top-level racial category (4 categories).

## [0.290.0] - 2023-04-15 09:31:34

### Added

- Utah State income tax.

## [0.289.0] - 2023-04-15 03:01:12

### Added

- Washington TANF resource limit.

## [0.288.0] - 2023-04-15 01:06:27

### Added

- ME Child Care Credit, refundable and nonrefundable portion.

## [0.287.0] - 2023-04-15 00:25:24

### Added

- Hawaii standard deduction.

## [0.286.2] - 2023-04-14 10:05:46

### Changed

- CalEITC reimplemented without branching and without bug.

## [0.286.1] - 2023-04-13 16:18:46

### Changed

- CalEITC reimplemented without branching.

## [0.286.0] - 2023-04-13 02:15:59

### Added

- DC standard deduction.

## [0.285.1] - 2023-04-11 19:35:40

### Fixed

- Subtraction error in EITC joint bonus.

## [0.285.0] - 2023-04-11 04:46:52

### Added

- Oklahoma state income tax.

## [0.284.0] - 2023-04-11 04:11:43

### Added

- New Jersey CDCC.

## [0.283.0] - 2023-04-11 04:09:36

### Added

- Minnesota state income tax.

## [0.282.0] - 2023-04-10 21:13:07

### Added

- Virginia military basic pay subtraction.

## [0.281.1] - 2023-04-10 16:22:22

### Added

- Legislative reference for California mental health services tax.

## [0.281.0] - 2023-04-10 03:21:40

### Added

- ME main income tax (before credits and supplemental tax)

## [0.280.0] - 2023-04-08 04:35:49

### Added

- New Jersey taxable income.

## [0.279.0] - 2023-04-07 16:22:50

### Added

- New York TANF resource limit.
- New York TANF to general TANF variable.

### Fixed

- Multiply New York TANF flat earned income disregard by 12.

## [0.278.0] - 2023-04-06 18:22:11

### Added

- Arizona standard deduction.

## [0.277.0] - 2023-04-05 23:18:07

### Added

- Modify file name for earned income

## [0.276.0] - 2023-04-05 16:25:35

### Added

- South Carolina income tax before credits.

## [0.275.0] - 2023-04-05 03:08:10

### Added

- New York TANF demographic and income eligibility

## [0.274.0] - 2023-04-04 22:47:27

### Added

- Ohio AGI deductions

## [0.273.0] - 2023-04-04 14:16:28

### Added

- New York TANF gross unearned income

## [0.272.0] - 2023-04-04 14:04:35

### Added

- New York TANF flat income disregard.

## [0.271.0] - 2023-04-04 04:32:08

### Added

- New Jersey total exemptions.

## [0.270.0] - 2023-04-04 02:09:32

### Added

- Virginia income tax rate and blank Virginia income tax variable file.

## [0.269.0] - 2023-04-03 18:48:55

### Added

- New Jersey dependent attending college exemption.

## [0.268.0] - 2023-04-03 17:24:53

### Added

- Nebraska state income tax.

## [0.267.0] - 2023-04-03 16:13:54

### Added

- South Carolina young child exemption.

## [0.266.0] - 2023-04-02 16:55:48

### Added

- North Dakota state income tax.

## [0.265.0] - 2023-04-02 15:07:00

### Added

- Earned income for new york tanf.

## [0.264.0] - 2023-04-02 02:13:21

### Added

- Maine dependent exemption.

## [0.263.5] - 2023-04-01 15:19:26

### Fixed

- is_ssi_disabled variable.

## [0.263.4] - 2023-03-31 06:18:36

### Fixed

- Apply EITC married filing separately limitation.

## [0.263.3] - 2023-03-30 21:40:37

### Fixed

- Lowered SSI asset limit pass rate to 8.8%.

## [0.263.2] - 2023-03-30 16:04:37

### Fixed

- CPS url updated to fix poverty rate bug.

## [0.263.1] - 2023-03-30 05:13:18

### Fixed

- California CDCC formula, which previously doubly applied the federal CDCC rate.

## [0.263.0] - 2023-03-30 04:13:27

### Added

- Maine taxable income.

## [0.262.0] - 2023-03-30 01:37:19

### Added

- Kansas state income tax.

## [0.261.1] - 2023-03-29 23:22:36

### Changed

- Pin pydata-sphinx-theme==0.13.1 to fix jupyterbook build.

## [0.261.0] - 2023-03-29 23:06:13

### Added

- Ohio AGI addition and deduction.

## [0.260.1] - 2023-03-29 20:36:52

### Fixed

- survey-enhance now a dev dependency.

## [0.260.0] - 2023-03-28 22:21:13

### Added

- New Jersey dependent exemption.

## [0.259.1] - 2023-03-28 04:45:32

## [0.259.0] - 2023-03-27 20:40:18

### Changed

- Add Colorado EITC.

## [0.258.0] - 2023-03-27 20:36:50

### Added

- Maine EITC.

## [0.257.1] - 2023-03-27 18:48:24

### Added

- Calibrated CPS basic structure.

## [0.257.0] - 2023-03-27 02:12:55

### Added

- Alabama standard deductions

## [0.256.0] - 2023-03-26 15:17:24

### Added

- Alabama dependent exemption

## [0.255.0] - 2023-03-26 15:00:14

### Added

- Alabama income tax rate structure

## [0.254.1] - 2023-03-25 11:09:53

### Fixed

- SLSPC not included in the CPS microdata, causing a 2x runtime.

## [0.254.0] - 2023-03-24 04:59:06

### Added

- New Jersey blind or disabled exemption.

## [0.253.0] - 2023-03-24 04:33:15

### Added

- Virginia standard deduction.

## [0.252.0] - 2023-03-23 10:27:47

### Changed

- PolicyEngine Core data updates handled.

## [0.251.1] - 2023-03-21 00:52:11

### Changed

- Add California to modelled_policies.yaml so it shows up in population impacts.

## [0.251.0] - 2023-03-20 15:49:33

### Added

- Miscellaneous income.

## [0.250.0] - 2023-03-20 05:16:36

### Added

- California income tax to net income tree.

## [0.249.0] - 2023-03-19 22:30:49

### Added

- Virginia personal exemption.

## [0.248.1] - 2023-03-19 20:20:41

### Fixed

- CalEITC now correctly has no joint bonus.

## [0.248.0] - 2023-03-19 16:30:59

### Added

- Missouri TANF income limit / maximum benefit.

## [0.247.0] - 2023-03-18 05:22:13

### Added

- Virginia aged/blind exemption.

## [0.246.0] - 2023-03-18 05:01:12

### Added

- New York TANF countable earned income based on earned income exclusion.

## [0.245.0] - 2023-03-17 23:08:36

### Added

- Alabama personal exemption.

## [0.244.0] - 2023-03-14 22:01:55

### Added

- NJ senior exemption.

## [0.243.0] - 2023-03-14 18:11:17

### Added

- Maryland TANF maximum benefit.

## [0.242.0] - 2023-03-14 16:59:42

### Added

- New York TANF need standard.

## [0.241.0] - 2023-03-13 20:45:21

### Added

- DC TANF maximum income.

## [0.240.0] - 2023-03-13 00:07:28

### Added

- DC EITC with no qualifying children.

## [0.239.1] - 2023-03-12 19:57:14

### Fixed

- CA AGI calculation.

## [0.239.0] - 2023-03-11 22:27:07

### Added

- Federally taxable social security benefits to list of CA AGI subtractions.

## [0.238.1] - 2023-03-11 13:41:52

### Fixed

- CalEITC bug where eligibility conditions weren't applied in the second phase-out region.

## [0.238.0] - 2023-03-11 01:17:50

### Added

- NJ regular exemption.

## [0.237.1] - 2023-03-10 23:30:13

### Fixed

- CA Young Child Tax Credit (YCTC) logic.

## [0.237.0] - 2023-03-10 19:26:00

### Added

- CA AGI formula.
- CA taxable income formula.

## [0.236.0] - 2023-03-10 00:53:46

### Added

- nj_agi and nj_income_tax variables, and income filing threshold parameters.

## [0.235.0] - 2023-03-09 23:25:37

### Added

- 2022 CA use tax parameters.
- 2022 CA income tax rate bracket parameters.
- 2022 CA income tax standard deduction parameter.
- 2022 CA income tax exemption parameters.
- 2022 CA income tax credit parameters.

## [0.234.0] - 2023-03-09 16:29:06

### Added

- Maryland TANF earned income deduction.

## [0.233.0] - 2023-03-09 16:19:45

### Added

- Colorado TANF pregnancy allowance and integration tests.

## [0.232.0] - 2023-03-09 04:57:54

### Added

- Added NYC taxes and refundable credits to relevant household variables.

## [0.231.2] - 2023-03-08 22:35:18

### Fixed

- CPS generation on Windows.

## [0.231.1] - 2023-03-08 17:08:12

### Fixed

- SSI pass rate calibrated to 45%.

## [0.231.0] - 2023-03-08 15:52:08

### Added

- Is male variable.

## [0.230.1] - 2023-03-08 11:16:04

### Fixed

- Bug causing incorrect CalEITC amounts when not computed first.

## [0.230.0] - 2023-03-07 21:57:01

### Added

- me_agi variable, based on federal AGI, additions, and subtractions (not yet defined yet)

## [0.229.0] - 2023-03-07 14:20:43

### Added

- Formula for CalEITC qualifying child variable.

## [0.228.0] - 2023-03-07 07:05:29

### Added

- Texas TANF monthly income limit.

## [0.227.1] - 2023-03-07 03:56:15

### Added

- Missing 2021 California EITC parameter values.

## [0.227.0] - 2023-03-06 18:39:45

### Added

- CalEITC.

## [0.226.0] - 2023-03-05 19:02:15

### Added

- CA refundable credits variable.
- CA income tax variable.

## [0.225.0] - 2023-03-04 21:41:47

### Added

- CA nonrefundable credits variable.
- CA income tax before refundable credits variable.

## [0.224.1] - 2023-03-03 23:42:54

### Fixed

- Corrected descriptions for FERA and CARE

## [0.224.0] - 2023-03-03 22:39:06

### Added

- Colorado TANF countable earned income.

## [0.223.0] - 2023-03-02 22:01:53

### Added

- Additional unearned income sources to SNAP.
- Worker's compensation, strike benefits, disability benefits, child support expense, health insurance premiums, and medical out of pocket expenses from CPS.

## [0.222.2] - 2023-03-02 20:44:43

### Fixed

- Confusing specification of EITC investment income.

## [0.222.1] - 2023-03-02 03:05:32

### Added

- California CARE and FERA electricity discount programs.

## [0.222.0] - 2023-03-01 01:51:22

### Added

- Massachusetts rules for 2022 and 2023, including millionaire tax.

## [0.221.0] - 2023-02-28 22:57:23

### Added

- Eligibility for Colorado TANF.

## [0.220.5] - 2023-02-28 05:31:41

### Changed

- Updated Oregon income tax parameters for 2022.

## [0.220.4] - 2023-02-27 16:56:43

### Fixed

- SSI resource pass rate is now 0.2 (from 0.6) to hit administrative targets.

## [0.220.3] - 2023-02-26 23:50:19

### Changed

- Moved computed income variables to their respective section to avoid showing them as inputs.

## [0.220.2] - 2023-02-24 14:42:35

### Changed

- Replace all instances of ETERNITY with YEAR.

## [0.220.1] - 2023-02-23 14:18:46

### Fixed

- Incomplete list of state income tax variables by adding IL.

## [0.220.0] - 2023-02-21 23:07:17

### Added

- Add NYC taxes to net income tree.

## [0.219.1] - 2023-02-20 17:10:15

### Fixed

- Incomplete list of MO itemized deductions.

## [0.219.0] - 2023-02-18 20:44:38

### Added

- NYC child and dependent care credit

## [0.218.0] - 2023-02-17 05:32:26

### Added

- Maine personal exemption deduction.

## [0.217.1] - 2023-02-17 04:46:22

### Fixed

- MO section B pension deduction calculations.
- MO adjusted gross income calculations.

## [0.217.0] - 2023-02-17 00:02:39

### Added

- DC EITC.

## [0.216.0] - 2023-02-16 22:58:46

### Added

- Colorado TANF grant standard.

## [0.215.2] - 2023-02-16 18:00:31

### Added

- Legislative references for California CARE program.

## [0.215.1] - 2023-02-14 21:56:48

### Fixed

- MO social security or social security disability deduction calculation.

## [0.215.0] - 2023-02-14 21:49:06

### Added

- California CARE eligibility.

## [0.214.4] - 2023-02-14 05:02:37

### Fixed

- Logic for summation of taxable Social Security in Part C of MO Pension/SS/SSD deduction

## [0.214.3] - 2023-02-14 04:35:35

### Fixed

- MO income tax brackets.

## [0.214.2] - 2023-02-13 20:27:43

### Fixed

- Removed "uncapped" from OR refundable credits description.

## [0.214.1] - 2023-02-13 00:09:41

### Changed

- Updated Missouri income tax for 2023.

### Fixed

- mo_income_tax_before_credits tests.

## [0.214.0] - 2023-02-12 20:12:05

### Added

- Illinois and Missouri income taxes to net income tree.

## [0.213.4] - 2023-02-11 14:40:00

### Fixed

- Calculation of MD itemized deduction amount.

## [0.213.3] - 2023-02-10 16:30:27

### Fixed

- CTC phase-out metadata.

## [0.213.2] - 2023-02-10 04:12:00

### Fixed

- Value of OASDI maximum taxable earnings for 2023.

## [0.213.1] - 2023-02-09 00:00:45

### Fixed

- Incomplete specification of pension income variables.

## [0.213.0] - 2023-02-08 04:04:24

### Added

- NYC household credit

## [0.212.0] - 2023-02-07 15:58:09

### Added

- nyc_school_credit_income equal to adjusted_gross_income

## [0.211.1] - 2023-02-07 04:35:54

### Fixed

- Missouri adjusted gross income calculation.

## [0.211.0] - 2023-02-06 21:29:09

### Added

- Medical out of pocket expenses and health insurance premiums to CPS.

## [0.210.1] - 2023-02-05 17:41:21

### Fixed

- Missouri Working Families Tax Credit start year.

## [0.210.0] - 2023-02-04 22:38:15

### Added

- Missouri Working Families Tax Credit.

## [0.209.3] - 2023-02-04 00:52:10

### Changed

- Formula for md_dependent_care_subtraction variable.

## [0.209.2] - 2023-02-03 15:22:34

### Changed

- Split CPS Social Security benefits between retirement and disability depending on age.

## [0.209.1] - 2023-02-02 21:54:04

### Added

- alimony_income and self_employment_tax_ald to list of MA disallowed ALDs.

## [0.209.0] - 2023-02-02 17:49:25

### Added

- NYC Taxable Income

## [0.208.0] - 2023-02-02 16:32:41

### Added

- in_nyc formula

## [0.207.3] - 2023-02-01 22:12:43

### Changed

- Base of PA taxable income from adjusted_gross_income to irs_gross_income.

## [0.207.2] - 2023-02-01 03:52:15

### Changed

- Increase default age from 30 to 40.

## [0.207.1] - 2023-02-01 00:43:30

### Changed

- Raised default age from 18 to 30.

## [0.207.0] - 2023-01-31 23:17:45

### Added

- NYC School Tax Credit Rate Reduction Amount.

## [0.206.0] - 2023-01-31 23:00:29

### Added

- New York City income tax schedule.

## [0.205.3] - 2023-01-31 19:03:00

### Changed

- Add state supplement to household benefits.

## [0.205.2] - 2023-01-31 18:46:32

### Changed

- Refundability status of MA limited income tax credit to non-refundable.

## [0.205.1] - 2023-01-31 17:38:19

### Changed

- Added state_supplement to spm_unit_benefits.

## [0.205.0] - 2023-01-29 17:59:09

### Added

- NYC School Tax Credit Fixed Amount.

## [0.204.0] - 2023-01-29 16:36:45

### Added

- NYC EITC.

## [0.203.10] - 2023-01-28 22:43:09

## [0.203.9] - 2023-01-27 23:10:16

### Changed

- Core bumped and SNAP EA efficiency improvements.

## [0.203.8] - 2023-01-25 16:55:23

### Changed

- Ingest CPS Social Security as Social Security retirement benefits, and remove reported logic.

## [0.203.7] - 2023-01-24 23:11:08

### Changed

- Added Washington to list of modelled policies states.

## [0.203.6] - 2023-01-24 22:22:34

### Changed

- Relaxed version dependencies.

## [0.203.5] - 2023-01-24 16:21:30

### Fixed

- Minor bug in reported state tax reform handling.

## [0.203.4] - 2023-01-24 15:06:42

### Added

- Parameter to use reported State income tax values.

## [0.203.3] - 2023-01-22 06:08:39

### Changed

- Updated 2023 federal poverty guidelines to official values.

## [0.203.2] - 2023-01-22 03:14:47

### Fixed

- Problems with IL non-refundable credits.

## [0.203.1] - 2023-01-20 12:49:37

### Fixed

- Incorrect IL income additions and subtractions.

## [0.203.0] - 2023-01-19 22:22:05

### Added

- Top-level CO TANF variable.

## [0.202.1] - 2023-01-19 21:45:27

### Fixed

- Incorrect IL income additions.

## [0.202.0] - 2023-01-19 21:00:47

### Added

- Abolition parameters for major taxes and benefits.

## [0.201.0] - 2023-01-16 22:02:05

### Added

- Illinois personal income tax system.

## [0.200.7] - 2023-01-16 18:14:49

### Changed

- Refactor SNAP emergency allotment to decompose correctly in the app.

## [0.200.6] - 2023-01-15 17:40:22

### Added

- Structural reform emulating TAXSIM.

## [0.200.5] - 2023-01-14 20:30:41

### Fixed

- Added several integration tests.

## [0.200.4] - 2023-01-12 00:27:48

### Fixed

- Added modelled policy metadata.

## [0.200.3] - 2023-01-11 23:55:26

### Changed

- Core bumped to next patch version.

## [0.200.2] - 2023-01-11 22:55:05

### Added

- Metadata for some modelled policies.

## [0.200.1] - 2023-01-11 18:57:20

### Added

- More md_cdcc unit tests.

## [0.200.0] - 2023-01-11 12:37:35

## [0.199.6] - 2023-01-11 06:09:00

### Added

- README files for parameter folders.

## [0.199.5] - 2023-01-11 05:07:04

### Added

- School meal program values for 2022-23 school year.

## [0.199.4] - 2023-01-11 04:59:47

### Added

- Tentative 2023 federal poverty guidelines based on November CPI-U.
- C-CPI-U for more months of 2022.

## [0.199.3] - 2023-01-11 03:09:07

### Added

- Units and labels for SNAP parameters.

## [0.199.2] - 2023-01-10 17:31:28

### Changed

- Replaced `aggr` with `add`.

## [0.199.1] - 2023-01-10 12:30:48

### Changed

- Used adds and subtracts instead of sum_of_variables and Python code.

## [0.199.0] - 2023-01-10 06:45:38

### Added

- OH Income Tax Rates

## [0.198.0] - 2023-01-09 16:06:12

### Added

- MD AGI subtraction for pension income.

## [0.197.7] - 2023-01-06 11:26:07

### Changed

- Core bumped to 1.11.1.

## [0.197.6] - 2023-01-06 01:56:20

### Fixed

- Incomplete MD care expense AGI subtraction logic.

## [0.197.5] - 2023-01-04 19:50:05

### Added

- Test to guard against inadvertently making 2021 CDCC non-refundable.

## [0.197.4] - 2023-01-04 00:33:41

### Changed

- Update default year to 2023.

## [0.197.3] - 2023-01-03 23:24:30

### Changed

- Widened Python dependency.

## [0.197.2] - 2023-01-03 23:13:23

### Fixed

- Use parameter to define refundable and non-refundable credits, fixing CDCC refundability under ARPA.

## [0.197.1] - 2023-01-03 21:24:39

### Fixed

- PyPI deployments.

## [0.197.0] - 2023-01-03 21:17:57

### Changed

- SNAP EAs are calculated monthly.

## [0.196.1] - 2023-01-02 21:05:11

### Changed

- Pin and alphabetize dependencies, and pin Python 3.9.

## [0.196.0] - 2022-12-31 19:09:37

### Added

- Blindness, veterans benefits, and child support paid and received from the CPS.

## [0.195.1] - 2022-12-30 21:26:54

### Fixed

- Printing of annoying coverage warning messages.

## [0.195.0] - 2022-12-30 18:52:00

### Added

- Imputation for non-aged SSI recipients.

## [0.194.5] - 2022-12-29 22:51:36

### Changed

- Fix EITC parameter metadata propagation.

## [0.194.4] - 2022-12-29 21:18:40

### Fixed

- Incompleteness of MO property tax credit logic.

## [0.194.3] - 2022-12-28 21:05:37

### Fixed

- Household benefits are now back to using `adds`.

## [0.194.2] - 2022-12-28 14:47:16

### Fixed

- Household benefits now behave correctly with housing subsidy reforms.

## [0.194.1] - 2022-12-27 17:26:14

## [0.194.0] - 2022-12-27 17:07:33

### Added

- Normalised poverty variables.

## [0.193.1] - 2022-12-26 22:38:38

### Added

- Household tax including refundable credits.

## [0.193.0] - 2022-12-26 20:39:39

### Changed

- Moved state refundable credits into a total refundable credits variable with federal.
- Reorganized state income tax variables.

## [0.192.0] - 2022-12-26 20:04:44

### Added

- Switch to abolish housing subsidies.

## [0.191.0] - 2022-12-24 16:15:15

### Added

- SNAP emergency allotment end dates per Consolidated Appropriations Act of 2023.

## [0.190.3] - 2022-12-20 16:01:23

### Fixed

- Error in filter for deployment action.

## [0.190.2] - 2022-12-20 10:50:45

### Added

- API auto-deployment.

## [0.190.1] - 2022-12-20 08:13:53

### Fixed

- Apply ARPA's fully refundable CTC to the child CTC only, not the adult dependent CTC.

## [0.190.0] - 2022-12-20 07:55:11

### Added

- SMI for each state in FY2022 and FY2023.

## [0.189.0] - 2022-12-18 17:05:58

### Added

- Formula for is_in_k12_school based on age.

## [0.188.7] - 2022-12-18 16:50:59

### Fixed

- Metadata for CTC ARPA amount parameter.

## [0.188.6] - 2022-12-17 15:43:50

### Fixed

- Apply full refundability logic to adult dependent CTC.

## [0.188.5] - 2022-12-17 07:29:38

### Fixed

- Incorrect labels for new CTC parameters.

## [0.188.4] - 2022-12-16 15:02:28

### Fixed

- Absence of MD two-income AGI subtraction.

## [0.188.3] - 2022-12-16 05:36:42

### Fixed

- Presence of unneeded taxsim35_emulation statements in the tests.

## [0.188.2] - 2022-12-15 16:10:56

### Changed

- Bumped PolicyEngine Core.

## [0.188.1] - 2022-12-14 16:54:06

### Added

- Metadata for PolicyEngine

## [0.188.0] - 2022-12-14 16:50:18

### Added

- 2023 CPS, uprated from 2021.

## [0.187.0] - 2022-12-14 06:38:16

### Added

- 2023 SSI amounts.

## [0.186.2] - 2022-12-13 22:32:28

### Fixed

- Apply pre-TCJA qualifying rules to NY CTC.

## [0.186.1] - 2022-12-13 20:11:11

### Changed

- Moved `contrib` parameters to `gov.contrib`.

## [0.186.0] - 2022-12-13 19:01:41

### Fixed

- Social Security input in the CPS dataset.

## [0.185.2] - 2022-12-13 07:57:02

### Changed

- Model PA's increased SNAP gross income limit.

## [0.185.1] - 2022-12-13 07:05:42

### Fixed

- End SNAP emergency allotments in GA and NV.

## [0.185.0] - 2022-12-13 05:53:30

### Added

- Unit tests for Child Tax Credit variables.
- Intermediate ARPA CTC reduction variable.

### Changed

- Refactor Child Tax Credit reduction, including no longer capping at maximum.

### Fixed

- Child Tax Credit full refundability bug.
- Child Tax Credit now steps down rather than phases out.

## [0.184.2] - 2022-12-12 16:32:33

### Added

- Metadata for PolicyEngine.

## [0.184.1] - 2022-12-08 16:18:25

### Fixed

- Calculation of qualified business income deduction.

## [0.184.0] - 2022-12-07 20:55:22

### Added

- SNAP FY2023 parameters.

## [0.183.2] - 2022-12-07 19:52:54

### Changed

- Remove parameters representing a set of complex tax reforms.

### Fixed

- Calculation of federal income tax with self-employment income.

## [0.183.1] - 2022-12-07 13:35:40

### Fixed

- PolicyEngine-Core pinned to a minor version.

## [0.183.0] - 2022-12-05 17:46:08

### Changed

- Input folder structure and other new PolicyEngine app updates.
- Now dependent on PolicyEngine-Core v0.10.10

## [0.182.0] - 2022-12-01 23:15:49

### Added

- pa_income_tax_forgiveness_amount variable for breaking down tax in app table.
- Other sources to PA tax forgiveness eligibility income.

## [0.181.7] - 2022-12-01 23:07:54

### Fixed

- Absence of OR income subtraction for federally taxable social security benefits.

## [0.181.6] - 2022-11-30 14:51:01

### Fixed

- MO income tax debugging print is converted to a comment.

## [0.181.5] - 2022-11-30 04:19:57

### Changed

- Qualified business income to be a personal variable.
- Qualified business income to be net of several personal deductions.

## [0.181.4] - 2022-11-29 19:54:07

### Fixed

- MA bank interest deduction logic.

## [0.181.3] - 2022-11-28 05:19:48

### Changed

- Simplify MO federal income tax deduction code.

## [0.181.2] - 2022-11-28 04:33:20

### Fixed

- Move MO federal income tax deduction ignored credits list to a parameter.

## [0.181.1] - 2022-11-27 22:47:33

### Fixed

- MO federal income tax deduction logic.

## [0.181.0] - 2022-11-27 18:39:07

### Added

- Add MO Pension and SS or SSD Deduction variable
- Add Public Pension Income variable

## [0.180.1] - 2022-11-26 05:21:06

### Fixed

- MA excess exemption logic.

## [0.180.0] - 2022-11-24 05:45:06

### Added

- Missouri tax rates for 2020 and 2021.

## [0.179.0] - 2022-11-23 16:11:34

### Added

- TAXSIM35 emulation parameter.
- TAXSIM35 emulation logic to PA income tax forgiveness calculations.
- Test of PA income tax calculations using TAXSIM35 emulation.

## [0.178.9] - 2022-11-23 00:34:40

### Changed

- Renamed `or_income_tax_after_refundable_credits` to `or_income_tax` for consistency with other state income tax variables.

## [0.178.8] - 2022-11-22 06:40:01

### Fixed

- Logic of pension income exclusion from PA AGI.

## [0.178.7] - 2022-11-22 00:54:01

### Fixed

- MA short-term capital gains taxation logic.

## [0.178.6] - 2022-11-19 23:04:41

### Fixed

- Incorrect calculation of taxable social security benefits.

## [0.178.5] - 2022-11-19 21:33:23

### Fixed

- MA income tax Part A AGI calculation.

## [0.178.4] - 2022-11-19 21:10:44

### Fixed

- Incorrect inclusion of tax-exempt pension income in US AGI.

## [0.178.3] - 2022-11-19 21:07:36

### Fixed

- Absence of non-refundable American Opportunity Credit calculation.

## [0.178.2] - 2022-11-19 21:01:42

### Fixed

- Inability of data tests to work without a policyengine_us package.

## [0.178.1] - 2022-11-19 20:54:31

### Fixed

- Calculation of dividend income from qualified and non-qualified.

## [0.178.0] - 2022-11-19 20:41:19

### Added

- Simple splitting of CPS income variables into PolicyEngine-US variables.

## [0.177.3] - 2022-11-15 05:45:33

### Added

- Maryland standard deduction documentation

## [0.177.2] - 2022-11-14 22:37:20

### Fixed

- Missing 2021 parameters for nontaxable income under PA income tax.

## [0.177.1] - 2022-11-14 20:57:48

### Fixed

- Missing 2021 NY supplemental income tax parameters.

## [0.177.0] - 2022-11-08 12:25:49

### Changed

- Made CTC formulas year-agnostic.

## [0.176.0] - 2022-10-29 03:44:55

### Added

- AMT parameters for 2020-2022.

## [0.175.0] - 2022-10-25 17:49:04

### Added

- IRS parameters for 2023 tax year.
- Some missing IRS parameters for 2020-2022 tax years.

## [0.174.2] - 2022-10-22 18:25:44

### Fixed

- Charts in documentation render.

## [0.174.1] - 2022-10-20 13:40:02

### Fixed

- GH actions now run on Python 3.9.

## [0.174.0] - 2022-10-20 13:13:35

### Changed

- Moved to PolicyEngine Core.

## [0.173.3] - 2022-10-17 23:08:54

### Fixed

- Bug in MD EITC where chlidless_max parameter was called instead of childless.max_amount.

## [0.173.2] - 2022-10-16 15:58:42

### Added

- Change logic for MO tax system to calculate AGI, qualified_health_insurance_premiums, taxable_income at person level.

## [0.173.1] - 2022-10-15 22:44:42

### Changed

- Text and PolicyEngine names for some OR and PA parameters.

## [0.173.0] - 2022-10-14 22:12:28

### Added

- Oregon tax after credits

## [0.172.0] - 2022-10-13 03:39:19

### Added

- Changed 2021 to 2020 in MD refundable/non-refundable tax credit parameters

## [0.171.0] - 2022-10-13 02:52:46

### Added

- Total US population.

## [0.170.0] - 2022-10-10 20:55:47

### Added

- California use tax.

## [0.169.0] - 2022-10-10 19:12:57

### Added

- Oregon federal tax liability income subtraction.

## [0.168.0] - 2022-10-08 19:33:26

### Added

- California Child and Dependent Care Expenses Credit.

## [0.167.0] - 2022-10-07 22:41:57

### Added

- Add MO state tax integration tests, illustrating different calculation methods.

## [0.166.0] - 2022-10-07 03:01:19

### Added

- Oregon taxable income deductions.

## [0.165.0] - 2022-10-03 22:56:42

### Added

- California mental health services tax

## [0.164.0] - 2022-10-03 18:29:29

### Added

- Maryland Child Alliance EITC abolition switches.

## [0.163.1] - 2022-09-27 22:17:57

### Fixed

- County selection now is vectorised, cutting runtimes by 20%.

## [0.163.0] - 2022-09-27 02:30:33

### Added

- Flat per-person UBI amount.

## [0.162.0] - 2022-09-21 20:07:25

### Added

- 2021 ASEC.

## [0.161.0] - 2022-09-21 01:52:55

### Added

- California income tax rates.

## [0.160.0] - 2022-09-20 17:04:16

### Added

- Oregon standard deduction.

## [0.159.1] - 2022-09-20 05:11:32

### Added

- Budgetary impacts of some NY and PA programs to documentation notebooks.

## [0.159.0] - 2022-09-20 02:29:55

### Added

- California tax exemptions

## [0.158.0] - 2022-09-18 16:29:13

### Added

- Federal poverty guideline-based basic income element.

### Changed

- Made all basic income variables tax unit-level.

## [0.157.0] - 2022-09-16 15:22:22

### Added

- PTC deduction switch for the UBI Center flat tax.

## [0.156.0] - 2022-09-16 03:02:08

### Added

- Add taxsim comparisons to MO state tax system.
- Add notebook documentation showcasing tax/tax and benefits systems.
- Disabled mo_property_tax_credit until output schedule can be modeled.

## [0.155.2] - 2022-09-16 00:15:33

### Added

- Federal income tax documentation page.

## [0.155.1] - 2022-09-14 12:41:59

### Fixed

- Basic income taxability interaction with other phase-outs.

## [0.155.0] - 2022-09-13 19:33:43

### Added

- Basic income taxability.

## [0.154.0] - 2022-09-13 05:13:03

### Added

- OR income tax before credits.

## [0.153.0] - 2022-09-12 22:24:35

### Added

- Add MO agi, subtractions (mo_qualified_health_insurance_premiums)
- Add MO taxable income and deductions
- Add variables required for MO Property Tax Credit demographic tests

## [0.152.0] - 2022-09-12 22:06:22

### Added

- Variable computing federal tax liability without SALT.

## [0.151.0] - 2022-09-10 00:00:24

### Added

- OR kicker credit.

## [0.150.0] - 2022-09-09 15:39:41

### Added

- Pennsylvania use tax

## [0.149.0] - 2022-09-07 23:07:57

### Added

- Oregon personal exemption credit.

## [0.148.0] - 2022-09-07 20:29:32

### Fixed

- Re-implemented NY supplemental tax to fix mistaken cliffs.

## [0.147.3] - 2022-09-06 15:31:51

### Added

- NY tax documentation page.
- NY documentation pages to table of contents.

## [0.147.2] - 2022-09-06 10:51:59

### Added

- NY tax-benefit page to the documentation.

### Fixed

- NY college tuition and CDCC credits added as refundable.

## [0.147.1] - 2022-09-05 18:14:55

### Fixed

- Use manual eligibility in basic income eligibility.

## [0.147.0] - 2022-09-05 16:50:53

### Added

- NY State income tax.

## [0.146.0] - 2022-09-04 19:15:21

### Added

- Historical parameters to NY college tuition credit.
- Year period to energy efficient home improvement credit parameters.

## [0.145.0] - 2022-09-04 19:09:21

### Added

- Calculations for the tax forgiveness rate in Pennsylvania

## [0.144.1] - 2022-09-04 06:22:00

### Changed

- Refer consistently to the new name, the "Energy Efficient Home Improvement Tax Credit".

## [0.144.0] - 2022-09-03 20:54:46

### Changed

- Made the electric vehicle credit under the Inflation Reduction Act into current policy.
- Revised text of IRA rebate and credit parameters and variables.

## [0.143.0] - 2022-09-03 09:33:08

### Added

- NY college tuition credit and itemized deduction.

## [0.142.0] - 2022-09-03 09:17:20

### Added

- NY real property tax credit.

## [0.141.0] - 2022-09-02 20:26:10

### Added

- Oregon EITC match.

## [0.140.0] - 2022-09-02 20:09:49

### Added

- NY CTC.

## [0.139.0] - 2022-09-02 14:29:45

### Added

- NY Supplemental EITC.

## [0.138.0] - 2022-09-02 13:00:55

### Added

- NY supplemental income tax.

## [0.137.0] - 2022-09-02 00:53:29

### Changed

- Apply residential efficiency and electrifaction rebates to perfromance based retrofit expenditures.

## [0.136.0] - 2022-09-01 11:46:59

### Added

- NY CDCC.

## [0.135.1] - 2022-09-01 00:47:34

### Fixed

- Breakdown format in basic income parameters.

## [0.135.0] - 2022-08-31 23:58:28

### Added

- AGI limit for basic income.
- Dollar-range basic income phase-out option.

## [0.134.0] - 2022-08-27 20:34:55

### Changed

- Apply energy efficient home improvement tax credits to post-rebate expenditures.

## [0.133.0] - 2022-08-27 17:41:38

### Changed

- Updated Residential Clean Energy Credit for the Inflation Reduction Act.

## [0.132.0] - 2022-08-25 00:48:25

### Added

- High Efficiency Electric Home Rebate Program.

## [0.131.0] - 2022-08-23 04:58:33

### Added

- Energy efficient home improvements credit post-Inflation Reduction Act.

## [0.130.0] - 2022-08-18 17:24:10

### Added

- Pennsylvania income tax before forgiveness.

## [0.129.2] - 2022-08-18 09:15:19

### Fixed

- Don't reduce CTC by more than the maximum in 2021.

## [0.129.1] - 2022-08-17 15:46:46

### Added

- 2022 value of EITC joint bonus for couples without children.

## [0.129.0] - 2022-08-17 05:44:08

### Added

- Nonbusiness energy property credit.

## [0.128.3] - 2022-08-13 01:27:00

### Changed

- Formatting improvements in documentation.

## [0.128.2] - 2022-08-12 17:54:09

### Fixed

- Use Mac version of taxsim.

## [0.128.1] - 2022-08-12 13:45:51

### Changed

- Adjust logic for Washington Working Families Tax Credit based on recent legislation.

## [0.128.0] - 2022-08-10 20:37:56

### Added

- SSTB business variable.

## [0.127.0] - 2022-08-10 12:48:17

### Added

- Taxable income deductions for NY State tax.

## [0.126.0] - 2022-08-10 12:47:25

### Added

- Logic pathway to NY income tax from income.

## [0.125.0] - 2022-08-09 16:00:40

### Added

- Residential energy efficient property credit.

## [0.124.1] - 2022-08-09 15:41:14

### Fixed

- A bug causing qualified dividends to not be counted as 'net capital gain'.

## [0.124.0] - 2022-08-09 13:21:28

### Fixed

- Refactored pension income to exclude IRA calculations.

## [0.123.0] - 2022-08-09 12:06:14

### Added

- NY AGI adjustments.

## [0.122.0] - 2022-08-09 11:08:16

### Added

- NY income tax before credits (without high-income adjustment).

## [0.121.2] - 2022-08-07 16:48:06

### Fixed

- Incorrect head of household capital gains thresholds.

## [0.121.1] - 2022-08-05 16:24:00

### Changed

- Bump openfisca-tools to 0.13.3.

## [0.121.0] - 2022-08-05 12:29:00

### Added

- Re-implementation of capital gains law.

## [0.120.0] - 2022-08-04 14:53:40

### Added

- California standard deduction.

## [0.119.1] - 2022-08-03 19:38:51

### Added

- Missing PolicyEngine metadata for electric vehicle variables and parameters.

## [0.119.0] - 2022-08-03 19:19:26

### Added

- Federal electric vehicle credits under current law and the Inflation Reduction Act.

## [0.118.0] - 2022-08-02 10:35:25

### Fixed

- Dividend logic correctly handles qualified/non-qualified dividends.

## [0.117.0] - 2022-07-29 15:32:28

### Added

- NY taxable income variable.

## [0.116.0] - 2022-07-26 16:06:49

### Added

- IRS capital gains parameters for FY20-22.

## [0.115.0] - 2022-07-25 23:07:53

### Added

- Indiana other taxes.

## [0.114.1] - 2022-07-25 20:46:29

### Changed

- Split Maryland tax rates and personal exemptions by each filing status.

## [0.114.0] - 2022-07-24 20:28:18

### Added

- IN adjusted gross income tax

## [0.113.0] - 2022-07-22 23:54:11

### Added

- California Young Child Tax Credit.

## [0.112.1] - 2022-07-22 23:39:14

### Fixed

- SNAP standard deductions and references.
- Count all non-shelter deductions in SNAP net income before shelter.

## [0.112.0] - 2022-07-22 20:16:52

### Added

- Performance improvements through partially-executed formulas from OpenFisca-Tools.

## [0.111.0] - 2022-07-22 15:07:46

### Added

- IN Add-Backs.

## [0.110.2] - 2022-07-22 10:11:10

### Added

- Test that parameter files do not contain tabs with informative error messages.

## [0.110.1] - 2022-07-22 08:25:43

### Changed

- Moved geographical Medicaid calculation parameters to an on-demand folder.

## [0.110.0] - 2022-07-21 19:28:21

### Added

- IN deductions.

## [0.109.1] - 2022-07-20 20:41:23

### Fixed

- Breakdown for two Maryland parameters.

## [0.109.0] - 2022-07-20 19:59:29

### Changed

- Separate MD standard deduction parameters by filing status.
- Add MD CTC to list of refundable credits.
- Add MD notebooks to documentation table of contents.

## [0.108.0] - 2022-07-20 11:58:26

### Added

- Caching of second-lowest silver plan cost in the CPS microdata.

## [0.107.0] - 2022-07-20 11:57:02

### Added

- MD income tax to State income tax.

## [0.106.0] - 2022-07-19 14:26:52

### Added

- Maryland Earned Income Tax Credit.
- Notebooks for Maryland tax programs.

## [0.105.0] - 2022-07-18 23:24:42

### Added

- Maryland Poverty Line Credit.

## [0.104.0] - 2022-07-18 22:14:59

### Added

- Maryland refundable and non-refundable CDCC.

## [0.103.1] - 2022-07-18 20:44:57

### Added

- MD CTC notebook

## [0.103.0] - 2022-07-18 02:56:11

### Added

- Non-qualified dividend income.

### Fixed

- Dividend income split into qualified and non-qualified correctly.

## [0.102.0] - 2022-07-18 02:28:29

### Added

- California renters tax credit

## [0.101.0] - 2022-07-17 21:38:27

### Added

- Net investment income tax and other taxes to tax before refundable credits.

## [0.100.2] - 2022-07-16 14:06:12

### Added

- Changelog entry file functionality.
- Linecheck dev dependency.

## [0.100.1] - 2022-07-16 12:30:48

### Fixed

- Click dependency limited to >=8.0.0.

## [0.100.0] - 2022-07-16 11:16:19

### Added

- MD local income tax rates.

## [0.99.1] - 2022-07-16 04:19:02

### Changed

- Change MA dependent care credit from a scale parameter to an amount/cap structure.

## [0.99.0] - 2022-07-16 03:04:11

### Added

- MD CTC

## [0.98.1] - 2022-07-15 21:50:01

### Fixed

- Avoid double-counting CDCC when it was refundable in 2021.

## [0.98.0] - 2022-07-15 18:49:51

### Added

- Maryland adjusted gross income, with the dependent care subtraction.

## [0.97.0] - 2022-07-15 07:47:31

### Added

- MD CDCC.
- Notebook for federal and MD CDCCs.

### Fixed

- Phase out federal CDCC in steps.

## [0.96.0] - 2022-07-15 07:04:51

### Added

- MD State income tax EITC.

## [0.95.0] - 2022-07-15 05:42:48

### Added

- MD Standard deduction

## [0.94.0] - 2022-07-14 14:33:19

### Added

- ZIP code random generation by population sizes.
- ZIP code -> county -> State mapping (~400kB).

## [0.93.0] - 2022-07-14 01:03:39

### Added

- MD aged, blind exemptions
- MD personal Exemptions
- MD income tax rates
- MD placeholders for deductions, md_agi

## [0.92.0] - 2022-07-12 15:03:47

### Added

- IN exemptions.

## [0.91.4] - 2022-07-12 11:00:29

### Added

- Validation against TAXSIM using the CPS tax unit set.
- Validation results on the documentation.

## [0.91.3] - 2022-07-11 05:30:45

### Fixed

- Includes TANF as a categorical eligibility program for free school meals.

## [0.91.2] - 2022-07-10 19:04:21

### Fixed

- Separate WA WFTC parameter labels.

## [0.91.1] - 2022-07-10 16:25:24

### Fixed

- Charitable deduction available for MA taxable income calculations.

## [0.91.0] - 2022-07-10 16:19:30

### Added

- Washington capital gains tax.

## [0.90.0] - 2022-07-10 16:05:38

### Added

- MA dependent care tax credit.

## [0.89.1] - 2022-07-10 10:45:23

### Changed

- Impute integer ages in CPS from 80 to 84.

## [0.89.0] - 2022-07-08 12:26:04

### Added

- MA COVID-19 Essential Employee Premium Pay Program.

## [0.88.2] - 2022-07-07 17:39:36

### Added

- Notebook for Massachusetts Senior Circuit Breaker Credit.

### Fixed

- Include non-tax-exempt Social Security benefits in income for Massachusetts Senior Circuit Breaker Credit income definition.

## [0.88.1] - 2022-07-07 17:09:07

### Fixed

- Add resource test to SSI State Supplement.

## [0.88.0] - 2022-07-07 07:15:06

### Added

- Washington Working Families Tax Credit.
- EITC AGI limit variable.

## [0.87.0] - 2022-07-06 20:08:08

### Added

- MO Income Tax before credits.
- Parameters for MO Tax Schedule.

## [0.86.1] - 2022-07-03 21:47:43

### Fixed

- Fixed the CTC formula in 2021 (only) to correctly apply the income-based reduction.

## [0.86.0] - 2022-07-02 06:09:09

### Added

- MA Senior Circuit Breaker credit.

## [0.85.3] - 2022-06-29 03:38:34

### Fixed

- AMT income formula now uses a legislative source.

## [0.85.2] - 2022-06-29 01:00:28

### Changed

- Tests now don't stop after the first failure.

## [0.85.1] - 2022-06-27 20:18:27

### Added

- Uprated parameters for the standard deduction additions in 2020 onwards.
- References for the RRC parameters.

## [0.85.0] - 2022-06-27 05:43:48

### Added

- Recovery Rebate Credit.

## [0.84.5] - 2022-06-27 03:00:42

### Fixed

- A bug causing excess MA Part B deductions to apply to Part A income.

## [0.84.4] - 2022-06-26 20:58:23

### Fixed

- EITC phase-out thresholds for filers with children corrected to be $10 larger for some years.

## [0.84.3] - 2022-06-26 05:11:41

### Fixed

- EITC parameters for childless tax units in 2021.

## [0.84.2] - 2022-06-25 23:09:20

### Fixed

- Bugs causing the Additional CTC amount to be too large.

## [0.84.1] - 2022-06-25 20:50:40

### Added

- Units for the ECPA variables.

## [0.84.0] - 2022-06-24 17:49:18

### Changed

- Add structure for Indiana AGI.

## [0.83.4] - 2022-06-23 05:01:22

### Changed

- Simplify SNAP deduction formulas.

## [0.83.3] - 2022-06-22 23:37:55

### Changed

- Move End Child Poverty Act credits from benefits to refundable credits.

## [0.83.2] - 2022-06-22 21:48:02

### Changed

- Shortened End Child Poverty Act parameter names.

## [0.83.1] - 2022-06-22 20:34:31

### Added

- Metadata for the standard and aged/blind deduction.

### Changed

- OpenFisca-Tools bumped to 0.12.0.

## [0.83.0] - 2022-06-22 19:28:43

### Added

- Filer and adult dependent credits for Rep Tlaib's End Child Poverty Act.

## [0.82.0] - 2022-06-22 17:42:20

### Added

- Metadata for the standard and aged/blind deduction.

## [0.81.5] - 2022-06-22 04:36:30

### Fixed

- Really last tab.

## [0.81.4] - 2022-06-22 04:17:18

### Fixed

- Last lingering tab.

## [0.81.3] - 2022-06-22 03:55:59

### Fixed

- Remove tab again.

## [0.81.2] - 2022-06-22 03:04:03

### Fixed

- Tabs in parameter files removed.

## [0.81.1] - 2022-06-22 01:51:51

### Fixed

- Bugs causing basic income to be NaN.

## [0.81.0] - 2022-06-21 23:47:14

### Added

- UT tax before credit
- UT tax rate

## [0.80.0] - 2022-06-21 23:38:30

### Added

- UT taxpayer credit.

## [0.79.0] - 2022-06-21 23:13:24

### Added

- UT taxpayer credit reduction.

## [0.78.0] - 2022-06-21 22:53:46

### Added

- UT total income.
- UT taxable income

## [0.77.0] - 2022-06-20 22:23:30

### Added

- UT taxpayer credit maximum.

## [0.76.1] - 2022-06-20 13:24:54

### Changed

- Reorganize tax credits to skip the refundable/non-refundable distinction.
- Reorganize parameters to layer under gov.

## [0.76.0] - 2022-06-19 16:59:40

### Added

- Basic income phase-out parameters, logic and testing.

## [0.75.2] - 2022-06-17 16:36:16

### Fixed

- Payroll taxable wages deduct pension contributions rather than adding them.
- Market income includes missing capital gains, farm, illicit and rental income.

## [0.75.1] - 2022-06-16 16:58:09

### Changed

- Replace `phaseout` with `phase_out` or `phase-out` in variables and text.
- Reorganize variables into their own files.

## [0.75.0] - 2022-06-16 16:28:07

### Added

- Basic income amounts for young children and young adults.
- Flat tax on AGI.

### Fixed

- Three-digit zipcodes are generated with a fixed seed.
- Housing subsidies correctly included in benefits.

## [0.74.2] - 2022-06-15 21:45:58

### Fixed

- A bug causing the CDCC to have negative relevant expenses.

## [0.74.1] - 2022-06-13 21:56:08

### Fixed

- Childcare expenses are now correctly loaded from the CPS.

## [0.74.0] - 2022-06-13 15:06:03

### Added

- New York State household credit.

## [0.73.2] - 2022-06-12 20:17:09

### Fixed

- Point `cdcc_refund` to `cdcc` not the deprecated `c33200`.

## [0.73.1] - 2022-06-10 13:24:12

### Fixed

- A bug causing itemisation logic to fail.

## [0.73.0] - 2022-06-09 03:20:13

### Added

- Housing assistance and dependent variables.

## [0.72.3] - 2022-06-08 10:45:48

### Changed

- Breakdowns always specified as a list.

## [0.72.2] - 2022-06-08 05:07:17

### Added

- Metadata for MA policy.

## [0.72.1] - 2022-06-07 20:27:48

### Fixed

- Deduct government retirement contributions from MA taxable income on a per-person basis.

## [0.72.0] - 2022-06-07 18:04:31

### Added

- New York State EITC.
- Longer history for the Massachusetts rental tax deduction.

## [0.71.2] - 2022-06-07 09:54:21

### Fixed

- Medicaid benefit value per state.

## [0.71.1] - 2022-06-06 16:15:48

### Changed

- Reorganized state documentation.

### Fixed

- Entered rent person-level in documentation to align with latest package update.

## [0.71.0] - 2022-06-06 13:50:33

### Added

- Massachusetts State income tax.

## [0.70.3] - 2022-06-02 17:03:08

### Fixed

- A bug causing UC- and SS-related MAGI to incorrectly overcount loss deductions.

## [0.70.2] - 2022-06-02 17:01:01

### Changed

- Applied new openfisca-tools helper function `index_` to speed up SLSPC calculations.

## [0.70.1] - 2022-06-02 16:51:48

### Fixed

- Fix EITC bug which applied the phase-out after, instead of before, the phase-in.

## [0.70.0] - 2022-06-02 11:44:25

### Changed

- Apply consistent CTC young child formula to all years.
- Move CTC variables into their own files and other minor refactoring.

### Fixed

- Limit excess of Social Security taxes over EITC for refundable CTC to taxpayers with a minimum number of children.

## [0.69.3] - 2022-06-02 03:24:39

### Added

- New `taxsim_tfica` variable for testing.

## [0.69.2] - 2022-06-01 05:49:06

### Fixed

- Typo in SSI notebook.

## [0.69.1] - 2022-06-01 04:50:12

### Added

- New `tax_unit_ssi` variable.
- Example of single parent with two disabled children in SSI documentation notebook.

### Fixed

- Zeroed out `premium_tax_credit` in Massachusetts example notebook.

## [0.69.0] - 2022-05-31 17:31:13

### Added

- SSI deeming rules.

## [0.68.1] - 2022-05-30 22:40:36

### Fixed

- A bug causing the CDCC to not cap at the two-child childcare max expenses.

## [0.68.0] - 2022-05-28 06:59:45

### Added

- EITC parameters for 2017 and 2018.

## [0.67.0] - 2022-05-26 14:10:48

### Added

- CDCC integration tests.

### Changed

- Re-implemented CDCC according to the U.S. code.

## [0.66.1] - 2022-05-24 15:20:46

### Added

- WIC by earnings example in docs.

### Fixed

- Made WIC categorical eligibility person-level and more accurate.
- Pointed TANF maximum benefit variable to the correct parameter.
- Bug preventing tax_unit_childcare_expenses from being calculated.

## [0.66.0] - 2022-05-19 12:47:08

### Added

- MaritalUnit entity.
- Massachusetts state supplement.

## [0.65.0] - 2022-05-19 11:54:27

### Added

- WIC takeup and nutritional risk imputations.

## [0.64.1] - 2022-05-17 22:49:48

### Fixed

- Corrected EITC phase-out start values for 2020 and 2021.

## [0.64.0] - 2022-05-16 20:12:47

### Changed

- Refactored (references, simplifications and reorganisation) AGI -> taxable income code.

## [0.63.0] - 2022-05-16 12:11:08

### Added

- Estimated Medicaid benefit value.
- Aged/blind/disabled asset and income limits.

## [0.62.3] - 2022-05-11 23:19:04

### Fixed

- Remove bad import causing failure on some headless configurations.

## [0.62.2] - 2022-05-11 17:41:12

### Changed

- Label state income tax consistently with federal.

## [0.62.1] - 2022-05-11 15:14:12

### Fixed

- Moved lingering state income tax deduction files into variables/gov.

## [0.62.0] - 2022-05-11 14:17:28

### Added

- List of fully implemented programs at the US and state level.

## [0.61.0] - 2022-05-10 17:57:30

### Added

- TANF from CPS data.
- Female variable.
- Variable for number of own children in household.

## [0.60.0] - 2022-05-10 13:57:16

### Added

- Medicaid eligibility for 50 states.

## [0.59.0] - 2022-05-08 19:55:20

### Added

- TAXSIM integration tests for AGI.

### Changed

- TAXSIM variables renamed to contain `taxsim_` prefix.

## [0.58.1] - 2022-05-05 21:54:08

### Fixed

- Bug causing the system to fail to load on Colab.

## [0.58.0] - 2022-05-05 17:25:36

### Added

- Metadata and verbose variable names for IRS computation up to AGI.

## [0.57.1] - 2022-05-05 06:07:31

### Changed

- CO SNAP BBCE net income limit set to true.
- Cite official source for SNAP emergency allotment amount.

## [0.57.0] - 2022-05-04 19:44:35

### Added

- SSI notebook.
- SSI example to MA notebook.
- MA state tax exemptions for aged and blind people.
- Unit tests for state tax exemptions.

## [0.56.0] - 2022-05-03 16:41:49

### Added

- SNAP parameters by state from snapscreener.com.

## [0.55.0] - 2022-05-02 17:50:11

### Added

- TAXSIM tests for taxable SS and UI.

## [0.54.1] - 2022-05-02 06:38:45

### Fixed

- Specify documentation colors without policyengine package.

## [0.54.0] - 2022-05-02 05:24:28

### Changed

- Tied SALT deduction to state income tax.
- Improved charts in Massachusetts notebook.

## [0.53.0] - 2022-05-01 23:08:30

### Added

- Script to generate integration tests from TAXSIM.
- TAXSIM integration tests for the EITC.

## [0.52.0] - 2022-05-01 21:21:19

### Added

- Formulas for xtot, num, blind_head, blind_spouse, age_head, and age_spouse.
- Unit tests for some existing formulas.

### Changed

- Classify single person with dependents as head of household, not single.
- Split tax unit variables into their own files.
- Rename `marital_status` and `mars` to `filing_status`.

## [0.51.1] - 2022-05-01 20:21:24

### Added

- Notebook showing total net income and marginal tax rate charts for Massachusetts residents.

## [0.51.0] - 2022-05-01 14:45:31

### Added

- Empty variables for state and local sales tax, and local income tax.
- Logic for the SALT deduction to choose the greater of state and local income tax or state and local sales tax.
- Massachusetts SNAP parameters.

## [0.50.0] - 2022-04-30 22:16:10

### Added

- Massachusetts state income tax.
- EITC documentation notebook.

## [0.49.1] - 2022-04-22 13:39:09

### Added

- URL from which to download the latest CPS dataset (skipping generation)

## [0.49.0] - 2022-04-21 20:42:35

### Added

- Basic income now included in SPM unit benefits.

## [0.48.0] - 2022-04-21 14:15:27

### Added

- SPM unit income decile.
- SPM unit OECD equivalisation.

### Fixed

- Basic income variable for adults and seniors.

## [0.47.0] - 2022-04-19 15:52:56

### Added

- Per-vehicle payment (California)

## [0.46.1] - 2022-04-19 13:04:12

### Fixed

- Bug preventing the package from publishing on PyPI.

## [0.46.0] - 2022-04-19 10:22:36

### Added

- American Community Survey input.

## [0.45.2] - 2022-04-15 18:10:27

### Added

- Unit tests for age variables.

### Fixed

- Tax unit head and spouse flag logic.

## [0.45.1] - 2022-04-15 14:23:11

### Added

- Legislative references for CDCC parameters.

### Fixed

- CDCC uses maximum dependent parameter.

## [0.45.0] - 2022-04-14 08:19:40

### Added

- Microdata now handled entirely within PolicyEngine US.

## [0.44.0] - 2022-04-13 12:58:29

### Added

- Capped non-refundable credits variable.
- Shortened labels for tax variables.

## [0.43.1] - 2022-04-12 18:38:49

### Fixed

- Refundable CTC formula works properly when phase-in rate increased (comments added).

## [0.43.0] - 2022-04-07 06:08:18

### Added

- More recent Social Security payroll tax cap parameter values.
- Separate parameters for employer payroll taxes and self-employment taxes.
- Parameter for self-employment net earnings disregard.
- Unit tests and legislative references for payroll and self-employment tax variables.

### Changed

- Reorganized payroll and self-employment tax parameters and variables.
- Replaced large parameters with infinity and made number formatting consistent.

## [0.42.1] - 2022-04-06 10:35:14

### Fixed

- Point TANF parameter to state instead of region.

## [0.42.0] - 2022-04-05 19:04:10

### Added

- HUD adjusted income and dependent variables and logic.

## [0.41.2] - 2022-03-30 18:53:00

### Added

- Added full-time college student variable.

## [0.41.1] - 2022-03-30 13:12:44

### Added

- Parameter metadata for tax credits and payroll taxes.

## [0.41.0] - 2022-03-30 11:46:11

### Added

- CDCC parameters for eligibility and metadata.

### Fixed

- A bug where the CDCC would phase down too quickly.

## [0.40.0] - 2022-03-30 01:17:38

### Added

- Net income limits for SNAP BBCE (TANF) program.
- Legislative references for SNAP income limits.

## [0.39.0] - 2022-03-28 11:34:53

### Changed

- Added `is_eitc_qualifying_child` variable to improve EITC child logic.
- Split `is_in_school` into `is_in_k12_school` and `is_full_time_student`.

## [0.38.2] - 2022-03-28 10:55:27

### Fixed

- Versioning action didn't update `pyproject.toml`.

## [0.38.1] - 2022-03-28 10:40:42

### Added

- Page on TANF to documentation.

## [0.38.0] - 2022-03-27 18:49:02

### Changed

- Added multiple parameters for California's TANF system.
- Refactored the TANF structure for easier implementation of other state TANF programs.

## [0.37.9] - 2022-03-16 21:22:44

### Fixed

- Push action on GitHub correctly publishes.

## [0.37.8] - 2022-03-16 21:22:44

### Changed

- Tax folder re-organised to improve modularity.

### Fixed

- A bug in AMT calculations.

## [0.37.7] - 2022-03-16 20:29:58

### Fixed

- Push action on GitHub correctly publishes.

## [0.37.6] - 2022-03-13 00:00:00

### Fixed

- EITC uses the correct phase-in rate.

## [0.37.5] - 2022-03-11 00:00:00

### Added

- February 2022 chained CPI-U.

### Changed

- Simplified WIC uprating.

## [0.37.4] - 2022-03-09 00:00:00

### Changed

- IRS-published uprated income tax parameters for 2019-22.

## [0.37.3] - 2022-03-08 00:00:00

### Changed

- `is_married` moved from person-level to family-level, with a formula added.

## [0.37.2] - 2022-03-07 00:00:01

### Added

- `spm_unit_weight` variable.

### Fixed

- SNAP now uses the additional amounts where main rates are not available.

## [0.37.1] - 2022-03-07 00:00:00

### Changed

- Point `e02400` to `social_security` (for PolicyEngine).

## [0.37.0] - 2022-03-05 00:00:00

### Added

- SNAP aggregate benefits and participation.

## [0.36.1] - 2022-03-04 00:00:01

### Changed

- Adjust variable labels for consistency.

## [0.36.0] - 2022-03-04 00:00:00

### Added

- Supplemental Security Income for individuals.
- Social Security input variables, counted as unearned income for several programs.

## [0.35.3] - 2022-02-28 00:00:00

### Added

- Code coverage badge to README.md.
- Reminder for pull requests to run `make format && make documentation`.
- CPI-uprated values for WIC average payments.

### Changed

- Child Tax Credit names renamed to `ctc`.
- Child and Dependent Care Credit names renamed to `cdcc`.

### Fixed

- EITC maximum age in 2021 changed from 125 to infinity.

## [0.35.2] - 2022-02-27 00:00:00

### Fixed

- Subtract Lifeline from broadband cost before calculating ACP and EBB.

## [0.35.1] - 2022-02-21 00:00:03

### Changed

- Edited labels for ACP and SNAP normal allotment.

## [0.35.0] - 2022-02-21 00:00:02

### Added

- Rural Tribal supplement for Lifeline.

### Changed

- Restructure ACP and EBB Tribal amounts to work with PolicyEngine.

## [0.34.0] - 2022-02-21 00:00:01

### Added

- Affordable Connectivity Program.

### Changed

- Split school meal subsidies into free and reduced-price.

## [0.33.0] - 2022-02-21 00:00:00

### Added

- Uprated tax parameters for federal income tax.

## [0.32.6] - 2022-02-16 00:00:00

### Changed

- OpenFisca-Tools constraint widened to the current major version.

## [0.32.5] - 2022-02-13 00:00:00

### Added

- Chained CPI-U (monthly and August-only) parameters.
- Metadata for SNAP max allotment.

## [0.32.4] - 2022-02-10 00:00:00

### Added

- Categorical breakdown metadata infrastructure from OpenFisca-Tools.

## [0.32.3] - 2022-02-09 00:00:04

### Fixed

- Remove guaranteed income / cash assistance from benefits.

## [0.32.2] - 2022-02-09 00:00:03

### Fixed

- Specify WIC's unit as USD.

## [0.32.1] - 2022-02-09 00:00:02

### Fixed

- Change WIC display name from `WIC benefit value` to `WIC`.

## [0.32.0] - 2022-02-09 00:00:01

### Added

- WIC program.

### Fixed

- Include guaranteed income / cash assistance in market income.

## [0.31.0] - 2022-02-09 00:00:00

### Added

- Income limits for 5 Maryland Medicaid coverage groups.

## [0.30.3] - 2022-02-08 00:00:02

### Fixed

- Add Lifeline notebook to table of contents.

## [0.30.2] - 2022-02-08 00:00:01

### Added

- PolicyEngine metadata and notebook for Lifeline program.
- Formula for `irs_gross_income`, which Lifeline uses to calculate income-based eligibility.

## [0.30.1] - 2022-02-08 00:00:00

### Fixed

- EITC logic and parameters for non-3-child tax units.

## [0.30.0] - 2022-02-07 00:00:01

### Added

- Guaranteed income / cash assistance pilot income variable. This counts as unearned income for SNAP, uncounted for taxes and other benefits.

## [0.29.0] - 2022-02-07 00:00:00

### Added

- California Clean Vehicle Rebate Project.

## [0.28.0] - 2022-02-06 00:00:01

### Added

- SNAP emergency allotments for California.
- SNAP unearned income example in JupyterBook docs.

## [0.27.2] - 2022-02-06 00:00:00

### Added

- Added formula for TANF variable `continuous_tanf_eligibility`
- Added integration test for continuous TANF eligibility to `integration.yaml`

## [0.27.1] - 2022-02-02 00:00:00

### Added

- Metadata and variable aliases for key tax variables.
- Employment, self-employment, interest and dividend income as inputs to tax logic.

## [0.27.0] - 2022-01-28 00:00:00

### Added

- Child Tax Credit (and historical policy).
- Non-refundable and refundable credit handling in tax logic.
- Metadata for education credits and the EITC.

### Fixed

- Bugs in head/spouse detection and nonrefundable credits.

## [0.26.0] - 2022-01-25 00:00:00

### Added

- Categorical eligibility to school meal subsidies.
- Documentation notebook on school meal subsidies.
- Parameterized income sources for school meal subsidies.

### Changed

- Count school meal subsidies by school enrollment rather than age.
- Remove `spm_unit_` prefix from school meal variables.

## [0.25.0] - 2022-01-17 00:00:02

### Added

- Child Tax Credit (including adult dependents) parameters, logic and tests.

## [0.24.1] - 2022-01-17 00:00:01

### Changed

- Add metadata for variables and parameters used in SNAP calculations.
- Renames two parameters involved in SNAP deductions from `threshold` to `disregard`.

## [0.24.0] - 2022-01-17 00:00:00

### Added

- Logic for SNAP excess medical deduction and dependent care deduction.
- Limit SNAP earned income deduction to earned income.
- Jupyter Book documentation on SNAP.
- Updated SNAP parameters.
- Empty variables for calculating SNAP: `employment_income`, `self_employment_income`, `dividend_income`, `interest_income`, `childcare_expenses`, and `medical_out_of_pocket_expenses`.

### Changed

- Significant refactoring of SNAP code.
- Use openfisca-tools for `add` and `aggr` functions, and pass lists of variables to these function.
- Rename min/max SNAP benefit parameters and variables to use `allotment`.

## [0.23.1] - 2022-01-15 00:00:01

### Fixed

- Added links to version tag diffs in changelog.

## [0.23.0] - 2022-01-15 00:00:00

### Fixed

- Update CCDF subsidy formula.

## [0.22.0] - 2022-01-14 00:00:02

### Added

- Formula for SSI based on eligibility and amount if eligible.

## [0.21.0] - 2022-01-14 00:00:01

### Added

- Add CCDF copay formula.

## [0.20.2] - 2022-01-14 00:00:00

### Added

- Metadata for SNAP eligibility parameters.

### Fixed

- Parameter misname in SNAP formula.

## [0.20.1] - 2022-01-12 00:00:00

### Fixed

- Test runner failed to test string values.

## [0.20.0] - 2022-01-09 00:00:00

### Added

- Formula for initial TANF eligibility.
- Two new variables: `tanf_gross_earned_income` and `tanf_gross_unearned_income`.
- Variable & parameter for `initial_employment_deduction`.
- Integration tests for TANF cash aid from TANF IL website.

### Changed

- `tanf_countable_income` now includes unearned income and earned income deduction.

## [0.19.3] - 2022-01-08 00:00:01

### Added

- Units to all tax variables.

### Changed

- Adds one line between tests in yaml files.
- Use consistent imports in variable Python files.

## [0.19.2] - 2022-01-08 00:00:00

### Changed

- Removes the `u` prefix from all variable label strings.

## [0.19.1] - 2022-01-07 00:00:00

### Added

- Formulas for `childcare_hours_per_week` and `spm_unit_size`.
- Unit tests and units for some variables.

### Changed

- Reorganized variables.

## [0.19.0] - 2022-01-06 00:00:02

### Added

- Update child care market rate to annual.

## [0.18.0] - 2022-01-06 00:00:01

### Added

- Total child care market rate.

## [0.17.1] - 2022-01-06 00:00:00

### Changed

- Use USDA elderly and disabled definitions in SNAP calculations.

## [0.17.0] - 2022-01-04 00:00:00

### Added

- Categorical eligibility for SNAP, including broad-based categorical eligibility via low-cost TANF programs that effectively extend SNAP's asset and income limits.

### Changed

- Refactored SNAP code.

## [0.16.0] - 2022-01-03 00:00:02

### Added

- CCDF subsidy top-level logic

## [0.15.0] - 2022-01-03 00:00:01

### Added

- Federal SNAP asset tests logic

## [0.14.0] - 2022-01-03 00:00:00

### Added

- SNAP eligibility based on federal net and gross income limits.
- Unit and integration tests for SNAP variables.

## [0.13.0] - 2021-12-31 00:00:00

### Added

- Formula for Medicaid person type, based on age and dependents.
- Variable for whether a person meets their Medicaid income eligibility requirement.

## [0.12.0] - 2021-12-30 00:00:01

### Added

- Elderly and Disabled (tax) Credit.

## [0.11.0] - 2021-12-30 00:00:00

### Added

- American Opportunity (tax) Credit.
- Lifetime Learning (tax) Credit.

## [0.10.0] - 2021-12-28 00:00:04

### Added

- Income-to-SMI (state median income) ratio.

## [0.9.0] - 2021-12-28 00:00:03

### Added

- Social Security taxation logic.

## [0.8.0] - 2021-12-28 00:00:02

### Added

- Minimum benefit logic for SNAP.

## [0.7.0] - 2021-12-28 00:00:01

### Added

- Gains Tax (capital gains treatment) logic and parameters.

## [0.6.0] - 2021-12-28 00:00:00

### Added

- Alternative Minimum Tax (AMT) income and liability logic.
- Development tools for auto-generating unit tests for Tax-Calculator functions.

## [0.5.0] - 2021-12-27 00:00:00

### Added

- Medicaid income thresholds for California.

## [0.4.0] - 2021-12-26 00:00:00

### Added

- TANF eligibility, broken down into demographic and financial variables, with financial separated by current enrollment in program.
- Demographic TANF eligibility per IL rules.

## [0.3.1] - 2021-12-25 00:00:03

### Added

- Automated tests.

## [0.3.0] - 2021-12-25 00:00:02

### Added

- Lifeline benefit.

## [0.2.0] - 2021-12-25 00:00:01

### Added

- Tax variables, some benefit variables.

## [0.1.0] - 2021-12-25 00:00:00

### Added

- Prototype with some tax implementations.

## [0.0.1] - 2021-06-28 00:00:00

### Added

- First prototype version with a standard deduction variable.



[1.586.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.586.1...1.586.2
[1.586.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.586.0...1.586.1
[1.586.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.585.0...1.586.0
[1.585.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.584.0...1.585.0
[1.584.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.583.0...1.584.0
[1.583.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.582.1...1.583.0
[1.582.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.582.0...1.582.1
[1.582.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.581.2...1.582.0
[1.581.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.581.1...1.581.2
[1.581.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.581.0...1.581.1
[1.581.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.580.0...1.581.0
[1.580.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.579.0...1.580.0
[1.579.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.578.1...1.579.0
[1.578.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.578.0...1.578.1
[1.578.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.577.1...1.578.0
[1.577.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.577.0...1.577.1
[1.577.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.576.0...1.577.0
[1.576.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.575.0...1.576.0
[1.575.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.574.0...1.575.0
[1.574.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.573.0...1.574.0
[1.573.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.572.5...1.573.0
[1.572.5]: https://github.com/PolicyEngine/policyengine-us/compare/1.572.4...1.572.5
[1.572.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.572.3...1.572.4
[1.572.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.572.2...1.572.3
[1.572.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.572.1...1.572.2
[1.572.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.572.0...1.572.1
[1.572.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.571.1...1.572.0
[1.571.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.571.0...1.571.1
[1.571.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.570.7...1.571.0
[1.570.7]: https://github.com/PolicyEngine/policyengine-us/compare/1.570.6...1.570.7
[1.570.6]: https://github.com/PolicyEngine/policyengine-us/compare/1.570.5...1.570.6
[1.570.5]: https://github.com/PolicyEngine/policyengine-us/compare/1.570.4...1.570.5
[1.570.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.570.3...1.570.4
[1.570.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.570.2...1.570.3
[1.570.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.570.1...1.570.2
[1.570.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.570.0...1.570.1
[1.570.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.569.0...1.570.0
[1.569.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.568.3...1.569.0
[1.568.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.568.2...1.568.3
[1.568.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.568.1...1.568.2
[1.568.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.568.0...1.568.1
[1.568.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.567.3...1.568.0
[1.567.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.567.2...1.567.3
[1.567.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.567.1...1.567.2
[1.567.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.567.0...1.567.1
[1.567.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.566.0...1.567.0
[1.566.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.565.1...1.566.0
[1.565.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.565.0...1.565.1
[1.565.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.564.2...1.565.0
[1.564.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.564.1...1.564.2
[1.564.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.564.0...1.564.1
[1.564.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.563.2...1.564.0
[1.563.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.563.1...1.563.2
[1.563.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.563.0...1.563.1
[1.563.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.562.3...1.563.0
[1.562.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.562.2...1.562.3
[1.562.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.562.1...1.562.2
[1.562.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.562.0...1.562.1
[1.562.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.561.1...1.562.0
[1.561.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.561.0...1.561.1
[1.561.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.560.3...1.561.0
[1.560.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.560.2...1.560.3
[1.560.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.560.1...1.560.2
[1.560.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.560.0...1.560.1
[1.560.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.559.0...1.560.0
[1.559.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.558.5...1.559.0
[1.558.5]: https://github.com/PolicyEngine/policyengine-us/compare/1.558.4...1.558.5
[1.558.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.558.3...1.558.4
[1.558.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.558.2...1.558.3
[1.558.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.558.1...1.558.2
[1.558.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.558.0...1.558.1
[1.558.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.557.2...1.558.0
[1.557.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.557.1...1.557.2
[1.557.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.557.0...1.557.1
[1.557.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.556.2...1.557.0
[1.556.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.556.1...1.556.2
[1.556.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.556.0...1.556.1
[1.556.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.555.3...1.556.0
[1.555.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.555.2...1.555.3
[1.555.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.555.1...1.555.2
[1.555.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.555.0...1.555.1
[1.555.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.554.1...1.555.0
[1.554.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.554.0...1.554.1
[1.554.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.553.0...1.554.0
[1.553.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.552.0...1.553.0
[1.552.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.551.1...1.552.0
[1.551.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.551.0...1.551.1
[1.551.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.550.2...1.551.0
[1.550.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.550.1...1.550.2
[1.550.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.550.0...1.550.1
[1.550.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.549.0...1.550.0
[1.549.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.548.0...1.549.0
[1.548.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.547.0...1.548.0
[1.547.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.546.1...1.547.0
[1.546.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.546.0...1.546.1
[1.546.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.545.3...1.546.0
[1.545.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.545.2...1.545.3
[1.545.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.545.1...1.545.2
[1.545.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.545.0...1.545.1
[1.545.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.544.0...1.545.0
[1.544.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.543.0...1.544.0
[1.543.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.542.1...1.543.0
[1.542.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.542.0...1.542.1
[1.542.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.541.1...1.542.0
[1.541.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.541.0...1.541.1
[1.541.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.540.1...1.541.0
[1.540.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.540.0...1.540.1
[1.540.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.539.0...1.540.0
[1.539.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.538.1...1.539.0
[1.538.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.538.0...1.538.1
[1.538.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.537.4...1.538.0
[1.537.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.537.3...1.537.4
[1.537.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.537.2...1.537.3
[1.537.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.537.1...1.537.2
[1.537.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.537.0...1.537.1
[1.537.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.536.0...1.537.0
[1.536.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.535.0...1.536.0
[1.535.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.534.6...1.535.0
[1.534.6]: https://github.com/PolicyEngine/policyengine-us/compare/1.534.5...1.534.6
[1.534.5]: https://github.com/PolicyEngine/policyengine-us/compare/1.534.4...1.534.5
[1.534.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.534.3...1.534.4
[1.534.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.534.2...1.534.3
[1.534.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.534.1...1.534.2
[1.534.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.534.0...1.534.1
[1.534.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.533.0...1.534.0
[1.533.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.532.4...1.533.0
[1.532.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.532.3...1.532.4
[1.532.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.532.2...1.532.3
[1.532.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.532.1...1.532.2
[1.532.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.532.0...1.532.1
[1.532.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.531.0...1.532.0
[1.531.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.530.0...1.531.0
[1.530.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.529.0...1.530.0
[1.529.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.528.0...1.529.0
[1.528.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.527.2...1.528.0
[1.527.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.527.1...1.527.2
[1.527.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.527.0...1.527.1
[1.527.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.526.2...1.527.0
[1.526.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.526.1...1.526.2
[1.526.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.526.0...1.526.1
[1.526.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.525.0...1.526.0
[1.525.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.524.1...1.525.0
[1.524.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.524.0...1.524.1
[1.524.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.523.1...1.524.0
[1.523.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.523.0...1.523.1
[1.523.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.522.0...1.523.0
[1.522.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.521.0...1.522.0
[1.521.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.520.0...1.521.0
[1.520.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.519.0...1.520.0
[1.519.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.518.0...1.519.0
[1.518.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.517.0...1.518.0
[1.517.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.516.4...1.517.0
[1.516.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.516.3...1.516.4
[1.516.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.516.2...1.516.3
[1.516.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.516.1...1.516.2
[1.516.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.516.0...1.516.1
[1.516.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.515.0...1.516.0
[1.515.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.514.2...1.515.0
[1.514.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.514.1...1.514.2
[1.514.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.514.0...1.514.1
[1.514.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.513.1...1.514.0
[1.513.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.513.0...1.513.1
[1.513.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.512.0...1.513.0
[1.512.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.511.2...1.512.0
[1.511.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.511.1...1.511.2
[1.511.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.511.0...1.511.1
[1.511.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.510.0...1.511.0
[1.510.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.509.0...1.510.0
[1.509.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.508.2...1.509.0
[1.508.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.508.1...1.508.2
[1.508.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.508.0...1.508.1
[1.508.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.507.0...1.508.0
[1.507.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.506.0...1.507.0
[1.506.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.505.0...1.506.0
[1.505.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.504.0...1.505.0
[1.504.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.503.3...1.504.0
[1.503.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.503.2...1.503.3
[1.503.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.503.1...1.503.2
[1.503.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.503.0...1.503.1
[1.503.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.502.3...1.503.0
[1.502.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.502.2...1.502.3
[1.502.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.502.1...1.502.2
[1.502.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.502.0...1.502.1
[1.502.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.501.0...1.502.0
[1.501.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.500.4...1.501.0
[1.500.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.500.3...1.500.4
[1.500.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.500.2...1.500.3
[1.500.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.500.1...1.500.2
[1.500.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.500.0...1.500.1
[1.500.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.499.1...1.500.0
[1.499.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.499.0...1.499.1
[1.499.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.498.1...1.499.0
[1.498.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.498.0...1.498.1
[1.498.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.497.1...1.498.0
[1.497.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.497.0...1.497.1
[1.497.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.496.2...1.497.0
[1.496.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.496.1...1.496.2
[1.496.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.496.0...1.496.1
[1.496.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.495.0...1.496.0
[1.495.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.494.0...1.495.0
[1.494.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.493.0...1.494.0
[1.493.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.492.0...1.493.0
[1.492.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.491.0...1.492.0
[1.491.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.490.0...1.491.0
[1.490.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.489.0...1.490.0
[1.489.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.488.0...1.489.0
[1.488.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.487.0...1.488.0
[1.487.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.486.0...1.487.0
[1.486.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.485.4...1.486.0
[1.485.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.485.3...1.485.4
[1.485.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.485.2...1.485.3
[1.485.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.485.1...1.485.2
[1.485.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.485.0...1.485.1
[1.485.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.484.3...1.485.0
[1.484.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.484.2...1.484.3
[1.484.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.484.1...1.484.2
[1.484.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.484.0...1.484.1
[1.484.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.483.0...1.484.0
[1.483.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.482.0...1.483.0
[1.482.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.481.0...1.482.0
[1.481.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.480.0...1.481.0
[1.480.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.479.0...1.480.0
[1.479.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.478.0...1.479.0
[1.478.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.477.0...1.478.0
[1.477.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.476.0...1.477.0
[1.476.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.475.0...1.476.0
[1.475.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.474.0...1.475.0
[1.474.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.473.0...1.474.0
[1.473.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.472.0...1.473.0
[1.472.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.471.0...1.472.0
[1.471.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.470.1...1.471.0
[1.470.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.470.0...1.470.1
[1.470.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.469.0...1.470.0
[1.469.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.468.0...1.469.0
[1.468.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.467.0...1.468.0
[1.467.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.466.0...1.467.0
[1.466.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.465.5...1.466.0
[1.465.5]: https://github.com/PolicyEngine/policyengine-us/compare/1.465.4...1.465.5
[1.465.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.465.3...1.465.4
[1.465.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.465.2...1.465.3
[1.465.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.465.1...1.465.2
[1.465.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.465.0...1.465.1
[1.465.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.464.2...1.465.0
[1.464.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.464.1...1.464.2
[1.464.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.464.0...1.464.1
[1.464.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.463.0...1.464.0
[1.463.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.462.1...1.463.0
[1.462.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.462.0...1.462.1
[1.462.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.461.3...1.462.0
[1.461.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.461.2...1.461.3
[1.461.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.461.1...1.461.2
[1.461.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.461.0...1.461.1
[1.461.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.460.2...1.461.0
[1.460.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.460.1...1.460.2
[1.460.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.460.0...1.460.1
[1.460.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.459.2...1.460.0
[1.459.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.459.1...1.459.2
[1.459.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.459.0...1.459.1
[1.459.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.458.2...1.459.0
[1.458.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.458.1...1.458.2
[1.458.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.458.0...1.458.1
[1.458.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.457.1...1.458.0
[1.457.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.457.0...1.457.1
[1.457.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.456.2...1.457.0
[1.456.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.456.1...1.456.2
[1.456.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.456.0...1.456.1
[1.456.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.455.0...1.456.0
[1.455.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.454.1...1.455.0
[1.454.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.454.0...1.454.1
[1.454.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.453.1...1.454.0
[1.453.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.453.0...1.453.1
[1.453.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.452.0...1.453.0
[1.452.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.451.0...1.452.0
[1.451.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.450.0...1.451.0
[1.450.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.449.8...1.450.0
[1.449.8]: https://github.com/PolicyEngine/policyengine-us/compare/1.449.7...1.449.8
[1.449.7]: https://github.com/PolicyEngine/policyengine-us/compare/1.449.6...1.449.7
[1.449.6]: https://github.com/PolicyEngine/policyengine-us/compare/1.449.5...1.449.6
[1.449.5]: https://github.com/PolicyEngine/policyengine-us/compare/1.449.4...1.449.5
[1.449.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.449.3...1.449.4
[1.449.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.449.2...1.449.3
[1.449.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.449.1...1.449.2
[1.449.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.449.0...1.449.1
[1.449.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.448.0...1.449.0
[1.448.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.447.0...1.448.0
[1.447.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.446.1...1.447.0
[1.446.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.446.0...1.446.1
[1.446.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.445.0...1.446.0
[1.445.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.444.1...1.445.0
[1.444.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.444.0...1.444.1
[1.444.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.443.0...1.444.0
[1.443.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.442.1...1.443.0
[1.442.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.442.0...1.442.1
[1.442.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.441.3...1.442.0
[1.441.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.441.2...1.441.3
[1.441.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.441.1...1.441.2
[1.441.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.441.0...1.441.1
[1.441.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.440.1...1.441.0
[1.440.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.440.0...1.440.1
[1.440.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.439.1...1.440.0
[1.439.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.439.0...1.439.1
[1.439.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.438.1...1.439.0
[1.438.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.438.0...1.438.1
[1.438.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.437.0...1.438.0
[1.437.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.436.0...1.437.0
[1.436.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.435.1...1.436.0
[1.435.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.435.0...1.435.1
[1.435.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.434.0...1.435.0
[1.434.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.433.0...1.434.0
[1.433.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.432.9...1.433.0
[1.432.9]: https://github.com/PolicyEngine/policyengine-us/compare/1.432.8...1.432.9
[1.432.8]: https://github.com/PolicyEngine/policyengine-us/compare/1.432.7...1.432.8
[1.432.7]: https://github.com/PolicyEngine/policyengine-us/compare/1.432.6...1.432.7
[1.432.6]: https://github.com/PolicyEngine/policyengine-us/compare/1.432.5...1.432.6
[1.432.5]: https://github.com/PolicyEngine/policyengine-us/compare/1.432.4...1.432.5
[1.432.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.432.3...1.432.4
[1.432.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.432.2...1.432.3
[1.432.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.432.1...1.432.2
[1.432.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.432.0...1.432.1
[1.432.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.431.0...1.432.0
[1.431.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.430.0...1.431.0
[1.430.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.429.0...1.430.0
[1.429.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.428.0...1.429.0
[1.428.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.427.0...1.428.0
[1.427.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.426.0...1.427.0
[1.426.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.425.7...1.426.0
[1.425.7]: https://github.com/PolicyEngine/policyengine-us/compare/1.425.6...1.425.7
[1.425.6]: https://github.com/PolicyEngine/policyengine-us/compare/1.425.5...1.425.6
[1.425.5]: https://github.com/PolicyEngine/policyengine-us/compare/1.425.4...1.425.5
[1.425.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.425.3...1.425.4
[1.425.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.425.2...1.425.3
[1.425.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.425.1...1.425.2
[1.425.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.425.0...1.425.1
[1.425.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.424.6...1.425.0
[1.424.6]: https://github.com/PolicyEngine/policyengine-us/compare/1.424.5...1.424.6
[1.424.5]: https://github.com/PolicyEngine/policyengine-us/compare/1.424.4...1.424.5
[1.424.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.424.3...1.424.4
[1.424.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.424.2...1.424.3
[1.424.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.424.1...1.424.2
[1.424.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.424.0...1.424.1
[1.424.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.423.4...1.424.0
[1.423.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.423.3...1.423.4
[1.423.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.423.2...1.423.3
[1.423.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.423.1...1.423.2
[1.423.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.423.0...1.423.1
[1.423.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.422.0...1.423.0
[1.422.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.421.0...1.422.0
[1.421.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.420.0...1.421.0
[1.420.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.419.0...1.420.0
[1.419.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.418.0...1.419.0
[1.418.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.417.3...1.418.0
[1.417.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.417.2...1.417.3
[1.417.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.417.1...1.417.2
[1.417.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.417.0...1.417.1
[1.417.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.416.0...1.417.0
[1.416.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.415.0...1.416.0
[1.415.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.414.0...1.415.0
[1.414.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.413.3...1.414.0
[1.413.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.413.2...1.413.3
[1.413.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.413.1...1.413.2
[1.413.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.413.0...1.413.1
[1.413.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.412.0...1.413.0
[1.412.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.411.0...1.412.0
[1.411.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.410.0...1.411.0
[1.410.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.409.0...1.410.0
[1.409.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.408.1...1.409.0
[1.408.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.408.0...1.408.1
[1.408.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.407.4...1.408.0
[1.407.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.407.3...1.407.4
[1.407.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.407.2...1.407.3
[1.407.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.407.1...1.407.2
[1.407.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.407.0...1.407.1
[1.407.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.406.0...1.407.0
[1.406.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.405.0...1.406.0
[1.405.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.404.1...1.405.0
[1.404.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.404.0...1.404.1
[1.404.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.403.2...1.404.0
[1.403.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.403.1...1.403.2
[1.403.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.403.0...1.403.1
[1.403.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.402.3...1.403.0
[1.402.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.402.2...1.402.3
[1.402.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.402.1...1.402.2
[1.402.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.402.0...1.402.1
[1.402.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.401.0...1.402.0
[1.401.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.400.2...1.401.0
[1.400.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.400.1...1.400.2
[1.400.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.400.0...1.400.1
[1.400.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.399.1...1.400.0
[1.399.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.399.0...1.399.1
[1.399.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.398.1...1.399.0
[1.398.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.398.0...1.398.1
[1.398.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.397.2...1.398.0
[1.397.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.397.1...1.397.2
[1.397.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.397.0...1.397.1
[1.397.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.396.0...1.397.0
[1.396.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.395.2...1.396.0
[1.395.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.395.1...1.395.2
[1.395.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.395.0...1.395.1
[1.395.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.394.0...1.395.0
[1.394.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.393.0...1.394.0
[1.393.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.392.0...1.393.0
[1.392.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.391.1...1.392.0
[1.391.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.391.0...1.391.1
[1.391.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.390.1...1.391.0
[1.390.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.390.0...1.390.1
[1.390.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.389.1...1.390.0
[1.389.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.389.0...1.389.1
[1.389.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.388.0...1.389.0
[1.388.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.387.3...1.388.0
[1.387.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.387.2...1.387.3
[1.387.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.387.1...1.387.2
[1.387.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.387.0...1.387.1
[1.387.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.386.1...1.387.0
[1.386.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.386.0...1.386.1
[1.386.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.385.1...1.386.0
[1.385.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.385.0...1.385.1
[1.385.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.384.0...1.385.0
[1.384.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.383.0...1.384.0
[1.383.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.382.0...1.383.0
[1.382.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.381.3...1.382.0
[1.381.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.381.2...1.381.3
[1.381.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.381.1...1.381.2
[1.381.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.381.0...1.381.1
[1.381.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.380.0...1.381.0
[1.380.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.379.0...1.380.0
[1.379.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.378.0...1.379.0
[1.378.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.377.1...1.378.0
[1.377.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.377.0...1.377.1
[1.377.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.376.4...1.377.0
[1.376.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.376.3...1.376.4
[1.376.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.376.2...1.376.3
[1.376.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.376.1...1.376.2
[1.376.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.376.0...1.376.1
[1.376.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.375.0...1.376.0
[1.375.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.374.1...1.375.0
[1.374.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.374.0...1.374.1
[1.374.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.373.1...1.374.0
[1.373.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.373.0...1.373.1
[1.373.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.372.0...1.373.0
[1.372.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.371.0...1.372.0
[1.371.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.370.2...1.371.0
[1.370.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.370.1...1.370.2
[1.370.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.370.0...1.370.1
[1.370.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.369.0...1.370.0
[1.369.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.368.0...1.369.0
[1.368.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.367.0...1.368.0
[1.367.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.366.2...1.367.0
[1.366.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.366.1...1.366.2
[1.366.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.366.0...1.366.1
[1.366.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.365.2...1.366.0
[1.365.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.365.1...1.365.2
[1.365.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.365.0...1.365.1
[1.365.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.364.0...1.365.0
[1.364.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.363.1...1.364.0
[1.363.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.363.0...1.363.1
[1.363.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.362.1...1.363.0
[1.362.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.362.0...1.362.1
[1.362.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.361.0...1.362.0
[1.361.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.360.1...1.361.0
[1.360.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.360.0...1.360.1
[1.360.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.359.1...1.360.0
[1.359.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.359.0...1.359.1
[1.359.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.358.1...1.359.0
[1.358.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.358.0...1.358.1
[1.358.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.357.2...1.358.0
[1.357.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.357.1...1.357.2
[1.357.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.357.0...1.357.1
[1.357.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.356.0...1.357.0
[1.356.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.355.0...1.356.0
[1.355.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.354.0...1.355.0
[1.354.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.353.0...1.354.0
[1.353.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.352.1...1.353.0
[1.352.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.352.0...1.352.1
[1.352.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.351.5...1.352.0
[1.351.5]: https://github.com/PolicyEngine/policyengine-us/compare/1.351.4...1.351.5
[1.351.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.351.3...1.351.4
[1.351.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.351.2...1.351.3
[1.351.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.351.1...1.351.2
[1.351.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.351.0...1.351.1
[1.351.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.350.1...1.351.0
[1.350.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.350.0...1.350.1
[1.350.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.349.3...1.350.0
[1.349.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.349.2...1.349.3
[1.349.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.349.1...1.349.2
[1.349.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.349.0...1.349.1
[1.349.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.348.1...1.349.0
[1.348.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.348.0...1.348.1
[1.348.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.347.0...1.348.0
[1.347.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.346.0...1.347.0
[1.346.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.345.0...1.346.0
[1.345.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.344.0...1.345.0
[1.344.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.343.0...1.344.0
[1.343.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.342.1...1.343.0
[1.342.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.342.0...1.342.1
[1.342.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.341.1...1.342.0
[1.341.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.341.0...1.341.1
[1.341.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.340.1...1.341.0
[1.340.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.340.0...1.340.1
[1.340.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.339.1...1.340.0
[1.339.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.339.0...1.339.1
[1.339.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.338.0...1.339.0
[1.338.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.337.0...1.338.0
[1.337.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.336.1...1.337.0
[1.336.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.336.0...1.336.1
[1.336.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.335.0...1.336.0
[1.335.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.334.0...1.335.0
[1.334.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.333.0...1.334.0
[1.333.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.332.0...1.333.0
[1.332.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.331.0...1.332.0
[1.331.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.330.0...1.331.0
[1.330.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.329.0...1.330.0
[1.329.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.328.0...1.329.0
[1.328.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.327.6...1.328.0
[1.327.6]: https://github.com/PolicyEngine/policyengine-us/compare/1.327.5...1.327.6
[1.327.5]: https://github.com/PolicyEngine/policyengine-us/compare/1.327.4...1.327.5
[1.327.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.327.3...1.327.4
[1.327.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.327.2...1.327.3
[1.327.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.327.1...1.327.2
[1.327.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.327.0...1.327.1
[1.327.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.326.0...1.327.0
[1.326.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.325.0...1.326.0
[1.325.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.324.0...1.325.0
[1.324.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.323.0...1.324.0
[1.323.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.322.0...1.323.0
[1.322.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.321.1...1.322.0
[1.321.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.321.0...1.321.1
[1.321.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.320.0...1.321.0
[1.320.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.319.0...1.320.0
[1.319.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.318.0...1.319.0
[1.318.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.317.0...1.318.0
[1.317.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.316.0...1.317.0
[1.316.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.315.0...1.316.0
[1.315.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.314.2...1.315.0
[1.314.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.314.1...1.314.2
[1.314.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.314.0...1.314.1
[1.314.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.313.0...1.314.0
[1.313.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.312.3...1.313.0
[1.312.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.312.2...1.312.3
[1.312.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.312.1...1.312.2
[1.312.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.312.0...1.312.1
[1.312.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.311.0...1.312.0
[1.311.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.310.0...1.311.0
[1.310.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.309.1...1.310.0
[1.309.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.309.0...1.309.1
[1.309.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.308.0...1.309.0
[1.308.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.307.1...1.308.0
[1.307.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.307.0...1.307.1
[1.307.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.306.0...1.307.0
[1.306.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.305.0...1.306.0
[1.305.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.304.0...1.305.0
[1.304.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.303.0...1.304.0
[1.303.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.302.0...1.303.0
[1.302.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.301.0...1.302.0
[1.301.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.300.0...1.301.0
[1.300.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.299.1...1.300.0
[1.299.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.299.0...1.299.1
[1.299.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.298.0...1.299.0
[1.298.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.297.2...1.298.0
[1.297.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.297.1...1.297.2
[1.297.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.297.0...1.297.1
[1.297.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.296.0...1.297.0
[1.296.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.295.1...1.296.0
[1.295.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.295.0...1.295.1
[1.295.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.294.0...1.295.0
[1.294.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.293.0...1.294.0
[1.293.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.292.0...1.293.0
[1.292.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.291.0...1.292.0
[1.291.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.290.0...1.291.0
[1.290.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.289.1...1.290.0
[1.289.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.289.0...1.289.1
[1.289.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.288.0...1.289.0
[1.288.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.287.2...1.288.0
[1.287.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.287.1...1.287.2
[1.287.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.287.0...1.287.1
[1.287.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.286.0...1.287.0
[1.286.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.285.0...1.286.0
[1.285.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.284.0...1.285.0
[1.284.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.283.0...1.284.0
[1.283.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.282.2...1.283.0
[1.282.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.282.1...1.282.2
[1.282.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.282.0...1.282.1
[1.282.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.281.0...1.282.0
[1.281.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.280.1...1.281.0
[1.280.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.280.0...1.280.1
[1.280.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.279.1...1.280.0
[1.279.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.279.0...1.279.1
[1.279.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.278.0...1.279.0
[1.278.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.277.0...1.278.0
[1.277.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.276.0...1.277.0
[1.276.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.275.0...1.276.0
[1.275.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.274.1...1.275.0
[1.274.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.274.0...1.274.1
[1.274.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.273.0...1.274.0
[1.273.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.272.1...1.273.0
[1.272.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.272.0...1.272.1
[1.272.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.271.0...1.272.0
[1.271.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.270.3...1.271.0
[1.270.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.270.2...1.270.3
[1.270.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.270.1...1.270.2
[1.270.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.270.0...1.270.1
[1.270.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.269.2...1.270.0
[1.269.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.269.1...1.269.2
[1.269.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.269.0...1.269.1
[1.269.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.268.0...1.269.0
[1.268.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.267.0...1.268.0
[1.267.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.266.0...1.267.0
[1.266.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.265.3...1.266.0
[1.265.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.265.2...1.265.3
[1.265.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.265.1...1.265.2
[1.265.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.265.0...1.265.1
[1.265.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.264.1...1.265.0
[1.264.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.264.0...1.264.1
[1.264.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.263.0...1.264.0
[1.263.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.262.1...1.263.0
[1.262.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.262.0...1.262.1
[1.262.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.261.0...1.262.0
[1.261.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.260.0...1.261.0
[1.260.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.259.0...1.260.0
[1.259.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.258.4...1.259.0
[1.258.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.258.3...1.258.4
[1.258.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.258.2...1.258.3
[1.258.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.258.1...1.258.2
[1.258.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.258.0...1.258.1
[1.258.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.257.0...1.258.0
[1.257.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.256.1...1.257.0
[1.256.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.256.0...1.256.1
[1.256.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.255.0...1.256.0
[1.255.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.254.0...1.255.0
[1.254.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.253.1...1.254.0
[1.253.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.253.0...1.253.1
[1.253.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.252.1...1.253.0
[1.252.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.252.0...1.252.1
[1.252.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.251.1...1.252.0
[1.251.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.251.0...1.251.1
[1.251.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.250.0...1.251.0
[1.250.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.249.0...1.250.0
[1.249.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.248.2...1.249.0
[1.248.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.248.1...1.248.2
[1.248.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.248.0...1.248.1
[1.248.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.247.1...1.248.0
[1.247.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.247.0...1.247.1
[1.247.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.246.0...1.247.0
[1.246.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.245.1...1.246.0
[1.245.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.245.0...1.245.1
[1.245.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.244.1...1.245.0
[1.244.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.244.0...1.244.1
[1.244.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.243.0...1.244.0
[1.243.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.242.1...1.243.0
[1.242.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.242.0...1.242.1
[1.242.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.241.0...1.242.0
[1.241.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.240.5...1.241.0
[1.240.5]: https://github.com/PolicyEngine/policyengine-us/compare/1.240.4...1.240.5
[1.240.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.240.3...1.240.4
[1.240.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.240.2...1.240.3
[1.240.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.240.1...1.240.2
[1.240.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.240.0...1.240.1
[1.240.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.239.0...1.240.0
[1.239.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.238.0...1.239.0
[1.238.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.237.0...1.238.0
[1.237.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.236.0...1.237.0
[1.236.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.235.0...1.236.0
[1.235.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.234.0...1.235.0
[1.234.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.233.0...1.234.0
[1.233.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.232.0...1.233.0
[1.232.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.231.0...1.232.0
[1.231.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.230.0...1.231.0
[1.230.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.229.0...1.230.0
[1.229.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.228.0...1.229.0
[1.228.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.227.1...1.228.0
[1.227.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.227.0...1.227.1
[1.227.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.226.1...1.227.0
[1.226.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.226.0...1.226.1
[1.226.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.225.0...1.226.0
[1.225.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.224.0...1.225.0
[1.224.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.223.0...1.224.0
[1.223.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.222.0...1.223.0
[1.222.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.221.0...1.222.0
[1.221.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.220.4...1.221.0
[1.220.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.220.3...1.220.4
[1.220.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.220.2...1.220.3
[1.220.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.220.1...1.220.2
[1.220.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.220.0...1.220.1
[1.220.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.219.2...1.220.0
[1.219.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.219.1...1.219.2
[1.219.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.219.0...1.219.1
[1.219.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.218.0...1.219.0
[1.218.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.217.1...1.218.0
[1.217.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.217.0...1.217.1
[1.217.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.216.0...1.217.0
[1.216.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.215.0...1.216.0
[1.215.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.214.0...1.215.0
[1.214.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.213.1...1.214.0
[1.213.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.213.0...1.213.1
[1.213.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.212.0...1.213.0
[1.212.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.211.0...1.212.0
[1.211.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.210.0...1.211.0
[1.210.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.209.2...1.210.0
[1.209.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.209.1...1.209.2
[1.209.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.209.0...1.209.1
[1.209.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.208.0...1.209.0
[1.208.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.207.5...1.208.0
[1.207.5]: https://github.com/PolicyEngine/policyengine-us/compare/1.207.4...1.207.5
[1.207.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.207.3...1.207.4
[1.207.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.207.2...1.207.3
[1.207.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.207.1...1.207.2
[1.207.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.207.0...1.207.1
[1.207.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.206.0...1.207.0
[1.206.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.205.0...1.206.0
[1.205.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.204.1...1.205.0
[1.204.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.204.0...1.204.1
[1.204.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.203.2...1.204.0
[1.203.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.203.1...1.203.2
[1.203.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.203.0...1.203.1
[1.203.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.202.2...1.203.0
[1.202.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.202.1...1.202.2
[1.202.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.202.0...1.202.1
[1.202.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.201.0...1.202.0
[1.201.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.200.2...1.201.0
[1.200.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.200.1...1.200.2
[1.200.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.200.0...1.200.1
[1.200.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.199.0...1.200.0
[1.199.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.198.1...1.199.0
[1.198.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.198.0...1.198.1
[1.198.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.197.1...1.198.0
[1.197.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.197.0...1.197.1
[1.197.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.196.1...1.197.0
[1.196.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.196.0...1.196.1
[1.196.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.195.1...1.196.0
[1.195.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.195.0...1.195.1
[1.195.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.194.0...1.195.0
[1.194.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.193.0...1.194.0
[1.193.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.192.2...1.193.0
[1.192.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.192.1...1.192.2
[1.192.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.192.0...1.192.1
[1.192.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.191.0...1.192.0
[1.191.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.190.0...1.191.0
[1.190.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.189.0...1.190.0
[1.189.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.188.0...1.189.0
[1.188.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.187.3...1.188.0
[1.187.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.187.2...1.187.3
[1.187.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.187.1...1.187.2
[1.187.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.187.0...1.187.1
[1.187.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.186.0...1.187.0
[1.186.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.185.0...1.186.0
[1.185.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.184.0...1.185.0
[1.184.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.183.1...1.184.0
[1.183.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.183.0...1.183.1
[1.183.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.182.2...1.183.0
[1.182.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.182.1...1.182.2
[1.182.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.182.0...1.182.1
[1.182.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.181.0...1.182.0
[1.181.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.180.4...1.181.0
[1.180.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.180.3...1.180.4
[1.180.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.180.2...1.180.3
[1.180.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.180.1...1.180.2
[1.180.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.180.0...1.180.1
[1.180.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.179.0...1.180.0
[1.179.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.178.0...1.179.0
[1.178.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.177.0...1.178.0
[1.177.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.176.3...1.177.0
[1.176.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.176.2...1.176.3
[1.176.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.176.1...1.176.2
[1.176.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.176.0...1.176.1
[1.176.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.175.0...1.176.0
[1.175.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.174.1...1.175.0
[1.174.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.174.0...1.174.1
[1.174.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.173.0...1.174.0
[1.173.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.172.1...1.173.0
[1.172.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.172.0...1.172.1
[1.172.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.171.0...1.172.0
[1.171.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.170.2...1.171.0
[1.170.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.170.1...1.170.2
[1.170.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.170.0...1.170.1
[1.170.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.169.0...1.170.0
[1.169.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.168.1...1.169.0
[1.168.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.168.0...1.168.1
[1.168.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.167.2...1.168.0
[1.167.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.167.1...1.167.2
[1.167.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.167.0...1.167.1
[1.167.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.166.0...1.167.0
[1.166.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.165.0...1.166.0
[1.165.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.164.0...1.165.0
[1.164.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.163.1...1.164.0
[1.163.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.163.0...1.163.1
[1.163.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.162.3...1.163.0
[1.162.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.162.2...1.162.3
[1.162.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.162.1...1.162.2
[1.162.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.162.0...1.162.1
[1.162.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.161.3...1.162.0
[1.161.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.161.2...1.161.3
[1.161.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.161.1...1.161.2
[1.161.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.161.0...1.161.1
[1.161.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.160.0...1.161.0
[1.160.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.159.0...1.160.0
[1.159.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.158.0...1.159.0
[1.158.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.157.0...1.158.0
[1.157.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.156.0...1.157.0
[1.156.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.155.1...1.156.0
[1.155.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.155.0...1.155.1
[1.155.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.154.2...1.155.0
[1.154.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.154.1...1.154.2
[1.154.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.154.0...1.154.1
[1.154.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.153.0...1.154.0
[1.153.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.152.0...1.153.0
[1.152.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.151.0...1.152.0
[1.151.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.150.1...1.151.0
[1.150.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.150.0...1.150.1
[1.150.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.149.0...1.150.0
[1.149.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.148.0...1.149.0
[1.148.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.147.0...1.148.0
[1.147.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.146.2...1.147.0
[1.146.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.146.1...1.146.2
[1.146.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.146.0...1.146.1
[1.146.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.145.0...1.146.0
[1.145.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.144.0...1.145.0
[1.144.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.143.0...1.144.0
[1.143.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.142.5...1.143.0
[1.142.5]: https://github.com/PolicyEngine/policyengine-us/compare/1.142.4...1.142.5
[1.142.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.142.3...1.142.4
[1.142.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.142.2...1.142.3
[1.142.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.142.1...1.142.2
[1.142.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.142.0...1.142.1
[1.142.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.141.0...1.142.0
[1.141.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.140.1...1.141.0
[1.140.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.140.0...1.140.1
[1.140.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.139.2...1.140.0
[1.139.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.139.1...1.139.2
[1.139.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.139.0...1.139.1
[1.139.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.138.0...1.139.0
[1.138.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.137.4...1.138.0
[1.137.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.137.3...1.137.4
[1.137.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.137.2...1.137.3
[1.137.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.137.1...1.137.2
[1.137.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.137.0...1.137.1
[1.137.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.136.2...1.137.0
[1.136.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.136.1...1.136.2
[1.136.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.136.0...1.136.1
[1.136.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.135.0...1.136.0
[1.135.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.134.0...1.135.0
[1.134.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.133.0...1.134.0
[1.133.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.132.0...1.133.0
[1.132.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.131.0...1.132.0
[1.131.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.130.0...1.131.0
[1.130.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.129.3...1.130.0
[1.129.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.129.2...1.129.3
[1.129.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.129.1...1.129.2
[1.129.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.129.0...1.129.1
[1.129.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.128.0...1.129.0
[1.128.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.127.0...1.128.0
[1.127.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.126.0...1.127.0
[1.126.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.125.0...1.126.0
[1.125.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.124.0...1.125.0
[1.124.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.123.0...1.124.0
[1.123.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.122.0...1.123.0
[1.122.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.121.0...1.122.0
[1.121.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.120.0...1.121.0
[1.120.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.119.0...1.120.0
[1.119.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.118.0...1.119.0
[1.118.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.117.0...1.118.0
[1.117.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.116.0...1.117.0
[1.116.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.115.0...1.116.0
[1.115.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.114.0...1.115.0
[1.114.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.113.0...1.114.0
[1.113.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.112.0...1.113.0
[1.112.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.111.0...1.112.0
[1.111.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.110.0...1.111.0
[1.110.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.109.0...1.110.0
[1.109.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.108.0...1.109.0
[1.108.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.107.0...1.108.0
[1.107.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.106.0...1.107.0
[1.106.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.105.2...1.106.0
[1.105.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.105.1...1.105.2
[1.105.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.105.0...1.105.1
[1.105.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.104.0...1.105.0
[1.104.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.103.0...1.104.0
[1.103.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.102.0...1.103.0
[1.102.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.101.0...1.102.0
[1.101.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.100.0...1.101.0
[1.100.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.99.1...1.100.0
[1.99.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.99.0...1.99.1
[1.99.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.98.0...1.99.0
[1.98.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.97.0...1.98.0
[1.97.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.96.0...1.97.0
[1.96.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.95.0...1.96.0
[1.95.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.94.0...1.95.0
[1.94.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.93.0...1.94.0
[1.93.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.92.1...1.93.0
[1.92.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.92.0...1.92.1
[1.92.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.91.0...1.92.0
[1.91.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.90.0...1.91.0
[1.90.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.89.0...1.90.0
[1.89.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.88.0...1.89.0
[1.88.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.87.0...1.88.0
[1.87.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.86.0...1.87.0
[1.86.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.85.4...1.86.0
[1.85.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.85.3...1.85.4
[1.85.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.85.2...1.85.3
[1.85.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.85.1...1.85.2
[1.85.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.85.0...1.85.1
[1.85.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.84.0...1.85.0
[1.84.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.83.1...1.84.0
[1.83.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.83.0...1.83.1
[1.83.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.82.0...1.83.0
[1.82.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.81.0...1.82.0
[1.81.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.80.1...1.81.0
[1.80.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.80.0...1.80.1
[1.80.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.79.3...1.80.0
[1.79.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.79.2...1.79.3
[1.79.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.79.1...1.79.2
[1.79.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.79.0...1.79.1
[1.79.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.78.1...1.79.0
[1.78.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.78.0...1.78.1
[1.78.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.77.0...1.78.0
[1.77.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.76.3...1.77.0
[1.76.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.76.2...1.76.3
[1.76.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.76.1...1.76.2
[1.76.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.76.0...1.76.1
[1.76.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.75.1...1.76.0
[1.75.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.75.0...1.75.1
[1.75.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.74.0...1.75.0
[1.74.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.73.0...1.74.0
[1.73.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.72.2...1.73.0
[1.72.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.72.1...1.72.2
[1.72.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.72.0...1.72.1
[1.72.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.71.1...1.72.0
[1.71.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.71.0...1.71.1
[1.71.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.70.0...1.71.0
[1.70.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.69.1...1.70.0
[1.69.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.69.0...1.69.1
[1.69.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.68.0...1.69.0
[1.68.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.67.0...1.68.0
[1.67.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.66.0...1.67.0
[1.66.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.65.1...1.66.0
[1.65.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.65.0...1.65.1
[1.65.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.64.0...1.65.0
[1.64.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.63.0...1.64.0
[1.63.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.62.0...1.63.0
[1.62.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.61.2...1.62.0
[1.61.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.61.1...1.61.2
[1.61.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.61.0...1.61.1
[1.61.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.60.0...1.61.0
[1.60.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.59.0...1.60.0
[1.59.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.58.0...1.59.0
[1.58.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.57.1...1.58.0
[1.57.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.57.0...1.57.1
[1.57.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.56.1...1.57.0
[1.56.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.56.0...1.56.1
[1.56.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.55.0...1.56.0
[1.55.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.54.4...1.55.0
[1.54.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.54.3...1.54.4
[1.54.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.54.2...1.54.3
[1.54.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.54.1...1.54.2
[1.54.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.54.0...1.54.1
[1.54.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.53.0...1.54.0
[1.53.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.52.0...1.53.0
[1.52.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.51.1...1.52.0
[1.51.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.51.0...1.51.1
[1.51.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.50.0...1.51.0
[1.50.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.49.0...1.50.0
[1.49.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.48.0...1.49.0
[1.48.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.47.0...1.48.0
[1.47.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.46.0...1.47.0
[1.46.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.45.2...1.46.0
[1.45.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.45.1...1.45.2
[1.45.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.45.0...1.45.1
[1.45.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.44.1...1.45.0
[1.44.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.44.0...1.44.1
[1.44.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.43.1...1.44.0
[1.43.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.43.0...1.43.1
[1.43.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.42.1...1.43.0
[1.42.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.42.0...1.42.1
[1.42.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.41.0...1.42.0
[1.41.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.40.1...1.41.0
[1.40.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.40.0...1.40.1
[1.40.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.39.0...1.40.0
[1.39.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.38.0...1.39.0
[1.38.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.37.0...1.38.0
[1.37.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.36.0...1.37.0
[1.36.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.35.0...1.36.0
[1.35.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.34.7...1.35.0
[1.34.7]: https://github.com/PolicyEngine/policyengine-us/compare/1.34.6...1.34.7
[1.34.6]: https://github.com/PolicyEngine/policyengine-us/compare/1.34.5...1.34.6
[1.34.5]: https://github.com/PolicyEngine/policyengine-us/compare/1.34.4...1.34.5
[1.34.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.34.3...1.34.4
[1.34.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.34.2...1.34.3
[1.34.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.34.1...1.34.2
[1.34.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.34.0...1.34.1
[1.34.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.33.1...1.34.0
[1.33.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.33.0...1.33.1
[1.33.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.32.0...1.33.0
[1.32.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.31.4...1.32.0
[1.31.4]: https://github.com/PolicyEngine/policyengine-us/compare/1.31.3...1.31.4
[1.31.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.31.2...1.31.3
[1.31.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.31.1...1.31.2
[1.31.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.31.0...1.31.1
[1.31.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.30.1...1.31.0
[1.30.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.30.0...1.30.1
[1.30.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.29.0...1.30.0
[1.29.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.28.0...1.29.0
[1.28.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.27.0...1.28.0
[1.27.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.26.2...1.27.0
[1.26.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.26.1...1.26.2
[1.26.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.26.0...1.26.1
[1.26.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.25.2...1.26.0
[1.25.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.25.1...1.25.2
[1.25.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.25.0...1.25.1
[1.25.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.24.1...1.25.0
[1.24.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.24.0...1.24.1
[1.24.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.23.1...1.24.0
[1.23.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.23.0...1.23.1
[1.23.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.22.1...1.23.0
[1.22.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.22.0...1.22.1
[1.22.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.21.0...1.22.0
[1.21.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.20.0...1.21.0
[1.20.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.19.0...1.20.0
[1.19.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.18.0...1.19.0
[1.18.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.17.1...1.18.0
[1.17.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.17.0...1.17.1
[1.17.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.16.3...1.17.0
[1.16.3]: https://github.com/PolicyEngine/policyengine-us/compare/1.16.2...1.16.3
[1.16.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.16.1...1.16.2
[1.16.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.16.0...1.16.1
[1.16.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.15.0...1.16.0
[1.15.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.14.0...1.15.0
[1.14.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.13.0...1.14.0
[1.13.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.12.0...1.13.0
[1.12.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.11.0...1.12.0
[1.11.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.10.0...1.11.0
[1.10.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.9.0...1.10.0
[1.9.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.8.0...1.9.0
[1.8.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.7.0...1.8.0
[1.7.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.6.0...1.7.0
[1.6.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.5.2...1.6.0
[1.5.2]: https://github.com/PolicyEngine/policyengine-us/compare/1.5.1...1.5.2
[1.5.1]: https://github.com/PolicyEngine/policyengine-us/compare/1.5.0...1.5.1
[1.5.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.4.0...1.5.0
[1.4.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.3.0...1.4.0
[1.3.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.2.0...1.3.0
[1.2.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.1.0...1.2.0
[1.1.0]: https://github.com/PolicyEngine/policyengine-us/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.796.1...1.0.0
[0.796.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.796.0...0.796.1
[0.796.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.795.0...0.796.0
[0.795.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.794.2...0.795.0
[0.794.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.794.1...0.794.2
[0.794.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.794.0...0.794.1
[0.794.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.793.0...0.794.0
[0.793.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.792.0...0.793.0
[0.792.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.791.0...0.792.0
[0.791.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.790.0...0.791.0
[0.790.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.789.0...0.790.0
[0.789.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.788.0...0.789.0
[0.788.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.787.0...0.788.0
[0.787.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.786.0...0.787.0
[0.786.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.785.2...0.786.0
[0.785.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.785.1...0.785.2
[0.785.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.785.0...0.785.1
[0.785.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.784.0...0.785.0
[0.784.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.783.0...0.784.0
[0.783.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.782.0...0.783.0
[0.782.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.781.0...0.782.0
[0.781.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.780.2...0.781.0
[0.780.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.780.1...0.780.2
[0.780.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.780.0...0.780.1
[0.780.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.779.2...0.780.0
[0.779.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.779.1...0.779.2
[0.779.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.779.0...0.779.1
[0.779.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.778.0...0.779.0
[0.778.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.777.7...0.778.0
[0.777.7]: https://github.com/PolicyEngine/policyengine-us/compare/0.777.6...0.777.7
[0.777.6]: https://github.com/PolicyEngine/policyengine-us/compare/0.777.5...0.777.6
[0.777.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.777.4...0.777.5
[0.777.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.777.3...0.777.4
[0.777.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.777.2...0.777.3
[0.777.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.777.1...0.777.2
[0.777.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.777.0...0.777.1
[0.777.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.776.0...0.777.0
[0.776.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.775.2...0.776.0
[0.775.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.775.1...0.775.2
[0.775.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.775.0...0.775.1
[0.775.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.774.0...0.775.0
[0.774.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.773.0...0.774.0
[0.773.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.772.0...0.773.0
[0.772.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.771.0...0.772.0
[0.771.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.770.1...0.771.0
[0.770.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.770.0...0.770.1
[0.770.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.769.0...0.770.0
[0.769.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.768.1...0.769.0
[0.768.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.768.0...0.768.1
[0.768.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.767.0...0.768.0
[0.767.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.766.0...0.767.0
[0.766.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.765.0...0.766.0
[0.765.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.764.0...0.765.0
[0.764.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.763.0...0.764.0
[0.763.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.762.0...0.763.0
[0.762.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.761.0...0.762.0
[0.761.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.760.0...0.761.0
[0.760.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.759.1...0.760.0
[0.759.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.759.0...0.759.1
[0.759.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.758.2...0.759.0
[0.758.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.758.1...0.758.2
[0.758.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.758.0...0.758.1
[0.758.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.757.1...0.758.0
[0.757.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.757.0...0.757.1
[0.757.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.756.0...0.757.0
[0.756.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.755.0...0.756.0
[0.755.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.754.0...0.755.0
[0.754.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.753.0...0.754.0
[0.753.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.752.1...0.753.0
[0.752.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.752.0...0.752.1
[0.752.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.751.0...0.752.0
[0.751.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.750.4...0.751.0
[0.750.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.750.3...0.750.4
[0.750.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.750.2...0.750.3
[0.750.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.750.1...0.750.2
[0.750.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.750.0...0.750.1
[0.750.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.749.1...0.750.0
[0.749.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.749.0...0.749.1
[0.749.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.748.1...0.749.0
[0.748.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.748.0...0.748.1
[0.748.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.747.0...0.748.0
[0.747.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.746.0...0.747.0
[0.746.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.745.0...0.746.0
[0.745.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.744.1...0.745.0
[0.744.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.744.0...0.744.1
[0.744.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.743.1...0.744.0
[0.743.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.743.0...0.743.1
[0.743.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.742.2...0.743.0
[0.742.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.742.1...0.742.2
[0.742.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.742.0...0.742.1
[0.742.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.741.1...0.742.0
[0.741.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.741.0...0.741.1
[0.741.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.740.0...0.741.0
[0.740.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.739.0...0.740.0
[0.739.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.738.0...0.739.0
[0.738.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.737.1...0.738.0
[0.737.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.737.0...0.737.1
[0.737.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.736.0...0.737.0
[0.736.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.735.0...0.736.0
[0.735.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.734.1...0.735.0
[0.734.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.734.0...0.734.1
[0.734.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.733.1...0.734.0
[0.733.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.733.0...0.733.1
[0.733.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.732.0...0.733.0
[0.732.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.731.0...0.732.0
[0.731.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.730.1...0.731.0
[0.730.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.730.0...0.730.1
[0.730.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.729.1...0.730.0
[0.729.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.729.0...0.729.1
[0.729.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.728.0...0.729.0
[0.728.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.727.2...0.728.0
[0.727.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.727.1...0.727.2
[0.727.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.727.0...0.727.1
[0.727.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.726.0...0.727.0
[0.726.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.725.0...0.726.0
[0.725.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.724.0...0.725.0
[0.724.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.723.0...0.724.0
[0.723.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.722.2...0.723.0
[0.722.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.722.1...0.722.2
[0.722.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.722.0...0.722.1
[0.722.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.721.1...0.722.0
[0.721.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.721.0...0.721.1
[0.721.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.720.0...0.721.0
[0.720.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.719.1...0.720.0
[0.719.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.719.0...0.719.1
[0.719.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.718.0...0.719.0
[0.718.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.717.0...0.718.0
[0.717.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.716.2...0.717.0
[0.716.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.716.1...0.716.2
[0.716.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.716.0...0.716.1
[0.716.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.715.0...0.716.0
[0.715.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.714.0...0.715.0
[0.714.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.713.3...0.714.0
[0.713.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.713.2...0.713.3
[0.713.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.713.1...0.713.2
[0.713.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.713.0...0.713.1
[0.713.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.712.0...0.713.0
[0.712.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.711.6...0.712.0
[0.711.6]: https://github.com/PolicyEngine/policyengine-us/compare/0.711.5...0.711.6
[0.711.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.711.4...0.711.5
[0.711.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.711.3...0.711.4
[0.711.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.711.2...0.711.3
[0.711.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.711.1...0.711.2
[0.711.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.711.0...0.711.1
[0.711.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.710.1...0.711.0
[0.710.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.710.0...0.710.1
[0.710.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.709.0...0.710.0
[0.709.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.708.8...0.709.0
[0.708.8]: https://github.com/PolicyEngine/policyengine-us/compare/0.708.7...0.708.8
[0.708.7]: https://github.com/PolicyEngine/policyengine-us/compare/0.708.6...0.708.7
[0.708.6]: https://github.com/PolicyEngine/policyengine-us/compare/0.708.5...0.708.6
[0.708.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.708.4...0.708.5
[0.708.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.708.3...0.708.4
[0.708.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.708.2...0.708.3
[0.708.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.708.1...0.708.2
[0.708.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.708.0...0.708.1
[0.708.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.707.0...0.708.0
[0.707.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.706.0...0.707.0
[0.706.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.705.0...0.706.0
[0.705.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.704.0...0.705.0
[0.704.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.703.0...0.704.0
[0.703.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.702.0...0.703.0
[0.702.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.701.0...0.702.0
[0.701.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.700.0...0.701.0
[0.700.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.699.2...0.700.0
[0.699.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.699.1...0.699.2
[0.699.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.699.0...0.699.1
[0.699.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.698.0...0.699.0
[0.698.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.697.2...0.698.0
[0.697.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.697.1...0.697.2
[0.697.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.697.0...0.697.1
[0.697.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.696.2...0.697.0
[0.696.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.696.1...0.696.2
[0.696.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.696.0...0.696.1
[0.696.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.695.3...0.696.0
[0.695.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.695.2...0.695.3
[0.695.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.695.1...0.695.2
[0.695.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.695.0...0.695.1
[0.695.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.694.0...0.695.0
[0.694.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.693.1...0.694.0
[0.693.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.693.0...0.693.1
[0.693.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.692.0...0.693.0
[0.692.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.691.1...0.692.0
[0.691.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.691.0...0.691.1
[0.691.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.690.0...0.691.0
[0.690.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.689.1...0.690.0
[0.689.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.689.0...0.689.1
[0.689.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.688.5...0.689.0
[0.688.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.688.4...0.688.5
[0.688.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.688.3...0.688.4
[0.688.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.688.2...0.688.3
[0.688.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.688.1...0.688.2
[0.688.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.688.0...0.688.1
[0.688.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.687.0...0.688.0
[0.687.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.686.2...0.687.0
[0.686.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.686.1...0.686.2
[0.686.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.686.0...0.686.1
[0.686.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.685.1...0.686.0
[0.685.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.685.0...0.685.1
[0.685.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.684.0...0.685.0
[0.684.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.683.1...0.684.0
[0.683.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.683.0...0.683.1
[0.683.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.682.1...0.683.0
[0.682.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.682.0...0.682.1
[0.682.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.681.1...0.682.0
[0.681.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.681.0...0.681.1
[0.681.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.680.0...0.681.0
[0.680.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.679.1...0.680.0
[0.679.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.679.0...0.679.1
[0.679.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.678.2...0.679.0
[0.678.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.678.1...0.678.2
[0.678.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.678.0...0.678.1
[0.678.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.677.0...0.678.0
[0.677.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.676.1...0.677.0
[0.676.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.676.0...0.676.1
[0.676.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.675.0...0.676.0
[0.675.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.674.0...0.675.0
[0.674.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.673.0...0.674.0
[0.673.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.672.1...0.673.0
[0.672.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.672.0...0.672.1
[0.672.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.671.1...0.672.0
[0.671.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.671.0...0.671.1
[0.671.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.670.0...0.671.0
[0.670.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.669.1...0.670.0
[0.669.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.669.0...0.669.1
[0.669.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.668.1...0.669.0
[0.668.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.668.0...0.668.1
[0.668.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.667.2...0.668.0
[0.667.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.667.1...0.667.2
[0.667.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.667.0...0.667.1
[0.667.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.666.1...0.667.0
[0.666.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.666.0...0.666.1
[0.666.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.665.0...0.666.0
[0.665.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.664.0...0.665.0
[0.664.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.663.0...0.664.0
[0.663.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.662.0...0.663.0
[0.662.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.661.2...0.662.0
[0.661.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.661.1...0.661.2
[0.661.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.661.0...0.661.1
[0.661.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.660.0...0.661.0
[0.660.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.659.0...0.660.0
[0.659.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.658.1...0.659.0
[0.658.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.658.0...0.658.1
[0.658.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.657.0...0.658.0
[0.657.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.656.1...0.657.0
[0.656.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.656.0...0.656.1
[0.656.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.655.2...0.656.0
[0.655.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.655.1...0.655.2
[0.655.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.655.0...0.655.1
[0.655.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.654.2...0.655.0
[0.654.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.654.1...0.654.2
[0.654.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.654.0...0.654.1
[0.654.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.653.0...0.654.0
[0.653.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.652.1...0.653.0
[0.652.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.652.0...0.652.1
[0.652.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.651.4...0.652.0
[0.651.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.651.3...0.651.4
[0.651.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.651.2...0.651.3
[0.651.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.651.1...0.651.2
[0.651.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.651.0...0.651.1
[0.651.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.650.0...0.651.0
[0.650.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.649.0...0.650.0
[0.649.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.648.4...0.649.0
[0.648.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.648.3...0.648.4
[0.648.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.648.2...0.648.3
[0.648.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.648.1...0.648.2
[0.648.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.648.0...0.648.1
[0.648.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.647.1...0.648.0
[0.647.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.647.0...0.647.1
[0.647.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.646.1...0.647.0
[0.646.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.646.0...0.646.1
[0.646.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.645.0...0.646.0
[0.645.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.644.0...0.645.0
[0.644.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.643.0...0.644.0
[0.643.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.642.0...0.643.0
[0.642.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.641.1...0.642.0
[0.641.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.641.0...0.641.1
[0.641.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.640.1...0.641.0
[0.640.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.640.0...0.640.1
[0.640.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.639.0...0.640.0
[0.639.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.638.1...0.639.0
[0.638.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.638.0...0.638.1
[0.638.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.637.6...0.638.0
[0.637.6]: https://github.com/PolicyEngine/policyengine-us/compare/0.637.5...0.637.6
[0.637.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.637.4...0.637.5
[0.637.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.637.3...0.637.4
[0.637.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.637.2...0.637.3
[0.637.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.637.1...0.637.2
[0.637.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.637.0...0.637.1
[0.637.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.636.2...0.637.0
[0.636.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.636.1...0.636.2
[0.636.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.636.0...0.636.1
[0.636.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.635.1...0.636.0
[0.635.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.635.0...0.635.1
[0.635.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.634.4...0.635.0
[0.634.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.634.3...0.634.4
[0.634.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.634.2...0.634.3
[0.634.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.634.1...0.634.2
[0.634.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.634.0...0.634.1
[0.634.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.633.4...0.634.0
[0.633.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.633.3...0.633.4
[0.633.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.633.2...0.633.3
[0.633.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.633.1...0.633.2
[0.633.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.633.0...0.633.1
[0.633.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.632.0...0.633.0
[0.632.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.631.6...0.632.0
[0.631.6]: https://github.com/PolicyEngine/policyengine-us/compare/0.631.5...0.631.6
[0.631.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.631.4...0.631.5
[0.631.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.631.3...0.631.4
[0.631.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.631.2...0.631.3
[0.631.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.631.1...0.631.2
[0.631.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.631.0...0.631.1
[0.631.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.630.0...0.631.0
[0.630.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.629.2...0.630.0
[0.629.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.629.1...0.629.2
[0.629.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.629.0...0.629.1
[0.629.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.628.0...0.629.0
[0.628.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.627.1...0.628.0
[0.627.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.627.0...0.627.1
[0.627.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.626.0...0.627.0
[0.626.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.625.1...0.626.0
[0.625.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.625.0...0.625.1
[0.625.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.624.0...0.625.0
[0.624.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.623.0...0.624.0
[0.623.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.622.1...0.623.0
[0.622.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.622.0...0.622.1
[0.622.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.621.0...0.622.0
[0.621.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.620.3...0.621.0
[0.620.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.620.2...0.620.3
[0.620.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.620.1...0.620.2
[0.620.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.620.0...0.620.1
[0.620.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.619.0...0.620.0
[0.619.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.618.3...0.619.0
[0.618.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.618.2...0.618.3
[0.618.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.618.1...0.618.2
[0.618.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.618.0...0.618.1
[0.618.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.617.2...0.618.0
[0.617.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.617.1...0.617.2
[0.617.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.617.0...0.617.1
[0.617.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.616.0...0.617.0
[0.616.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.615.0...0.616.0
[0.615.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.614.0...0.615.0
[0.614.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.613.0...0.614.0
[0.613.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.612.0...0.613.0
[0.612.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.611.0...0.612.0
[0.611.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.610.1...0.611.0
[0.610.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.610.0...0.610.1
[0.610.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.609.1...0.610.0
[0.609.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.609.0...0.609.1
[0.609.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.608.0...0.609.0
[0.608.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.607.0...0.608.0
[0.607.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.606.1...0.607.0
[0.606.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.606.0...0.606.1
[0.606.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.605.0...0.606.0
[0.605.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.604.2...0.605.0
[0.604.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.604.1...0.604.2
[0.604.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.604.0...0.604.1
[0.604.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.603.3...0.604.0
[0.603.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.603.2...0.603.3
[0.603.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.603.1...0.603.2
[0.603.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.603.0...0.603.1
[0.603.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.602.1...0.603.0
[0.602.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.602.0...0.602.1
[0.602.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.601.2...0.602.0
[0.601.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.601.1...0.601.2
[0.601.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.601.0...0.601.1
[0.601.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.600.1...0.601.0
[0.600.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.600.0...0.600.1
[0.600.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.599.0...0.600.0
[0.599.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.598.0...0.599.0
[0.598.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.597.2...0.598.0
[0.597.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.597.1...0.597.2
[0.597.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.597.0...0.597.1
[0.597.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.596.0...0.597.0
[0.596.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.595.3...0.596.0
[0.595.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.595.2...0.595.3
[0.595.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.595.1...0.595.2
[0.595.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.595.0...0.595.1
[0.595.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.594.0...0.595.0
[0.594.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.593.0...0.594.0
[0.593.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.592.0...0.593.0
[0.592.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.591.1...0.592.0
[0.591.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.591.0...0.591.1
[0.591.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.590.0...0.591.0
[0.590.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.589.1...0.590.0
[0.589.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.589.0...0.589.1
[0.589.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.588.2...0.589.0
[0.588.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.588.1...0.588.2
[0.588.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.588.0...0.588.1
[0.588.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.587.0...0.588.0
[0.587.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.586.2...0.587.0
[0.586.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.586.1...0.586.2
[0.586.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.586.0...0.586.1
[0.586.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.585.2...0.586.0
[0.585.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.585.1...0.585.2
[0.585.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.585.0...0.585.1
[0.585.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.584.3...0.585.0
[0.584.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.584.2...0.584.3
[0.584.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.584.1...0.584.2
[0.584.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.584.0...0.584.1
[0.584.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.583.3...0.584.0
[0.583.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.583.2...0.583.3
[0.583.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.583.1...0.583.2
[0.583.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.583.0...0.583.1
[0.583.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.582.2...0.583.0
[0.582.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.582.1...0.582.2
[0.582.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.582.0...0.582.1
[0.582.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.581.1...0.582.0
[0.581.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.581.0...0.581.1
[0.581.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.580.1...0.581.0
[0.580.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.580.0...0.580.1
[0.580.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.579.1...0.580.0
[0.579.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.579.0...0.579.1
[0.579.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.578.0...0.579.0
[0.578.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.577.0...0.578.0
[0.577.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.576.1...0.577.0
[0.576.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.576.0...0.576.1
[0.576.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.575.0...0.576.0
[0.575.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.574.1...0.575.0
[0.574.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.574.0...0.574.1
[0.574.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.573.0...0.574.0
[0.573.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.572.0...0.573.0
[0.572.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.571.2...0.572.0
[0.571.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.571.1...0.571.2
[0.571.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.571.0...0.571.1
[0.571.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.570.4...0.571.0
[0.570.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.570.3...0.570.4
[0.570.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.570.2...0.570.3
[0.570.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.570.1...0.570.2
[0.570.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.570.0...0.570.1
[0.570.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.569.0...0.570.0
[0.569.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.568.0...0.569.0
[0.568.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.567.0...0.568.0
[0.567.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.566.0...0.567.0
[0.566.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.565.0...0.566.0
[0.565.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.564.1...0.565.0
[0.564.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.564.0...0.564.1
[0.564.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.563.1...0.564.0
[0.563.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.563.0...0.563.1
[0.563.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.562.0...0.563.0
[0.562.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.561.1...0.562.0
[0.561.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.561.0...0.561.1
[0.561.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.560.0...0.561.0
[0.560.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.559.0...0.560.0
[0.559.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.558.1...0.559.0
[0.558.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.558.0...0.558.1
[0.558.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.557.0...0.558.0
[0.557.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.556.0...0.557.0
[0.556.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.555.1...0.556.0
[0.555.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.555.0...0.555.1
[0.555.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.554.1...0.555.0
[0.554.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.554.0...0.554.1
[0.554.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.553.1...0.554.0
[0.553.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.553.0...0.553.1
[0.553.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.552.2...0.553.0
[0.552.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.552.1...0.552.2
[0.552.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.552.0...0.552.1
[0.552.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.551.0...0.552.0
[0.551.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.550.0...0.551.0
[0.550.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.549.0...0.550.0
[0.549.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.548.0...0.549.0
[0.548.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.547.0...0.548.0
[0.547.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.546.1...0.547.0
[0.546.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.546.0...0.546.1
[0.546.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.545.0...0.546.0
[0.545.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.544.0...0.545.0
[0.544.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.543.0...0.544.0
[0.543.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.542.0...0.543.0
[0.542.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.541.1...0.542.0
[0.541.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.541.0...0.541.1
[0.541.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.540.0...0.541.0
[0.540.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.539.0...0.540.0
[0.539.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.538.2...0.539.0
[0.538.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.538.1...0.538.2
[0.538.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.538.0...0.538.1
[0.538.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.537.1...0.538.0
[0.537.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.537.0...0.537.1
[0.537.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.536.1...0.537.0
[0.536.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.536.0...0.536.1
[0.536.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.535.1...0.536.0
[0.535.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.535.0...0.535.1
[0.535.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.534.0...0.535.0
[0.534.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.533.1...0.534.0
[0.533.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.533.0...0.533.1
[0.533.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.532.0...0.533.0
[0.532.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.531.0...0.532.0
[0.531.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.530.1...0.531.0
[0.530.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.530.0...0.530.1
[0.530.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.529.0...0.530.0
[0.529.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.528.0...0.529.0
[0.528.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.527.0...0.528.0
[0.527.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.526.0...0.527.0
[0.526.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.525.0...0.526.0
[0.525.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.524.0...0.525.0
[0.524.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.523.1...0.524.0
[0.523.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.523.0...0.523.1
[0.523.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.522.0...0.523.0
[0.522.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.521.0...0.522.0
[0.521.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.520.0...0.521.0
[0.520.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.519.0...0.520.0
[0.519.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.518.5...0.519.0
[0.518.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.518.4...0.518.5
[0.518.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.518.3...0.518.4
[0.518.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.518.2...0.518.3
[0.518.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.518.1...0.518.2
[0.518.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.518.0...0.518.1
[0.518.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.517.0...0.518.0
[0.517.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.516.3...0.517.0
[0.516.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.516.2...0.516.3
[0.516.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.516.1...0.516.2
[0.516.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.516.0...0.516.1
[0.516.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.515.0...0.516.0
[0.515.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.514.3...0.515.0
[0.514.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.514.2...0.514.3
[0.514.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.514.1...0.514.2
[0.514.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.514.0...0.514.1
[0.514.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.513.3...0.514.0
[0.513.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.513.2...0.513.3
[0.513.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.513.1...0.513.2
[0.513.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.513.0...0.513.1
[0.513.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.512.0...0.513.0
[0.512.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.511.0...0.512.0
[0.511.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.510.0...0.511.0
[0.510.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.509.0...0.510.0
[0.509.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.508.4...0.509.0
[0.508.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.508.3...0.508.4
[0.508.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.508.2...0.508.3
[0.508.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.508.1...0.508.2
[0.508.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.508.0...0.508.1
[0.508.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.507.1...0.508.0
[0.507.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.507.0...0.507.1
[0.507.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.506.1...0.507.0
[0.506.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.506.0...0.506.1
[0.506.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.505.0...0.506.0
[0.505.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.504.0...0.505.0
[0.504.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.503.1...0.504.0
[0.503.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.503.0...0.503.1
[0.503.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.502.1...0.503.0
[0.502.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.502.0...0.502.1
[0.502.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.501.1...0.502.0
[0.501.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.501.0...0.501.1
[0.501.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.500.0...0.501.0
[0.500.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.499.0...0.500.0
[0.499.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.498.0...0.499.0
[0.498.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.497.2...0.498.0
[0.497.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.497.1...0.497.2
[0.497.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.497.0...0.497.1
[0.497.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.496.0...0.497.0
[0.496.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.495.0...0.496.0
[0.495.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.494.1...0.495.0
[0.494.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.494.0...0.494.1
[0.494.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.493.1...0.494.0
[0.493.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.493.0...0.493.1
[0.493.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.492.0...0.493.0
[0.492.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.491.0...0.492.0
[0.491.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.490.0...0.491.0
[0.490.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.489.1...0.490.0
[0.489.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.489.0...0.489.1
[0.489.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.488.1...0.489.0
[0.488.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.488.0...0.488.1
[0.488.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.487.0...0.488.0
[0.487.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.486.0...0.487.0
[0.486.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.485.0...0.486.0
[0.485.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.484.0...0.485.0
[0.484.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.483.0...0.484.0
[0.483.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.482.2...0.483.0
[0.482.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.482.1...0.482.2
[0.482.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.482.0...0.482.1
[0.482.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.481.0...0.482.0
[0.481.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.480.0...0.481.0
[0.480.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.479.1...0.480.0
[0.479.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.479.0...0.479.1
[0.479.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.478.0...0.479.0
[0.478.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.477.0...0.478.0
[0.477.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.476.1...0.477.0
[0.476.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.476.0...0.476.1
[0.476.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.475.0...0.476.0
[0.475.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.474.0...0.475.0
[0.474.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.473.0...0.474.0
[0.473.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.472.0...0.473.0
[0.472.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.471.1...0.472.0
[0.471.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.471.0...0.471.1
[0.471.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.470.1...0.471.0
[0.470.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.470.0...0.470.1
[0.470.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.469.0...0.470.0
[0.469.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.468.0...0.469.0
[0.468.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.467.0...0.468.0
[0.467.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.466.1...0.467.0
[0.466.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.466.0...0.466.1
[0.466.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.465.3...0.466.0
[0.465.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.465.2...0.465.3
[0.465.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.465.1...0.465.2
[0.465.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.465.0...0.465.1
[0.465.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.464.1...0.465.0
[0.464.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.464.0...0.464.1
[0.464.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.463.0...0.464.0
[0.463.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.462.3...0.463.0
[0.462.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.462.2...0.462.3
[0.462.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.462.1...0.462.2
[0.462.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.462.0...0.462.1
[0.462.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.461.1...0.462.0
[0.461.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.461.0...0.461.1
[0.461.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.460.1...0.461.0
[0.460.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.460.0...0.460.1
[0.460.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.459.0...0.460.0
[0.459.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.458.2...0.459.0
[0.458.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.458.1...0.458.2
[0.458.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.458.0...0.458.1
[0.458.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.457.0...0.458.0
[0.457.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.456.0...0.457.0
[0.456.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.455.0...0.456.0
[0.455.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.454.0...0.455.0
[0.454.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.453.0...0.454.0
[0.453.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.452.1...0.453.0
[0.452.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.452.0...0.452.1
[0.452.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.451.0...0.452.0
[0.451.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.450.0...0.451.0
[0.450.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.449.0...0.450.0
[0.449.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.448.0...0.449.0
[0.448.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.447.1...0.448.0
[0.447.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.447.0...0.447.1
[0.447.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.446.0...0.447.0
[0.446.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.445.0...0.446.0
[0.445.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.444.0...0.445.0
[0.444.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.443.0...0.444.0
[0.443.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.442.0...0.443.0
[0.442.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.441.0...0.442.0
[0.441.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.440.0...0.441.0
[0.440.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.439.1...0.440.0
[0.439.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.439.0...0.439.1
[0.439.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.438.0...0.439.0
[0.438.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.437.1...0.438.0
[0.437.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.437.0...0.437.1
[0.437.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.436.0...0.437.0
[0.436.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.435.0...0.436.0
[0.435.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.434.0...0.435.0
[0.434.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.433.0...0.434.0
[0.433.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.432.0...0.433.0
[0.432.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.431.3...0.432.0
[0.431.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.431.2...0.431.3
[0.431.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.431.1...0.431.2
[0.431.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.431.0...0.431.1
[0.431.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.430.0...0.431.0
[0.430.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.429.1...0.430.0
[0.429.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.429.0...0.429.1
[0.429.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.428.1...0.429.0
[0.428.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.428.0...0.428.1
[0.428.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.427.1...0.428.0
[0.427.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.427.0...0.427.1
[0.427.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.426.0...0.427.0
[0.426.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.425.1...0.426.0
[0.425.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.425.0...0.425.1
[0.425.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.424.1...0.425.0
[0.424.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.424.0...0.424.1
[0.424.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.423.2...0.424.0
[0.423.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.423.1...0.423.2
[0.423.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.423.0...0.423.1
[0.423.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.422.0...0.423.0
[0.422.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.421.0...0.422.0
[0.421.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.420.1...0.421.0
[0.420.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.420.0...0.420.1
[0.420.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.419.0...0.420.0
[0.419.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.418.0...0.419.0
[0.418.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.417.3...0.418.0
[0.417.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.417.2...0.417.3
[0.417.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.417.1...0.417.2
[0.417.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.417.0...0.417.1
[0.417.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.416.2...0.417.0
[0.416.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.416.1...0.416.2
[0.416.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.416.0...0.416.1
[0.416.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.415.0...0.416.0
[0.415.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.414.0...0.415.0
[0.414.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.413.0...0.414.0
[0.413.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.412.0...0.413.0
[0.412.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.411.0...0.412.0
[0.411.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.410.2...0.411.0
[0.410.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.410.1...0.410.2
[0.410.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.410.0...0.410.1
[0.410.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.409.3...0.410.0
[0.409.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.409.2...0.409.3
[0.409.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.409.1...0.409.2
[0.409.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.409.0...0.409.1
[0.409.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.408.0...0.409.0
[0.408.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.407.1...0.408.0
[0.407.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.407.0...0.407.1
[0.407.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.406.0...0.407.0
[0.406.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.405.0...0.406.0
[0.405.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.404.0...0.405.0
[0.404.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.403.3...0.404.0
[0.403.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.403.2...0.403.3
[0.403.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.403.1...0.403.2
[0.403.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.403.0...0.403.1
[0.403.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.402.0...0.403.0
[0.402.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.401.5...0.402.0
[0.401.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.401.4...0.401.5
[0.401.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.401.3...0.401.4
[0.401.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.401.2...0.401.3
[0.401.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.401.1...0.401.2
[0.401.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.401.0...0.401.1
[0.401.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.400.0...0.401.0
[0.400.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.399.0...0.400.0
[0.399.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.398.0...0.399.0
[0.398.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.397.0...0.398.0
[0.397.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.396.0...0.397.0
[0.396.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.395.0...0.396.0
[0.395.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.394.0...0.395.0
[0.394.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.393.0...0.394.0
[0.393.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.392.0...0.393.0
[0.392.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.391.0...0.392.0
[0.391.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.390.1...0.391.0
[0.390.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.390.0...0.390.1
[0.390.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.389.1...0.390.0
[0.389.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.389.0...0.389.1
[0.389.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.388.0...0.389.0
[0.388.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.387.1...0.388.0
[0.387.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.387.0...0.387.1
[0.387.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.386.0...0.387.0
[0.386.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.385.0...0.386.0
[0.385.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.384.0...0.385.0
[0.384.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.383.0...0.384.0
[0.383.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.382.0...0.383.0
[0.382.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.381.0...0.382.0
[0.381.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.380.0...0.381.0
[0.380.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.379.0...0.380.0
[0.379.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.378.0...0.379.0
[0.378.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.377.1...0.378.0
[0.377.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.377.0...0.377.1
[0.377.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.376.0...0.377.0
[0.376.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.375.0...0.376.0
[0.375.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.374.0...0.375.0
[0.374.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.373.0...0.374.0
[0.373.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.372.0...0.373.0
[0.372.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.371.0...0.372.0
[0.371.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.370.1...0.371.0
[0.370.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.370.0...0.370.1
[0.370.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.369.0...0.370.0
[0.369.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.368.1...0.369.0
[0.368.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.368.0...0.368.1
[0.368.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.367.0...0.368.0
[0.367.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.366.0...0.367.0
[0.366.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.365.0...0.366.0
[0.365.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.364.1...0.365.0
[0.364.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.364.0...0.364.1
[0.364.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.363.0...0.364.0
[0.363.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.362.0...0.363.0
[0.362.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.361.0...0.362.0
[0.361.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.360.1...0.361.0
[0.360.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.360.0...0.360.1
[0.360.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.359.1...0.360.0
[0.359.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.359.0...0.359.1
[0.359.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.358.1...0.359.0
[0.358.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.358.0...0.358.1
[0.358.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.357.2...0.358.0
[0.357.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.357.1...0.357.2
[0.357.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.357.0...0.357.1
[0.357.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.356.0...0.357.0
[0.356.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.355.0...0.356.0
[0.355.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.354.0...0.355.0
[0.354.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.353.0...0.354.0
[0.353.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.352.0...0.353.0
[0.352.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.351.0...0.352.0
[0.351.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.350.1...0.351.0
[0.350.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.350.0...0.350.1
[0.350.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.349.0...0.350.0
[0.349.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.348.2...0.349.0
[0.348.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.348.1...0.348.2
[0.348.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.348.0...0.348.1
[0.348.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.347.1...0.348.0
[0.347.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.347.0...0.347.1
[0.347.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.346.4...0.347.0
[0.346.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.346.3...0.346.4
[0.346.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.346.2...0.346.3
[0.346.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.346.1...0.346.2
[0.346.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.346.0...0.346.1
[0.346.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.345.12...0.346.0
[0.345.12]: https://github.com/PolicyEngine/policyengine-us/compare/0.345.11...0.345.12
[0.345.11]: https://github.com/PolicyEngine/policyengine-us/compare/0.345.10...0.345.11
[0.345.10]: https://github.com/PolicyEngine/policyengine-us/compare/0.345.9...0.345.10
[0.345.9]: https://github.com/PolicyEngine/policyengine-us/compare/0.345.8...0.345.9
[0.345.8]: https://github.com/PolicyEngine/policyengine-us/compare/0.345.7...0.345.8
[0.345.7]: https://github.com/PolicyEngine/policyengine-us/compare/0.345.6...0.345.7
[0.345.6]: https://github.com/PolicyEngine/policyengine-us/compare/0.345.5...0.345.6
[0.345.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.345.4...0.345.5
[0.345.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.345.3...0.345.4
[0.345.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.345.2...0.345.3
[0.345.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.345.1...0.345.2
[0.345.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.345.0...0.345.1
[0.345.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.344.0...0.345.0
[0.344.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.343.0...0.344.0
[0.343.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.342.0...0.343.0
[0.342.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.341.0...0.342.0
[0.341.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.340.0...0.341.0
[0.340.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.339.1...0.340.0
[0.339.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.339.0...0.339.1
[0.339.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.338.0...0.339.0
[0.338.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.337.1...0.338.0
[0.337.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.337.0...0.337.1
[0.337.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.336.0...0.337.0
[0.336.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.335.1...0.336.0
[0.335.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.335.0...0.335.1
[0.335.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.334.0...0.335.0
[0.334.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.333.1...0.334.0
[0.333.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.333.0...0.333.1
[0.333.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.332.0...0.333.0
[0.332.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.331.1...0.332.0
[0.331.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.331.0...0.331.1
[0.331.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.330.1...0.331.0
[0.330.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.330.0...0.330.1
[0.330.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.329.4...0.330.0
[0.329.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.329.3...0.329.4
[0.329.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.329.2...0.329.3
[0.329.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.329.1...0.329.2
[0.329.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.329.0...0.329.1
[0.329.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.328.0...0.329.0
[0.328.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.327.0...0.328.0
[0.327.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.326.0...0.327.0
[0.326.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.325.0...0.326.0
[0.325.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.324.0...0.325.0
[0.324.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.323.0...0.324.0
[0.323.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.322.0...0.323.0
[0.322.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.321.0...0.322.0
[0.321.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.320.1...0.321.0
[0.320.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.320.0...0.320.1
[0.320.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.319.0...0.320.0
[0.319.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.318.0...0.319.0
[0.318.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.317.1...0.318.0
[0.317.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.317.0...0.317.1
[0.317.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.316.1...0.317.0
[0.316.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.316.0...0.316.1
[0.316.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.315.0...0.316.0
[0.315.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.314.1...0.315.0
[0.314.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.314.0...0.314.1
[0.314.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.313.1...0.314.0
[0.313.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.313.0...0.313.1
[0.313.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.312.0...0.313.0
[0.312.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.311.0...0.312.0
[0.311.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.310.2...0.311.0
[0.310.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.310.1...0.310.2
[0.310.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.310.0...0.310.1
[0.310.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.309.0...0.310.0
[0.309.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.308.0...0.309.0
[0.308.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.307.0...0.308.0
[0.307.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.306.0...0.307.0
[0.306.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.305.0...0.306.0
[0.305.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.304.0...0.305.0
[0.304.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.303.1...0.304.0
[0.303.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.303.0...0.303.1
[0.303.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.302.0...0.303.0
[0.302.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.301.2...0.302.0
[0.301.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.301.1...0.301.2
[0.301.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.301.0...0.301.1
[0.301.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.300.4...0.301.0
[0.300.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.300.3...0.300.4
[0.300.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.300.2...0.300.3
[0.300.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.300.1...0.300.2
[0.300.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.300.0...0.300.1
[0.300.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.299.0...0.300.0
[0.299.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.298.0...0.299.0
[0.298.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.297.0...0.298.0
[0.297.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.296.0...0.297.0
[0.296.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.295.1...0.296.0
[0.295.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.295.0...0.295.1
[0.295.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.294.0...0.295.0
[0.294.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.293.1...0.294.0
[0.293.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.293.0...0.293.1
[0.293.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.292.0...0.293.0
[0.292.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.291.0...0.292.0
[0.291.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.290.0...0.291.0
[0.290.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.289.0...0.290.0
[0.289.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.288.0...0.289.0
[0.288.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.287.0...0.288.0
[0.287.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.286.2...0.287.0
[0.286.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.286.1...0.286.2
[0.286.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.286.0...0.286.1
[0.286.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.285.1...0.286.0
[0.285.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.285.0...0.285.1
[0.285.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.284.0...0.285.0
[0.284.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.283.0...0.284.0
[0.283.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.282.0...0.283.0
[0.282.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.281.1...0.282.0
[0.281.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.281.0...0.281.1
[0.281.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.280.0...0.281.0
[0.280.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.279.0...0.280.0
[0.279.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.278.0...0.279.0
[0.278.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.277.0...0.278.0
[0.277.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.276.0...0.277.0
[0.276.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.275.0...0.276.0
[0.275.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.274.0...0.275.0
[0.274.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.273.0...0.274.0
[0.273.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.272.0...0.273.0
[0.272.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.271.0...0.272.0
[0.271.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.270.0...0.271.0
[0.270.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.269.0...0.270.0
[0.269.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.268.0...0.269.0
[0.268.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.267.0...0.268.0
[0.267.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.266.0...0.267.0
[0.266.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.265.0...0.266.0
[0.265.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.264.0...0.265.0
[0.264.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.263.5...0.264.0
[0.263.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.263.4...0.263.5
[0.263.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.263.3...0.263.4
[0.263.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.263.2...0.263.3
[0.263.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.263.1...0.263.2
[0.263.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.263.0...0.263.1
[0.263.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.262.0...0.263.0
[0.262.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.261.1...0.262.0
[0.261.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.261.0...0.261.1
[0.261.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.260.1...0.261.0
[0.260.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.260.0...0.260.1
[0.260.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.259.1...0.260.0
[0.259.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.259.0...0.259.1
[0.259.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.258.0...0.259.0
[0.258.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.257.1...0.258.0
[0.257.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.257.0...0.257.1
[0.257.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.256.0...0.257.0
[0.256.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.255.0...0.256.0
[0.255.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.254.1...0.255.0
[0.254.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.254.0...0.254.1
[0.254.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.253.0...0.254.0
[0.253.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.252.0...0.253.0
[0.252.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.251.1...0.252.0
[0.251.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.251.0...0.251.1
[0.251.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.250.0...0.251.0
[0.250.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.249.0...0.250.0
[0.249.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.248.1...0.249.0
[0.248.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.248.0...0.248.1
[0.248.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.247.0...0.248.0
[0.247.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.246.0...0.247.0
[0.246.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.245.0...0.246.0
[0.245.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.244.0...0.245.0
[0.244.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.243.0...0.244.0
[0.243.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.242.0...0.243.0
[0.242.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.241.0...0.242.0
[0.241.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.240.0...0.241.0
[0.240.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.239.1...0.240.0
[0.239.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.239.0...0.239.1
[0.239.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.238.1...0.239.0
[0.238.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.238.0...0.238.1
[0.238.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.237.1...0.238.0
[0.237.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.237.0...0.237.1
[0.237.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.236.0...0.237.0
[0.236.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.235.0...0.236.0
[0.235.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.234.0...0.235.0
[0.234.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.233.0...0.234.0
[0.233.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.232.0...0.233.0
[0.232.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.231.2...0.232.0
[0.231.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.231.1...0.231.2
[0.231.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.231.0...0.231.1
[0.231.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.230.1...0.231.0
[0.230.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.230.0...0.230.1
[0.230.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.229.0...0.230.0
[0.229.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.228.0...0.229.0
[0.228.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.227.1...0.228.0
[0.227.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.227.0...0.227.1
[0.227.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.226.0...0.227.0
[0.226.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.225.0...0.226.0
[0.225.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.224.1...0.225.0
[0.224.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.224.0...0.224.1
[0.224.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.223.0...0.224.0
[0.223.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.222.2...0.223.0
[0.222.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.222.1...0.222.2
[0.222.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.222.0...0.222.1
[0.222.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.221.0...0.222.0
[0.221.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.220.5...0.221.0
[0.220.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.220.4...0.220.5
[0.220.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.220.3...0.220.4
[0.220.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.220.2...0.220.3
[0.220.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.220.1...0.220.2
[0.220.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.220.0...0.220.1
[0.220.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.219.1...0.220.0
[0.219.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.219.0...0.219.1
[0.219.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.218.0...0.219.0
[0.218.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.217.1...0.218.0
[0.217.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.217.0...0.217.1
[0.217.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.216.0...0.217.0
[0.216.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.215.2...0.216.0
[0.215.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.215.1...0.215.2
[0.215.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.215.0...0.215.1
[0.215.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.214.4...0.215.0
[0.214.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.214.3...0.214.4
[0.214.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.214.2...0.214.3
[0.214.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.214.1...0.214.2
[0.214.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.214.0...0.214.1
[0.214.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.213.4...0.214.0
[0.213.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.213.3...0.213.4
[0.213.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.213.2...0.213.3
[0.213.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.213.1...0.213.2
[0.213.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.213.0...0.213.1
[0.213.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.212.0...0.213.0
[0.212.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.211.1...0.212.0
[0.211.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.211.0...0.211.1
[0.211.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.210.1...0.211.0
[0.210.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.210.0...0.210.1
[0.210.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.209.3...0.210.0
[0.209.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.209.2...0.209.3
[0.209.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.209.1...0.209.2
[0.209.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.209.0...0.209.1
[0.209.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.208.0...0.209.0
[0.208.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.207.3...0.208.0
[0.207.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.207.2...0.207.3
[0.207.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.207.1...0.207.2
[0.207.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.207.0...0.207.1
[0.207.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.206.0...0.207.0
[0.206.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.205.3...0.206.0
[0.205.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.205.2...0.205.3
[0.205.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.205.1...0.205.2
[0.205.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.205.0...0.205.1
[0.205.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.204.0...0.205.0
[0.204.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.203.10...0.204.0
[0.203.10]: https://github.com/PolicyEngine/policyengine-us/compare/0.203.9...0.203.10
[0.203.9]: https://github.com/PolicyEngine/policyengine-us/compare/0.203.8...0.203.9
[0.203.8]: https://github.com/PolicyEngine/policyengine-us/compare/0.203.7...0.203.8
[0.203.7]: https://github.com/PolicyEngine/policyengine-us/compare/0.203.6...0.203.7
[0.203.6]: https://github.com/PolicyEngine/policyengine-us/compare/0.203.5...0.203.6
[0.203.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.203.4...0.203.5
[0.203.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.203.3...0.203.4
[0.203.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.203.2...0.203.3
[0.203.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.203.1...0.203.2
[0.203.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.203.0...0.203.1
[0.203.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.202.1...0.203.0
[0.202.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.202.0...0.202.1
[0.202.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.201.0...0.202.0
[0.201.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.200.7...0.201.0
[0.200.7]: https://github.com/PolicyEngine/policyengine-us/compare/0.200.6...0.200.7
[0.200.6]: https://github.com/PolicyEngine/policyengine-us/compare/0.200.5...0.200.6
[0.200.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.200.4...0.200.5
[0.200.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.200.3...0.200.4
[0.200.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.200.2...0.200.3
[0.200.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.200.1...0.200.2
[0.200.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.200.0...0.200.1
[0.200.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.199.6...0.200.0
[0.199.6]: https://github.com/PolicyEngine/policyengine-us/compare/0.199.5...0.199.6
[0.199.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.199.4...0.199.5
[0.199.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.199.3...0.199.4
[0.199.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.199.2...0.199.3
[0.199.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.199.1...0.199.2
[0.199.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.199.0...0.199.1
[0.199.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.198.0...0.199.0
[0.198.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.197.7...0.198.0
[0.197.7]: https://github.com/PolicyEngine/policyengine-us/compare/0.197.6...0.197.7
[0.197.6]: https://github.com/PolicyEngine/policyengine-us/compare/0.197.5...0.197.6
[0.197.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.197.4...0.197.5
[0.197.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.197.3...0.197.4
[0.197.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.197.2...0.197.3
[0.197.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.197.1...0.197.2
[0.197.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.197.0...0.197.1
[0.197.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.196.1...0.197.0
[0.196.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.196.0...0.196.1
[0.196.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.195.1...0.196.0
[0.195.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.195.0...0.195.1
[0.195.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.194.5...0.195.0
[0.194.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.194.4...0.194.5
[0.194.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.194.3...0.194.4
[0.194.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.194.2...0.194.3
[0.194.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.194.1...0.194.2
[0.194.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.194.0...0.194.1
[0.194.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.193.1...0.194.0
[0.193.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.193.0...0.193.1
[0.193.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.192.0...0.193.0
[0.192.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.191.0...0.192.0
[0.191.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.190.3...0.191.0
[0.190.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.190.2...0.190.3
[0.190.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.190.1...0.190.2
[0.190.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.190.0...0.190.1
[0.190.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.189.0...0.190.0
[0.189.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.188.7...0.189.0
[0.188.7]: https://github.com/PolicyEngine/policyengine-us/compare/0.188.6...0.188.7
[0.188.6]: https://github.com/PolicyEngine/policyengine-us/compare/0.188.5...0.188.6
[0.188.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.188.4...0.188.5
[0.188.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.188.3...0.188.4
[0.188.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.188.2...0.188.3
[0.188.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.188.1...0.188.2
[0.188.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.188.0...0.188.1
[0.188.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.187.0...0.188.0
[0.187.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.186.2...0.187.0
[0.186.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.186.1...0.186.2
[0.186.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.186.0...0.186.1
[0.186.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.185.2...0.186.0
[0.185.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.185.1...0.185.2
[0.185.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.185.0...0.185.1
[0.185.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.184.2...0.185.0
[0.184.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.184.1...0.184.2
[0.184.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.184.0...0.184.1
[0.184.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.183.2...0.184.0
[0.183.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.183.1...0.183.2
[0.183.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.183.0...0.183.1
[0.183.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.182.0...0.183.0
[0.182.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.181.7...0.182.0
[0.181.7]: https://github.com/PolicyEngine/policyengine-us/compare/0.181.6...0.181.7
[0.181.6]: https://github.com/PolicyEngine/policyengine-us/compare/0.181.5...0.181.6
[0.181.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.181.4...0.181.5
[0.181.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.181.3...0.181.4
[0.181.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.181.2...0.181.3
[0.181.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.181.1...0.181.2
[0.181.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.181.0...0.181.1
[0.181.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.180.1...0.181.0
[0.180.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.180.0...0.180.1
[0.180.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.179.0...0.180.0
[0.179.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.178.9...0.179.0
[0.178.9]: https://github.com/PolicyEngine/policyengine-us/compare/0.178.8...0.178.9
[0.178.8]: https://github.com/PolicyEngine/policyengine-us/compare/0.178.7...0.178.8
[0.178.7]: https://github.com/PolicyEngine/policyengine-us/compare/0.178.6...0.178.7
[0.178.6]: https://github.com/PolicyEngine/policyengine-us/compare/0.178.5...0.178.6
[0.178.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.178.4...0.178.5
[0.178.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.178.3...0.178.4
[0.178.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.178.2...0.178.3
[0.178.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.178.1...0.178.2
[0.178.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.178.0...0.178.1
[0.178.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.177.3...0.178.0
[0.177.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.177.2...0.177.3
[0.177.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.177.1...0.177.2
[0.177.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.177.0...0.177.1
[0.177.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.176.0...0.177.0
[0.176.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.175.0...0.176.0
[0.175.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.174.2...0.175.0
[0.174.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.174.1...0.174.2
[0.174.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.174.0...0.174.1
[0.174.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.173.3...0.174.0
[0.173.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.173.2...0.173.3
[0.173.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.173.1...0.173.2
[0.173.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.173.0...0.173.1
[0.173.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.172.0...0.173.0
[0.172.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.171.0...0.172.0
[0.171.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.170.0...0.171.0
[0.170.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.169.0...0.170.0
[0.169.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.168.0...0.169.0
[0.168.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.167.0...0.168.0
[0.167.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.166.0...0.167.0
[0.166.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.165.0...0.166.0
[0.165.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.164.0...0.165.0
[0.164.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.163.1...0.164.0
[0.163.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.163.0...0.163.1
[0.163.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.162.0...0.163.0
[0.162.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.161.0...0.162.0
[0.161.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.160.0...0.161.0
[0.160.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.159.1...0.160.0
[0.159.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.159.0...0.159.1
[0.159.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.158.0...0.159.0
[0.158.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.157.0...0.158.0
[0.157.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.156.0...0.157.0
[0.156.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.155.2...0.156.0
[0.155.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.155.1...0.155.2
[0.155.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.155.0...0.155.1
[0.155.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.154.0...0.155.0
[0.154.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.153.0...0.154.0
[0.153.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.152.0...0.153.0
[0.152.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.151.0...0.152.0
[0.151.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.150.0...0.151.0
[0.150.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.149.0...0.150.0
[0.149.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.148.0...0.149.0
[0.148.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.147.3...0.148.0
[0.147.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.147.2...0.147.3
[0.147.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.147.1...0.147.2
[0.147.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.147.0...0.147.1
[0.147.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.146.0...0.147.0
[0.146.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.145.0...0.146.0
[0.145.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.144.1...0.145.0
[0.144.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.144.0...0.144.1
[0.144.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.143.0...0.144.0
[0.143.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.142.0...0.143.0
[0.142.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.141.0...0.142.0
[0.141.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.140.0...0.141.0
[0.140.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.139.0...0.140.0
[0.139.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.138.0...0.139.0
[0.138.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.137.0...0.138.0
[0.137.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.136.0...0.137.0
[0.136.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.135.1...0.136.0
[0.135.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.135.0...0.135.1
[0.135.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.134.0...0.135.0
[0.134.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.133.0...0.134.0
[0.133.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.132.0...0.133.0
[0.132.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.131.0...0.132.0
[0.131.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.130.0...0.131.0
[0.130.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.129.2...0.130.0
[0.129.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.129.1...0.129.2
[0.129.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.129.0...0.129.1
[0.129.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.128.3...0.129.0
[0.128.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.128.2...0.128.3
[0.128.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.128.1...0.128.2
[0.128.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.128.0...0.128.1
[0.128.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.127.0...0.128.0
[0.127.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.126.0...0.127.0
[0.126.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.125.0...0.126.0
[0.125.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.124.1...0.125.0
[0.124.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.124.0...0.124.1
[0.124.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.123.0...0.124.0
[0.123.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.122.0...0.123.0
[0.122.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.121.2...0.122.0
[0.121.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.121.1...0.121.2
[0.121.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.121.0...0.121.1
[0.121.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.120.0...0.121.0
[0.120.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.119.1...0.120.0
[0.119.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.119.0...0.119.1
[0.119.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.118.0...0.119.0
[0.118.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.117.0...0.118.0
[0.117.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.116.0...0.117.0
[0.116.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.115.0...0.116.0
[0.115.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.114.1...0.115.0
[0.114.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.114.0...0.114.1
[0.114.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.113.0...0.114.0
[0.113.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.112.1...0.113.0
[0.112.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.112.0...0.112.1
[0.112.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.111.0...0.112.0
[0.111.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.110.2...0.111.0
[0.110.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.110.1...0.110.2
[0.110.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.110.0...0.110.1
[0.110.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.109.1...0.110.0
[0.109.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.109.0...0.109.1
[0.109.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.108.0...0.109.0
[0.108.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.107.0...0.108.0
[0.107.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.106.0...0.107.0
[0.106.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.105.0...0.106.0
[0.105.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.104.0...0.105.0
[0.104.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.103.1...0.104.0
[0.103.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.103.0...0.103.1
[0.103.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.102.0...0.103.0
[0.102.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.101.0...0.102.0
[0.101.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.100.2...0.101.0
[0.100.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.100.1...0.100.2
[0.100.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.100.0...0.100.1
[0.100.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.99.1...0.100.0
[0.99.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.99.0...0.99.1
[0.99.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.98.1...0.99.0
[0.98.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.98.0...0.98.1
[0.98.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.97.0...0.98.0
[0.97.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.96.0...0.97.0
[0.96.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.95.0...0.96.0
[0.95.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.94.0...0.95.0
[0.94.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.93.0...0.94.0
[0.93.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.92.0...0.93.0
[0.92.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.91.4...0.92.0
[0.91.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.91.3...0.91.4
[0.91.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.91.2...0.91.3
[0.91.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.91.1...0.91.2
[0.91.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.91.0...0.91.1
[0.91.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.90.0...0.91.0
[0.90.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.89.1...0.90.0
[0.89.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.89.0...0.89.1
[0.89.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.88.2...0.89.0
[0.88.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.88.1...0.88.2
[0.88.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.88.0...0.88.1
[0.88.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.87.0...0.88.0
[0.87.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.86.1...0.87.0
[0.86.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.86.0...0.86.1
[0.86.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.85.3...0.86.0
[0.85.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.85.2...0.85.3
[0.85.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.85.1...0.85.2
[0.85.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.85.0...0.85.1
[0.85.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.84.5...0.85.0
[0.84.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.84.4...0.84.5
[0.84.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.84.3...0.84.4
[0.84.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.84.2...0.84.3
[0.84.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.84.1...0.84.2
[0.84.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.84.0...0.84.1
[0.84.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.83.4...0.84.0
[0.83.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.83.3...0.83.4
[0.83.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.83.2...0.83.3
[0.83.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.83.1...0.83.2
[0.83.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.83.0...0.83.1
[0.83.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.82.0...0.83.0
[0.82.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.81.5...0.82.0
[0.81.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.81.4...0.81.5
[0.81.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.81.3...0.81.4
[0.81.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.81.2...0.81.3
[0.81.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.81.1...0.81.2
[0.81.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.81.0...0.81.1
[0.81.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.80.0...0.81.0
[0.80.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.79.0...0.80.0
[0.79.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.78.0...0.79.0
[0.78.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.77.0...0.78.0
[0.77.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.76.1...0.77.0
[0.76.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.76.0...0.76.1
[0.76.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.75.2...0.76.0
[0.75.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.75.1...0.75.2
[0.75.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.75.0...0.75.1
[0.75.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.74.2...0.75.0
[0.74.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.74.1...0.74.2
[0.74.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.74.0...0.74.1
[0.74.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.73.2...0.74.0
[0.73.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.73.1...0.73.2
[0.73.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.73.0...0.73.1
[0.73.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.72.3...0.73.0
[0.72.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.72.2...0.72.3
[0.72.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.72.1...0.72.2
[0.72.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.72.0...0.72.1
[0.72.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.71.2...0.72.0
[0.71.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.71.1...0.71.2
[0.71.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.71.0...0.71.1
[0.71.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.70.3...0.71.0
[0.70.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.70.2...0.70.3
[0.70.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.70.1...0.70.2
[0.70.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.70.0...0.70.1
[0.70.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.69.3...0.70.0
[0.69.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.69.2...0.69.3
[0.69.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.69.1...0.69.2
[0.69.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.69.0...0.69.1
[0.69.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.68.1...0.69.0
[0.68.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.68.0...0.68.1
[0.68.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.67.0...0.68.0
[0.67.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.66.1...0.67.0
[0.66.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.66.0...0.66.1
[0.66.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.65.0...0.66.0
[0.65.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.64.1...0.65.0
[0.64.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.64.0...0.64.1
[0.64.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.63.0...0.64.0
[0.63.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.62.3...0.63.0
[0.62.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.62.2...0.62.3
[0.62.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.62.1...0.62.2
[0.62.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.62.0...0.62.1
[0.62.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.61.0...0.62.0
[0.61.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.60.0...0.61.0
[0.60.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.59.0...0.60.0
[0.59.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.58.1...0.59.0
[0.58.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.58.0...0.58.1
[0.58.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.57.1...0.58.0
[0.57.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.57.0...0.57.1
[0.57.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.56.0...0.57.0
[0.56.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.55.0...0.56.0
[0.55.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.54.1...0.55.0
[0.54.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.54.0...0.54.1
[0.54.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.53.0...0.54.0
[0.53.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.52.0...0.53.0
[0.52.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.51.1...0.52.0
[0.51.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.51.0...0.51.1
[0.51.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.50.0...0.51.0
[0.50.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.49.1...0.50.0
[0.49.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.49.0...0.49.1
[0.49.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.48.0...0.49.0
[0.48.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.47.0...0.48.0
[0.47.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.46.1...0.47.0
[0.46.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.46.0...0.46.1
[0.46.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.45.2...0.46.0
[0.45.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.45.1...0.45.2
[0.45.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.45.0...0.45.1
[0.45.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.44.0...0.45.0
[0.44.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.43.1...0.44.0
[0.43.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.43.0...0.43.1
[0.43.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.42.1...0.43.0
[0.42.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.42.0...0.42.1
[0.42.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.41.2...0.42.0
[0.41.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.41.1...0.41.2
[0.41.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.41.0...0.41.1
[0.41.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.40.0...0.41.0
[0.40.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.39.0...0.40.0
[0.39.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.38.2...0.39.0
[0.38.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.38.1...0.38.2
[0.38.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.38.0...0.38.1
[0.38.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.37.9...0.38.0
[0.37.9]: https://github.com/PolicyEngine/policyengine-us/compare/0.37.8...0.37.9
[0.37.8]: https://github.com/PolicyEngine/policyengine-us/compare/0.37.7...0.37.8
[0.37.7]: https://github.com/PolicyEngine/policyengine-us/compare/0.37.6...0.37.7
[0.37.6]: https://github.com/PolicyEngine/policyengine-us/compare/0.37.5...0.37.6
[0.37.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.37.4...0.37.5
[0.37.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.37.3...0.37.4
[0.37.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.37.2...0.37.3
[0.37.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.37.1...0.37.2
[0.37.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.37.0...0.37.1
[0.37.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.36.1...0.37.0
[0.36.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.36.0...0.36.1
[0.36.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.35.3...0.36.0
[0.35.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.35.2...0.35.3
[0.35.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.35.1...0.35.2
[0.35.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.35.0...0.35.1
[0.35.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.34.0...0.35.0
[0.34.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.33.0...0.34.0
[0.33.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.32.6...0.33.0
[0.32.6]: https://github.com/PolicyEngine/policyengine-us/compare/0.32.5...0.32.6
[0.32.5]: https://github.com/PolicyEngine/policyengine-us/compare/0.32.4...0.32.5
[0.32.4]: https://github.com/PolicyEngine/policyengine-us/compare/0.32.3...0.32.4
[0.32.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.32.2...0.32.3
[0.32.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.32.1...0.32.2
[0.32.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.32.0...0.32.1
[0.32.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.31.0...0.32.0
[0.31.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.30.3...0.31.0
[0.30.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.30.2...0.30.3
[0.30.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.30.1...0.30.2
[0.30.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.30.0...0.30.1
[0.30.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.29.0...0.30.0
[0.29.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.28.0...0.29.0
[0.28.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.27.2...0.28.0
[0.27.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.27.1...0.27.2
[0.27.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.27.0...0.27.1
[0.27.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.26.0...0.27.0
[0.26.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.25.0...0.26.0
[0.25.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.24.1...0.25.0
[0.24.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.24.0...0.24.1
[0.24.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.23.1...0.24.0
[0.23.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.23.0...0.23.1
[0.23.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.22.0...0.23.0
[0.22.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.21.0...0.22.0
[0.21.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.20.2...0.21.0
[0.20.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.20.1...0.20.2
[0.20.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.20.0...0.20.1
[0.20.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.19.3...0.20.0
[0.19.3]: https://github.com/PolicyEngine/policyengine-us/compare/0.19.2...0.19.3
[0.19.2]: https://github.com/PolicyEngine/policyengine-us/compare/0.19.1...0.19.2
[0.19.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.19.0...0.19.1
[0.19.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.18.0...0.19.0
[0.18.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.17.1...0.18.0
[0.17.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.17.0...0.17.1
[0.17.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.16.0...0.17.0
[0.16.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.15.0...0.16.0
[0.15.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.14.0...0.15.0
[0.14.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.13.0...0.14.0
[0.13.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.12.0...0.13.0
[0.12.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.11.0...0.12.0
[0.11.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.10.0...0.11.0
[0.10.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.9.0...0.10.0
[0.9.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.8.0...0.9.0
[0.8.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.7.0...0.8.0
[0.7.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.6.0...0.7.0
[0.6.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.5.0...0.6.0
[0.5.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.4.0...0.5.0
[0.4.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.3.1...0.4.0
[0.3.1]: https://github.com/PolicyEngine/policyengine-us/compare/0.3.0...0.3.1
[0.3.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/PolicyEngine/policyengine-us/compare/0.0.1...0.1.0

