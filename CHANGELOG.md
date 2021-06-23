# Changelog

### 3.12.8 - [#105](https://github.com/openfisca/country-template/pull/105)

* Minor change.
* Details:
  - Upgrade `flake8-print`

### 3.12.7 - [#104](https://github.com/openfisca/country-template/pull/104)

* Minor change.
* Details:
  - Upgrade `flake8-bugbear`

### 3.12.6 - [#102](https://github.com/openfisca/country-template/pull/102)

* Bug fix.
* Impacted periods: all.
* Impacted areas: `openfisca_country_template/variables/benefits.py`.
* Details:
  - Fixes `parenting_allowance` formula syntax.
  - Uses vectorial computing to return a `parenting_allowance` amount per household.

### 3.12.5 - [#107](https://github.com/openfisca/country-template/pull/107)

* Technical improvement.
* Details:
  - Forces the installation of the new build each time `make build` is run.
  - CircleCI tests against the packaged version of this library.
    - When a branch is pushed first time, CircleCI creates a build and caches dependencies.
    - Subsequent pushes do not reinstall the build as it is already in cache.
    - If the code has been modified in between, changes will be ignored, and tests will fail.

### 3.12.4 - [#103](https://github.com/openfisca/country-template/pull/103)

* Minor change.
* Details:
  - Fix CHANGELOG versions:
    - `3.13.0` was supposed to be `3.12.3`.
    - `3.12.0` and `3.12.1` are unpublished.

### 3.12.3 - [#97](https://github.com/openfisca/country-template/pull/97)

* Technical improvement.
* Impacted areas: `**/*`.
* Details:
  - Make style checks stricter and clearer to help country package developers get started.

### 3.12.2 - [#99](https://github.com/openfisca/country-template/pull/99)

 * Technical improvement.
 * Impacted areas: tests/variables and parameters.
 * Details:
   - Add a new variable called parenting_allowance to show how group entities and single entities can be used together.
   - This variable calls the household_income variable.

### 3.12.1 -

> Note: Version `3.12.1` wasn't unpublished by mistake. Please use version `3.12.2` or more recent.

## 3.12.0 -

> Note: Version `3.12.0` wasn't unpublished by mistake. Please use version `3.12.2` or more recent.

## 3.11.0 - [#90](https://github.com/openfisca/country-template/pull/90)

* Technical change
* Details:
  - Declare package compatible with OpenFisca-Core v35 that updates `numpy` dependency.

## 3.10.0 - [#98](https://github.com/openfisca/country-template/pull/98)

* Tax and benefit system evolution.
* Impacted periods: all.
* Impacted areas: `reforms/add_new_tax.py`.
* Details:
  - Add a new reform example creating a variable (there was none prior).
  - The example is a new tax that adds a fixed 100.0 of the country's currency to the actual income tax.

### 3.9.13 - [#96](https://github.com/openfisca/country-template/pull/96)

* Technical improvement.
* Impacted areas: `**/*`.
* Details:
  - Remove wildcard imports as they're considered and [anti-pattern](https://docs.quantifiedcode.com/python-anti-patterns/maintainability/from_module_import_all_used.html).

### 3.9.12 - [#93](https://github.com/openfisca/country-template/pull/93)

* Minor change.
* Details:
  - Upgrade `autopep8`, `flake8` & `pycodestyle`.

### 3.9.11 - [#94](https://github.com/openfisca/country-template/pull/94)

* Minor change.
* Details:
  - Fix `make test` warning by updating OpenFisca test command.

### 3.9.10 - [#86](https://github.com/openfisca/country-template/pull/86)

* Technical change.
* Details:
  - Fix installation and building operations by fixing the bootstrap script.

### 3.9.9 - [#85](https://github.com/openfisca/country-template/pull/85)

* Minor change.
* Details:
  - Add `make serve-local` command to Makefile.

### 3.9.8 - [#83](https://github.com/openfisca/country-template/pull/83)

* Minor change.
* Details:
  - Add additional example JSON file; add to README.

### 3.9.7 - [#80](https://github.com/openfisca/country-template/pull/80)

* Minor change.
* Details:
  - Upgrade `autopep8`.

