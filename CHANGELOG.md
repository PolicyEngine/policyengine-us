# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0).

## [0.37.5] - 2022-03-11

### Changed

* Simplified WIC uprating.

### Added

* February 2022 chained CPI-U.

## [0.37.4] - 2022-03-09

### Changed

* IRS-published uprated income tax parameters for 2019-22.

## [0.37.3] - 2022-03-08

### Changed

* `is_married` moved from person-level to family-level, with a formula added.

## [0.37.2] - 2022-03-07

### Added

* `spm_unit_weight` variable.

### Fixed

* SNAP now uses the additional amounts where main rates are not available.

## [0.37.1] - 2022-03-07

### Changed

* Point `e02400` to `social_security` (for PolicyEngine).

## [0.37.0] - 2022-03-05

### Added

* SNAP aggregate benefits and participation.

## [0.36.1] - 2022-03-04

### Changed

* Adjust variable labels for consistency.

## [0.36.0] - 2022-03-04

### Added

* Supplemental Security Income for individuals.
* Social Security input variables, counted as unearned income for several programs.

## [0.35.3] - 2022-02-28

### Added

* Code coverage badge to README.md.
* Reminder for pull requests to run `make format && make documentation`.
* CPI-uprated values for WIC average payments.

### Changed

* Child Tax Credit names renamed to `ctc`.
* Child and Dependent Care Credit names renamed to `cdcc`.

### Fixed

* EITC maximum age in 2021 changed from 125 to infinity.

## [0.35.2] - 2022-02-27

### Fixed

* Subtract Lifeline from broadband cost before calculating ACP and EBB.

## [0.35.1] - 2022-02-21

### Changed

* Edited labels for ACP and SNAP normal allotment.

## [0.35.0] - 2022-02-21

### Added

* Rural Tribal supplement for Lifeline.

### Changed

* Restructure ACP and EBB Tribal amounts to work with PolicyEngine.

## [0.34.0] - 2022-02-21

### Added

* Affordable Connectivity Program.

### Changed

* Split school meal subsidies into free and reduced-price.

## [0.33.0] - 2022-02-21

### Added

* Uprated tax parameters for federal income tax.

## [0.32.6] - 2022-02-16

### Changed

* OpenFisca-Tools constraint widened to the current major version.

## [0.32.5] - 2022-02-13

### Added

* Chained CPI-U (monthly and August-only) parameters.
* Metadata for SNAP max allotment.

## [0.32.4] - 2022-02-10

### Added

* Categorical breakdown metadata infrastructure from OpenFisca-Tools.

## [0.32.3] - 2022-02-09

### Fixed

* Remove guaranteed income / cash assistance from benefits.

## [0.32.2] - 2022-02-09

### Fixed

* Specify WIC's unit as USD.

## [0.32.1] - 2022-02-09

### Fixed

* Change WIC display name from `WIC benefit value` to `WIC`.

## [0.32.0] - 2022-02-09

### Added

* WIC program.

### Fixed

* Include guaranteed income / cash assistance in market income.

## [0.31.0] - 2022-02-09

### Added

* Income limits for 5 Maryland Medicaid coverage groups.

## [0.30.3] - 2022-02-08

### Fixed

* Add Lifeline notebook to table of contents.

## [0.30.2] - 2022-02-08

### Added

* PolicyEngine metadata and notebook for Lifeline program.
* Formula for `irs_gross_income`, which Lifeline uses to calculate income-based eligibility.

## [0.30.1] - 2022-02-08

### Fixed

* EITC logic and parameters for non-3-child tax units.

## [0.30.0] - 2022-02-07

### Added

* Guaranteed income / cash assistance pilot income variable. This counts as unearned income for SNAP, uncounted for taxes and other benefits.

## [0.29.0] - 2022-02-07

### Added

* California Clean Vehicle Rebate Project.

## [0.28.0] - 2022-02-06

### Added

* SNAP emergency allotments for California.
* SNAP unearned income example in JupyterBook docs.

## [0.27.2] - 2022-02-06

### Added

* Added formula for TANF variable `continuous_tanf_eligibility`
* Added integration test for continuous TANF eligibility to `integration.yaml`

## [0.27.1] - 2022-02-02

### Added

* Metadata and variable aliases for key tax variables.
* Employment, self-employment, interest and dividend income as inputs to tax logic.

## [0.27.0] - 2022-01-28

### Added

* Child Tax Credit (and historical policy).
* Non-refundable and refundable credit handling in tax logic.
* Metadata for education credits and the EITC.

### Fixed

* Bugs in head/spouse detection and nonrefundable credits.

## [0.26.0] - 2022-01-25

### Added

* Categorical eligibility to school meal subsidies.
* Documentation notebook on school meal subsidies.
* Parameterized income sources for school meal subsidies.

### Changed

* Count school meal subsidies by school enrollment rather than age.
* Remove `spm_unit_` prefix from school meal variables.

## [0.25.0] - 2022-01-17

### Added

* Child Tax Credit (including adult dependents) parameters, logic and tests.

## [0.24.1] - 2022-01-17

### Changed

