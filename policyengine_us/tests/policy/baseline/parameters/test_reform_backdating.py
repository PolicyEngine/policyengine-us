"""Reforms must not change years outside their own period.

``CountryTaxBenefitSystem`` backdates every parameter to 2015 by copying its
earliest value back. It used to do so after applying the reform, so for a
parameter first dated after 2015:

1. a reform starting on the first dated value was copied back to 2015; and
2. a reform bounded to a year before the first dated value left the years
   between the two undefined (``None``), so a scale lost that bracket.

Structural-reform detection also read those parameters before they were
backdated, so a ``start_instant`` before 2024 raised ``ParameterNotFoundError``.

Backdating now runs before the reform is applied, on the baseline values only.
"""

import pytest
import yaml
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.system import COUNTRY_DIR, CountryTaxBenefitSystem, system

PARAMETERS = COUNTRY_DIR / "parameters"

SCALE = "calibration.gov.irs.soi.agi.number_of_returns"
SCALE_FILE = "calibration/gov/irs/soi/agi/number_of_returns.yaml"
# Reform on the first dated value, which then must not reach back to 2015.
FIRST_DATE_BRACKET = 0
FIRST_DATE_YEAR = 2021
FIRST_DATE_VALUE = 123
# Reform bounded to a year before the first dated value.
EARLY_BRACKET = 2
EARLY_YEAR = 2019
EARLY_VALUE = 789

# App-style reform ("start.2100-12-31") on a policy parameter whose first
# dated value is its start date.
RANGE_PARAMETER = "gov.irs.deductions.tip_income.cap"
RANGE_FILE = "gov/irs/deductions/tip_income/cap.yaml"
RANGE_START_YEAR = 2025
RANGE_VALUE = 50_000

# A scalar policy parameter reformed for one year before its first value.
EARLY_SCALAR = "gov.irs.deductions.auto_loan_interest.cap"
EARLY_SCALAR_FILE = "gov/irs/deductions/auto_loan_interest/cap.yaml"
EARLY_SCALAR_YEAR = 2023
EARLY_SCALAR_VALUE = 5_000

# A structural reform switch first dated after 2015, turned on from a
# ``start_instant`` before its first dated value.
SWITCH = "gov.contrib.ctc.linear_phase_out.in_effect"
SWITCH_FILE = "gov/contrib/ctc/linear_phase_out/in_effect.yaml"
SWITCH_START_YEAR = 2019
SWITCH_VARIABLE = "ctc_phase_out"
SWITCH_REFORM_FILE = "ctc_linear_phase_out.py"

YEARS = range(2015, 2031)


def first_dated_year(values):
    return min(date.year for date in values)


def scale_amount(parameter_tree, bracket, year):
    return parameter_tree.get_child(f"{SCALE}[{bracket}].amount")(f"{year}-01-01")


@pytest.fixture(scope="module")
def reformed():
    reform = Reform.from_dict(
        {
            f"{SCALE}[{FIRST_DATE_BRACKET}].amount": {
                f"year:{FIRST_DATE_YEAR}:1": FIRST_DATE_VALUE
            },
            f"{SCALE}[{EARLY_BRACKET}].amount": {f"year:{EARLY_YEAR}:1": EARLY_VALUE},
            RANGE_PARAMETER: {f"{RANGE_START_YEAR}-01-01.2100-12-31": RANGE_VALUE},
            EARLY_SCALAR: {f"year:{EARLY_SCALAR_YEAR}:1": EARLY_SCALAR_VALUE},
        },
        country_id="us",
    )
    return CountryTaxBenefitSystem(reform=(reform,)).parameters


def test_reformed_parameters_are_first_dated_after_2015():
    # Guard: the tests below only discriminate while each parameter's first
    # dated value falls after 2015, so backdating has something to fill.
    brackets = yaml.safe_load((PARAMETERS / SCALE_FILE).read_text())["brackets"]
    assert first_dated_year(brackets[FIRST_DATE_BRACKET]["amount"]["values"]) == (
        FIRST_DATE_YEAR
    )
    assert first_dated_year(brackets[EARLY_BRACKET]["amount"]["values"]) > (
        EARLY_YEAR + 1
    )
    range_values = yaml.safe_load((PARAMETERS / RANGE_FILE).read_text())["values"]
    assert first_dated_year(range_values) == RANGE_START_YEAR
    early_values = yaml.safe_load((PARAMETERS / EARLY_SCALAR_FILE).read_text())[
        "values"
    ]
    assert first_dated_year(early_values) > EARLY_SCALAR_YEAR + 1
    switch_values = yaml.safe_load((PARAMETERS / SWITCH_FILE).read_text())["values"]
    assert first_dated_year(switch_values) > SWITCH_START_YEAR