### 3.9.6 - [#78](https://github.com/openfisca/country-template/pull/78)

* Minor change.
* Details:
  - Declare package compatible with Core v34.

### 3.9.5 - [#76](https://github.com/openfisca/country-template/pull/76)

* Minor change.
* Details:
  - Declare package compatible with Core v32.

### 3.9.4 - [#75](https://github.com/openfisca/country-template/pull/75)

* Minor change.
* Details:
  - Upgrade `autopep8`.

### 3.9.3 - [#73](https://github.com/openfisca/country-template/pull/73)

* Minor change.
* Details:
  - Upgrade `autopep8`.

### 3.9.2 - [#71](https://github.com/openfisca/country-template/pull/71)

* Minor change.
* Details:
  - Upgrade `flake8` and `pycodestyle`.

### 3.9.1 - [#74](https://github.com/openfisca/country-template/pull/74)

* Minor change.
* Details:
  - Explicit expected test output.

## 3.9.0 - [#72](https://github.com/openfisca/country-template/pull/72)

* Technical change.
* Details:
  - Declare package compatible with Core v31.

## 3.8.0 - [#69](https://github.com/openfisca/country-template/pull/69)

* Technical change.
* Details:
  - Declare package compatible with Core v27.

## 3.7.0 - [#68](https://github.com/openfisca/country-template/pull/68)

* Technical change.
* Details:
  - Declare package compatible with Core v26.
  - Remove Python 2 checks from continuous integration.

## 3.6.O - [#66](https://github.com/openfisca/country-template/pull/66)

* Minor change.
* Details:
  - Adapt to OpenFisca Core v25.
  - Change the syntax of OpenFisca YAML tests.

For instance, a test that was using the `input_variables` and the `output_variables` keywords like:

```yaml
- name: Basic income
  period: 2016-12
  input_variables:
    salary: 1200
  output_variables:
    basic_income: 600
```

Becomes:

```yaml
- name: Basic income
  period: 2016-12
  input:
    salary: 1200
  output:
    basic_income: 600
```

A test that was fully specifying its entities like:

```yaml
name: Housing tax
  period: 2017-01
  households:
    - parents: [ Alicia ]
      children: [ Michael ]
  persons:
    - id: Alicia
        birth: 1961-01-15
    - id: Michael
        birth: 2002-01-15
  output_variables:
    housing_tax:
      2017: 1000
```

Becomes:

```yaml
name: Housing tax
  period: 2017-01
  input:
    household:
      parents: [ Alicia ]
      children: [ Michael ]
    persons:
      Alicia:
        birth: 1961-01-15
      Michael:
        birth: 2002-01-15
  output:
    housing_tax:
      2017: 1000
```

### 3.5.4 - [#65](https://github.com/openfisca/country-template/pull/65)

* Minor change.
* Details:
  - Update links to the doc.

### 3.5.3 - [#64](https://github.com/openfisca/country-template/pull/64)

* Minor change.
* Details:
  - Document housing tax.

### 3.5.2 - [#59](https://github.com/openfisca/country-template/pull/59) [#62](https://github.com/openfisca/country-template/pull/62) [#63](https://github.com/openfisca/country-template/pull/63)

* Technical change.
* Details:
  - Tests library against its packaged version.
  - By doing so, we prevent some hideous bugs.

> Note: Version `3.5.1` has been unpublished as it accidentally introduced a bug. Please use version `3.5.2` or more recent.

## 3.5.0 - [#58](https://github.com/openfisca/country-template/pull/58)

* Technical change.
  - In the `/spec` Web API route, use examples that apply to this country package.

## 3.4.0

* Tax and benefit system evolution.
* Impacted periods: all.
* Impacted areas: `housing`.
* Details:
  - Introduce `code_postal` variable.

### 3.3.2

* Minor change.
* Details:
  - Update entities labels.

### 3.3.1 - [#53](https://github.com/openfisca/country-template/pull/53)

* Minor change.
* Details:
  - Add `documentation` to parameters: `benefits` node and `benefits/housing_allowance`.
  - Add documentation to `housing_allowance` variable and formula.