* Add metadata for variables and parameters used in SNAP calculations.
* Renames two parameters involved in SNAP deductions from `threshold` to `disregard`.

## [0.24.0] - 2022-01-17

### Added

* Logic for SNAP excess medical deduction and dependent care deduction.
* Limit SNAP earned income deduction to earned income.
* Jupyter Book documentation on SNAP.
* Updated SNAP parameters.
* Empty variables for calculating SNAP: `employment_income`, `self_employment_income`, `dividend_income`, `interest_income`, `childcare_expenses`, and `medical_out_of_pocket_expenses`.

### Changed

* Significant refactoring of SNAP code.
* Use openfisca-tools for `add` and `aggr` functions, and pass lists of variables to these function.
* Rename min/max SNAP benefit parameters and variables to use `allotment`.

## [0.23.1] - 2022-01-15

### Fixed

* Added links to version tag diffs in changelog.

## [0.23.0] - 2022-01-15

### Fixed

* Update CCDF subsidy formula.

## [0.22.0] - 2022-01-14

### Added

* Formula for SSI based on eligibility and amount if eligible.

## [0.21.0] - 2022-01-14

### Added

* Add CCDF copay formula.

## [0.20.2] - 2022-01-14

### Fixed

* Parameter misname in SNAP formula.

### Added

* Metadata for SNAP eligibility parameters.

## [0.20.1] - 2022-01-12

### Fixed

* Test runner failed to test string values.

## [0.20.0] - 2022-01-09

### Added

* Formula for initial TANF eligibility.
* Two new variables: `tanf_gross_earned_income` and `tanf_gross_unearned_income`.
* Variable & parameter for `initial_employment_deduction`.
* Integration tests for TANF cash aid from TANF IL website.

### Changed

* `tanf_countable_income` now includes unearned income and earned income deduction.

## [0.19.3] - 2022-01-08

### Changed

* Adds one line between tests in yaml files.
* Use consistent imports in variable Python files.

### Added

* Units to all tax variables.

### Removed

* C-TAM benefit variables in tax Python files.
* Erroneous formula for `eic` variable.

## [0.19.2] - 2022-01-08

### Changed

* Removes the `u` prefix from all variable label strings.

## [0.19.1] - 2022-01-07

### Added

* Formulas for `childcare_hours_per_week` and `spm_unit_size`.
* Unit tests and units for some variables.

### Changed

* Reorganized variables.

## [0.19.0] - 2022-01-06

### Added

* Update child care market rate to annual.

## [0.18.0] - 2022-01-05

### Added

* Total child care market rate.

## [0.17.1] - 2022-01-06

### Changed

* Use USDA elderly and disabled definitions in SNAP calculations.

## [0.17.0] - 2022-01-04

### Added

* Categorical eligibility for SNAP, including broad-based categorical eligibility via low-cost TANF programs that effectively extend SNAP's asset and income limits.

### Changed

* Refactored SNAP code.

## [0.16.0] - 2022-01-03

### Added

* CCDF subsidy top-level logic

## [0.15.0] - 2022-01-03

### Added

* Federal SNAP asset tests logic

## [0.14.0] - 2022-01-03

### Added

* SNAP eligibility based on federal net and gross income limits.
* Unit and integration tests for SNAP variables.

## [0.13.0] - 2021-12-31

### Added

* Formula for Medicaid person type, based on age and dependents.
* Variable for whether a person meets their Medicaid income eligibility requirement.

## [0.12.0] - 2021-12-30

### Added

* Elderly and Disabled (tax) Credit.

## [0.11.0] - 2021-12-30

### Added

* American Opportunity (tax) Credit.
* Lifetime Learning (tax) Credit.

## [0.10.0] - 2021-12-28

### Added

* Income-to-SMI (state median income) ratio.

## [0.9.0] - 2021-12-28

### Added

* Social Security taxation logic.

## [0.8.0] - 2021-12-28

### Added

* Minimum benefit logic for SNAP.

## [0.7.0] - 2021-12-28

### Added

* Gains Tax (capital gains treatment) logic and parameters.

## [0.6.0] - 2021-12-28

### Added

* Alternative Minimum Tax (AMT) income and liability logic.
* Development tools for auto-generating unit tests for Tax-Calculator functions.

## [0.5.0] -

### Added

* Medicaid income thresholds for California.

## [0.4.0] - 2021-12-26

### Added

* TANF eligibility, broken down into demographic and financial variables, with financial separated by current enrollment in program.
* Demographic TANF eligibility per IL rules.

## [0.3.1] - 2021-12-25

### Added

* Automated tests.

## [0.3.0] - 2021-12-25

### Added

* Lifeline benefit.

## 0.0.1 - 2021-06-28

### Added

* First prototype version with a standard deduction variable.

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
[0.16.0]: https://github.com/PolicyEngine/openfisca-us/compare/0.15.2...0.16.0
[0.15.2]: https://github.com/PolicyEngine/openfisca-us/compare/0.15.1...0.15.2
[0.15.1]: https://github.com/PolicyEngine/openfisca-us/compare/0.15.0...0.15.1
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
[0.3.0]: https://github.com/PolicyEngine/openfisca-us/releases/tag/0.3.0