def test_reform_on_first_dated_value_is_not_backdated(reformed):
    for year in YEARS:
        expected = (
            FIRST_DATE_VALUE
            if year == FIRST_DATE_YEAR
            else scale_amount(system.parameters, FIRST_DATE_BRACKET, year)
        )
        assert scale_amount(reformed, FIRST_DATE_BRACKET, year) == expected


def test_reform_before_first_dated_value_leaves_no_gap(reformed):
    for year in YEARS:
        expected = (
            EARLY_VALUE
            if year == EARLY_YEAR
            else scale_amount(system.parameters, EARLY_BRACKET, year)
        )
        assert expected is not None
        assert scale_amount(reformed, EARLY_BRACKET, year) == expected


def test_reformed_scale_keeps_every_bracket(reformed):
    baseline_scale = system.parameters.get_child(SCALE)
    reformed_scale = reformed.get_child(SCALE)
    for year in YEARS:
        instant = f"{year}-01-01"
        assert len(reformed_scale(instant).thresholds) == len(
            baseline_scale(instant).thresholds
        )


def test_range_reform_from_first_dated_value_leaves_earlier_years(reformed):
    baseline = system.parameters.get_child(RANGE_PARAMETER)
    parameter = reformed.get_child(RANGE_PARAMETER)
    for year in YEARS:
        expected = (
            RANGE_VALUE if year >= RANGE_START_YEAR else baseline(f"{year}-01-01")
        )
        assert parameter(f"{year}-01-01") == expected


def test_scalar_reform_before_first_dated_value_leaves_no_gap(reformed):
    baseline = system.parameters.get_child(EARLY_SCALAR)
    parameter = reformed.get_child(EARLY_SCALAR)
    for year in YEARS:
        expected = (
            EARLY_SCALAR_VALUE
            if year == EARLY_SCALAR_YEAR
            else baseline(f"{year}-01-01")
        )
        assert expected is not None
        assert parameter(f"{year}-01-01") == expected


def test_only_reformed_parameters_are_marked_modified(reformed):
    # The macro-impact cache reads ``modified`` as "differs from current law".
    # Backdating edits every late-dated parameter, and those edits must not
    # leave the flag set on parameters the reform never touched.
    for name in (
        f"{SCALE}[{FIRST_DATE_BRACKET}].amount",
        f"{SCALE}[{EARLY_BRACKET}].amount",
        RANGE_PARAMETER,
        EARLY_SCALAR,
    ):
        assert reformed.get_child(name).modified
    for name in (
        f"{SCALE}[1].amount",
        "gov.irs.deductions.tip_income.phase_out.rate",
    ):
        assert not reformed.get_child(name).modified


def test_simulation_reform_leaves_earlier_years():
    # ``Simulation(reform=...)`` builds its system with the reform, the path
    # policyengine.py and the web app's API take.
    years = (RANGE_START_YEAR - 1, RANGE_START_YEAR)
    situation = {
        "people": {
            "worker": {
                "age": {year: 30 for year in years},
                "employment_income": {year: 80_000 for year in years},
                "tip_income": {year: 45_000 for year in years},
                "tip_income_deduction_occupation_requirement_met": {
                    year: True for year in years
                },
            }
        },
        "tax_units": {"tax_unit": {"members": ["worker"]}},
        "households": {
            "household": {
                "members": ["worker"],
                "state_code": {year: "TX" for year in years},
            }
        },
    }
    baseline = Simulation(situation=situation)
    reformed = Simulation(
        situation=situation,
        reform={RANGE_PARAMETER: {f"{RANGE_START_YEAR}-01-01.2100-12-31": RANGE_VALUE}},
    )
    before = RANGE_START_YEAR - 1
    assert (
        reformed.calculate("tip_income_deduction", before)[0]
        == (baseline.calculate("tip_income_deduction", before)[0])
    )
    # Tips fall under the reformed cap in the reform's own year.
    assert reformed.calculate("tip_income_deduction", RANGE_START_YEAR)[0] == 45_000


def test_structural_reform_detected_at_start_instant_before_2024():
    # Detection reads each switch at ``start_instant``. It used to read them
    # before backdating, so a switch first dated after the start was missing.
    reformed_system = CountryTaxBenefitSystem(
        reform={SWITCH: {f"{SWITCH_START_YEAR}-01-01.2100-12-31": True}},
        start_instant=f"{SWITCH_START_YEAR}-01-01",
    )
    switch = reformed_system.parameters.get_child(SWITCH)
    assert switch(f"{SWITCH_START_YEAR}-01-01")
    assert not switch(f"{SWITCH_START_YEAR - 1}-01-01")
    formulas = reformed_system.variables[SWITCH_VARIABLE].formulas.values()
    assert all(
        formula.__code__.co_filename.endswith(SWITCH_REFORM_FILE)
        for formula in formulas
    )