## 3.3.0 - [#51](https://github.com/openfisca/country-template/pull/51)

* Technical change.
  - Make package compatible with OpenFisca Core v24.
  - Rename development dependencies from `test` to `dev`.

### 3.2.3 - [#50](https://github.com/openfisca/country-template/pull/50)

* Minor change.
* Details:
  - Fix repository URL in package metadata.

### 3.2.2 - [#49](https://github.com/openfisca/country-template/pull/49)

* Tax and benefit system evolution.
* Impacted periods: all.
* Impacted areas: `taxes`.
* Details:
  - Implement housing tax minimal amount.

<!-- -->

* Minor change.
* Details:
  - Add metadata to parameters.

### 3.2.1 - [#47](https://github.com/openfisca/country-template/pull/47)

* Minor change.
* Details:
  - Make boostrap script portable.

## 3.2.0 - [#43](https://github.com/openfisca/country-template/pull/43)

* Tax and benefit system evolution.
* Impacted periods: all.
* Impacted areas: `demographics`.
* Details:
  - Improve reliability and accuracy of `age` formula.
  - Improve variables comments.

### 3.1.3 - [#37](https://github.com/openfisca/country-template/pull/37)

* Minor change.
* Details:
  - Upgrade openfisca.org references to HTTPS.

### 3.1.2 - [#38](https://github.com/openfisca/country-template/pull/38)

* Minor change.
* Details:
  - Add situation example using YAML.

### 3.1.1 - [#44](https://github.com/openfisca/country-template/pull/44)

* Technical improvement.
* Details:
  - Continuously deploy Python3 package.

## 3.1.0 - [#41](https://github.com/openfisca/country-template/pull/41)

* Technical improvement.
* Details:
  - Make package compatible with Python 3.

### 3.0.2 - [#37](https://github.com/openfisca/country-template/pull/37)

* Technical change.
* Details:
  - Declare package compatible with OpenFisca Core v23.

### 3.0.1 - [#39](https://github.com/openfisca/country-template/pull/39)

* Technical change.
* Details:
  - Declare package compatible with OpenFisca Core v22.

# 3.0.0 - [#34](https://github.com/openfisca/country-template/pull/34)

#### Breaking change

* Tax and benefit system evolution.
* Impacted periods: all.
* Impacted areas: `housing`.
* Details:
  - Fix spelling by renaming `accomodation_size` variable to `accommodation_size`.

#### Other changes

* Minor change.
* Impacted areas: no functional impact.
* Details:
  - Improve spelling.

## 2.1.0 - [#29](https://github.com/openfisca/country-template/pull/29) [#30](https://github.com/openfisca/country-template/pull/30)

* Tax and benefit system evolution.
* Impacted areas:
  - Parameters `general`.
  - Variables `benefits`.
* Details:
  - Add a parameter and a variable with non ascii characters:
    - Introduce `age_of_retirement` parameter.
    - Introduce `pension` variable.

### 2.0.1 - [#24](https://github.com/openfisca/country-template/pull/24) [#27](https://github.com/openfisca/country-template/pull/27)

_Note: the 2.0.0 version has been unpublished due to performance issues._

#### Breaking change

* Details:
  - Upgrade to Core v21.
  - Introduce the use of a string identifier to reference Enum items.
  - When setting an Enum (e.g. housing_occupancy_status), set the relevant string identifier (e.g. `free_lodger`). Indexes (e.g.`2`) and phrases (e.g. `Free Lodgers`) cannot be used anymore.
  - The default value is indicated for each Enum variable instead of being implicitly the first item of the enum.

#### Web API request/response

Before:

```
"persons": {
    "Bill": {}
},
"households": {
    "_": {
        "parent": ["Bill"]
        "housing_occupancy_status": "Free Lodger"
    }
}
```

Now:

```
"persons": {
    "Bill": {}
},
"households": {
    "_": {
        "parent": ["Bill"]
        "housing_occupancy_status": "free_lodger"
    }
}
```

#### YAML testing

Before:

```
name: Household living in a 40 sq. metres accommodation while being free lodgers
  period: 2017
  input_variables:
    accommodation_size:
      2017-01: 40
    housing_occupancy_status:
      2017-01: 2
  output_variables:
    housing_tax: 0
```

