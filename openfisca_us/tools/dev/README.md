# Tools for Tax-Calculator Integration

## Automated unit test generation

`generate_taxcalc_unit_tests.py` has both a command-line interface and can be debugged (set `DEBUG_MODE` to true) to both generate random OpenFisca yaml-format unit tests (from the CPS) for calcfunctions, and to debug the produced tests in Tax-Calculator.

### Manual steps required

Tax-Calculator inputs specify their structures with variables like `XTOT`, `num`, `n24`:

* `XTOT`: Total number of exemptions for filing unit.
* `num`: 2 when MARS is 2 (married filing jointly), otherwise 1.
* `nu06`: Number of dependents under 6 years old.
* `n24`: Number of children who are Child-Tax-Credit eligible, one condition for which is being under age 17
* `nu18`: Number of people in the tax unit under 18.
* `n1820`: Number of people in the tax unit age 18-20.
* `n21`: Number of people in the tax unit age 21+.

Generated unit tests might need to have their structure specified in the OpenFisca format. As a guide:

* There should be `