# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

