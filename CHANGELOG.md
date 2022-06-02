# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

- Microdata now handled entirely within OpenFisca-US.

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



[0.70.2]: https://github.com/PolicyEngine/openfisca-us/compare/0.70.1...0.70.2
[0.70.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.70.0...0.70.1
[0.70.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.69.3...0.70.0
[0.69.3]: https://github.com/PolicyEngine/openfisca-us/compare/0.69.2...0.69.3
[0.69.2]: https://github.com/PolicyEngine/openfisca-us/compare/0.69.1...0.69.2
[0.69.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.69.0...0.69.1
[0.69.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.68.1...0.69.0
[0.68.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.68.0...0.68.1
[0.68.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.67.0...0.68.0
[0.67.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.66.1...0.67.0
[0.66.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.66.0...0.66.1
[0.66.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.65.0...0.66.0
[0.65.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.64.1...0.65.0
[0.64.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.64.0...0.64.1
[0.64.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.63.0...0.64.0
[0.63.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.62.3...0.63.0
[0.62.3]: https://github.com/PolicyEngine/openfisca-us/compare/0.62.2...0.62.3
[0.62.2]: https://github.com/PolicyEngine/openfisca-us/compare/0.62.1...0.62.2
[0.62.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.62.0...0.62.1
[0.62.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.61.0...0.62.0
[0.61.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.60.0...0.61.0
[0.60.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.59.0...0.60.0
[0.59.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.58.1...0.59.0
[0.58.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.58.0...0.58.1
[0.58.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.57.1...0.58.0
[0.57.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.57.0...0.57.1
[0.57.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.56.0...0.57.0
[0.56.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.55.0...0.56.0
[0.55.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.54.1...0.55.0
[0.54.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.54.0...0.54.1
[0.54.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.53.0...0.54.0
[0.53.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.52.0...0.53.0
[0.52.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.51.1...0.52.0
[0.51.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.51.0...0.51.1
[0.51.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.50.0...0.51.0
[0.50.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.49.1...0.50.0
[0.49.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.49.0...0.49.1
[0.49.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.48.0...0.49.0
[0.48.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.47.0...0.48.0
[0.47.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.46.1...0.47.0
[0.46.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.46.0...0.46.1
[0.46.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.45.2...0.46.0
[0.45.2]: https://github.com/PolicyEngine/openfisca-us/compare/0.45.1...0.45.2
[0.45.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.45.0...0.45.1
[0.45.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.44.0...0.45.0
[0.44.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.43.1...0.44.0
[0.43.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.43.0...0.43.1
[0.43.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.42.1...0.43.0
[0.42.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.42.0...0.42.1
[0.42.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.41.2...0.42.0
[0.41.2]: https://github.com/PolicyEngine/openfisca-us/compare/0.41.1...0.41.2
[0.41.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.41.0...0.41.1
[0.41.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.40.0...0.41.0
[0.40.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.39.0...0.40.0
[0.39.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.38.2...0.39.0
[0.38.2]: https://github.com/PolicyEngine/openfisca-us/compare/0.38.1...0.38.2
[0.38.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.38.0...0.38.1
[0.38.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.37.9...0.38.0
[0.37.9]: https://github.com/PolicyEngine/openfisca-us/compare/0.37.8...0.37.9
[0.37.8]: https://github.com/PolicyEngine/openfisca-us/compare/0.37.7...0.37.8
[0.37.7]: https://github.com/PolicyEngine/openfisca-us/compare/0.37.6...0.37.7
[0.37.6]: https://github.com/PolicyEngine/openfisca-us/compare/0.37.5...0.37.6
[0.37.5]: https://github.com/PolicyEngine/openfisca-us/compare/0.37.4...0.37.5
[0.37.4]: https://github.com/PolicyEngine/openfisca-us/compare/0.37.3...0.37.4
[0.37.3]: https://github.com/PolicyEngine/openfisca-us/compare/0.37.2...0.37.3
[0.37.2]: https://github.com/PolicyEngine/openfisca-us/compare/0.37.1...0.37.2
[0.37.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.37.0...0.37.1
[0.37.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.36.1...0.37.0
[0.36.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.36.0...0.36.1
[0.36.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.35.3...0.36.0
[0.35.3]: https://github.com/PolicyEngine/openfisca-us/compare/0.35.2...0.35.3
[0.35.2]: https://github.com/PolicyEngine/openfisca-us/compare/0.35.1...0.35.2
[0.35.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.35.0...0.35.1
[0.35.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.34.0...0.35.0
[0.34.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.33.0...0.34.0
[0.33.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.32.6...0.33.0
[0.32.6]: https://github.com/PolicyEngine/openfisca-us/compare/0.32.5...0.32.6
[0.32.5]: https://github.com/PolicyEngine/openfisca-us/compare/0.32.4...0.32.5
[0.32.4]: https://github.com/PolicyEngine/openfisca-us/compare/0.32.3...0.32.4
[0.32.3]: https://github.com/PolicyEngine/openfisca-us/compare/0.32.2...0.32.3
[0.32.2]: https://github.com/PolicyEngine/openfisca-us/compare/0.32.1...0.32.2
[0.32.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.32.0...0.32.1
[0.32.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.31.0...0.32.0
[0.31.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.30.3...0.31.0
[0.30.3]: https://github.com/PolicyEngine/openfisca-us/compare/0.30.2...0.30.3
[0.30.2]: https://github.com/PolicyEngine/openfisca-us/compare/0.30.1...0.30.2
[0.30.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.30.0...0.30.1
[0.30.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.29.0...0.30.0
[0.29.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.28.0...0.29.0
[0.28.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.27.2...0.28.0
[0.27.2]: https://github.com/PolicyEngine/openfisca-us/compare/0.27.1...0.27.2
[0.27.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.27.0...0.27.1
[0.27.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.26.0...0.27.0
[0.26.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.25.0...0.26.0
[0.25.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.24.1...0.25.0
[0.24.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.24.0...0.24.1
[0.24.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.23.1...0.24.0
[0.23.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.23.0...0.23.1
[0.23.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.22.0...0.23.0
[0.22.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.21.0...0.22.0
[0.21.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.20.2...0.21.0
[0.20.2]: https://github.com/PolicyEngine/openfisca-us/compare/0.20.1...0.20.2
[0.20.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.20.0...0.20.1
[0.20.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.19.3...0.20.0
[0.19.3]: https://github.com/PolicyEngine/openfisca-us/compare/0.19.2...0.19.3
[0.19.2]: https://github.com/PolicyEngine/openfisca-us/compare/0.19.1...0.19.2
[0.19.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.19.0...0.19.1
[0.19.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.18.0...0.19.0
[0.18.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.17.1...0.18.0
[0.17.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.17.0...0.17.1
[0.17.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.16.0...0.17.0
[0.16.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.15.0...0.16.0
[0.15.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.14.0...0.15.0
[0.14.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.13.0...0.14.0
[0.13.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.12.0...0.13.0
[0.12.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.11.0...0.12.0
[0.11.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.10.0...0.11.0
[0.10.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.9.0...0.10.0
[0.9.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.8.0...0.9.0
[0.8.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.7.0...0.8.0
[0.7.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.6.0...0.7.0
[0.6.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.5.0...0.6.0
[0.5.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.4.0...0.5.0
[0.4.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.3.1...0.4.0
[0.3.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.3.0...0.3.1
[0.3.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.0.1...0.1.0