Now:

```
name: Household living in a 40 sq. metres accommodation while being free lodgers
  period: 2017
  input_variables:
    accommodation_size:
      2017-01: 40
    housing_occupancy_status:
      2017-01: free_lodger
  output_variables:
    housing_tax: 0
```

#### Python API

When calculating an enum variable in Python, the output will be an [EnumArray](https://openfisca.org/doc/openfisca-python-api/enum_array.html).

See more on the OpenFisca-Core [changelog](https://github.com/openfisca/openfisca-core/blob/enums-perfs/CHANGELOG.md#2102-589-600-605).

## 1.4.0 - [#26](https://github.com/openfisca/country-template/pull/26)

* Technical improvement.
* Details:
  - Upgrade to Core v20.

### 1.3.2 - [#25](https://github.com/openfisca/country-template/pull/25)

* Technical improvement.
* Details:
  - Declare package compatible with OpenFisca Core v19.

### 1.3.1 - [#23](https://github.com/openfisca/country-template/pull/23)

* Technical improvement.
* Details:
  - Declare package compatible with OpenFisca Core v18.

## 1.3.0 - [#22](https://github.com/openfisca/country-template/pull/22)

* Tax and benefit system evolution.
* Impacted periods: all.
* Impacted areas: `stats`.
* Details:
  - Introduce `total_benefits`.
  - Introduce `total_taxes`.

<!-- -->

* Minor change.
* Details:
  - Introduce situation examples:
    - These examples can be imported with: `from openfisca_country_template.situation_examples import single, couple`.

### 1.2.7 - [#21](https://github.com/openfisca/country-template/pull/21)

* Minor change.
* Details:
  - Use the technical documentation new address.

### 1.2.6 - [#20](https://github.com/openfisca/country-template/pull/20)

* Minor change.
* Details:
  - Document entities.

### 1.2.5 - [#17](https://github.com/openfisca/country-template/pull/17)

* Technical improvement.
* Details:
  - Adapt to version `17.0.0` of Openfisca-Core.
  - Transform XML parameter files to YAML parameter files.

### 1.2.4 - [#16](https://github.com/openfisca/country-template/pull/16)

* Tax and benefit system evolution.
* Details:
  - Introduce `housing_occupancy_status`.
  - Take the housing occupancy status into account in the housing tax.

### 1.2.3 - [#9](https://github.com/openfisca/country-template/pull/9)

* Technical improvement
* Details:
  - Adapt to version `15.0.0` of Openfisca-Core.
  - Rename Variable attribute `url` to `reference`.

### 1.2.2 - [#12](https://github.com/openfisca/country-template/pull/12)

* Tax and benefit system evolution.
* Details:
  - Allow to declare a yearly amount for `salary`.
  - The yearly amount will be spread over the months contained in the year.

### 1.2.1 - [#11](https://github.com/openfisca/country-template/pull/11)

* Technical improvement.
* Details:
  - Make `make test` command not ignore failing tests.

## 1.2.0 - [#10](https://github.com/openfisca/country-template/pull/10)

* Technical improvement.
* Details:
  - Upgrade OpenFisca-Core:
    - Update the way we define formulas start dates and variables stop dates.
    - Update the naming conventions for variable formulas.
    - See the [OpenFisca-Core Changelog](https://github.com/openfisca/openfisca-core/blob/master/CHANGELOG.md#1400---522).

## 1.1.0 - [#7](https://github.com/openfisca/country-template/pull/7)

* Tax and benefit system evolution.
* Impacted periods: from 2013-01-01.
* Impacted areas:
   - Reform: `modify_social_security_taxation`.
* Details:
  - Add a reform modifying the brackets of a scale:
      - Show how to add, modify and remove a bracket.
      - Add corresponding tests.

# 1.0.0 - [#4](https://github.com/openfisca/country-template/pull/4)

* Tax and benefit system evolution.
* Impacted periods: all.
* Impacted areas:
  - `benefits`.
  - `demographics`.
  - `housing`.
  - `income`.
  - `taxes`.
* Details:
  - Build the skeleton of the tax and benefit system.
