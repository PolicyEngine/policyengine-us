# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

- Versioning action didn't update `setup.py`.

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

