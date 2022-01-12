# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), 
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
