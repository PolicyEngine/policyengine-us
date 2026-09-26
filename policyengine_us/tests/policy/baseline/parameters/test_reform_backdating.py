"""Reforms must not change years outside their own period.

``CountryTaxBenefitSystem`` backdates every parameter to 2015 by copying its
earliest value back. It used to do so after applying the reform, so for a
parameter first dated after 2015:

1. a reform starting on or before the first dated value was copied back to
   2015; and
2. a reform bounded to a year before the first dated value was copied back to
   2015 and left the years between the two undefined (``None``), so a scale
   lost that bracket and a formula reading the parameter raised
   ``ParameterNotFoundError``.

Structural-reform detection also read contrib parameters before backdating,
so any ``start_instant`` from 2015 through 2023 raised
``ParameterNotFoundError`` while the system was built.

Backdating now runs before the reform is applied, on the baseline values, and
again afterwards for any parameter the reform added.
"""

import datetime
import math
from pathlib import Path

import pytest
import yaml
from policyengine_core.parameters import Parameter
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

# App-style reform starting before a breakdown parameter's first dated value.
BEFORE_PARAMETER = "gov.irs.deductions.overtime_income.cap.SINGLE"
BEFORE_FILE = "gov/irs/deductions/overtime_income/cap.yaml"
BEFORE_START_YEAR = 2023
BEFORE_VALUE = 20_000

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

# A parameter a reform adds, first dated after 2015. It has no baseline, so
# its first dated value is backdated to 2015 like any other parameter's.
ADDED_NAME = "reform_backdating_added"
ADDED_PARAMETER = f"gov.contrib.{ADDED_NAME}"
ADDED_YEAR = 2025
ADDED_VALUE = 7

YEARS = range(2015, 2031)

TIPS = 45_000
AUTO_LOAN_INTEREST = 8_000


def first_dated_year(file, *keys):
    # BaseLoader keeps dates as strings, so a "0000-01-01" key parses too.
    node = yaml.load((PARAMETERS / file).read_text(), Loader=yaml.BaseLoader)
    for key in keys:
        node = node[key]
    return min(int(date[:4]) for date in node)


def series(parameter):
    return {year: parameter(f"{year}-01-01") for year in YEARS}


def formula_files(tax_benefit_system):
    variable = tax_benefit_system.variables[SWITCH_VARIABLE]
    return {
        Path(formula.__code__.co_filename).name
        for formula in variable.formulas.values()
    }


def add_parameter(parameters):
    # ``__init__`` applies a reform twice, so an added child needs a guard.
    if ADDED_NAME not in parameters.gov.contrib.children:
        parameters.gov.contrib.add_child(
            ADDED_NAME,
            Parameter(ADDED_PARAMETER, data={f"{ADDED_YEAR}-01-01": ADDED_VALUE}),
        )
    return parameters


class add_parameter_reform(Reform):
    def apply(self):
        self.modify_parameters(add_parameter)


@pytest.fixture(scope="module")
def reformed():
    reform = Reform.from_dict(
        {
            f"{SCALE}[{FIRST_DATE_BRACKET}].amount": {
                f"year:{FIRST_DATE_YEAR}:1": FIRST_DATE_VALUE
            },
            f"{SCALE}[{EARLY_BRACKET}].amount": {f"year:{EARLY_YEAR}:1": EARLY_VALUE},
            RANGE_PARAMETER: {f"{RANGE_START_YEAR}-01-01.2100-12-31": RANGE_VALUE},
            BEFORE_PARAMETER: {f"{BEFORE_START_YEAR}-01-01.2100-12-31": BEFORE_VALUE},
            EARLY_SCALAR: {f"year:{EARLY_SCALAR_YEAR}:1": EARLY_SCALAR_VALUE},
        },
        country_id="us",
    )
    return CountryTaxBenefitSystem(reform=(reform, add_parameter_reform)).parameters


GUARDS = [
    pytest.param(
        SCALE_FILE,
        ("brackets", FIRST_DATE_BRACKET, "amount", "values"),
        lambda year: year == FIRST_DATE_YEAR,
        id=f"{SCALE}[{FIRST_DATE_BRACKET}].amount",
    ),
    pytest.param(
        SCALE_FILE,
        ("brackets", EARLY_BRACKET, "amount", "values"),
        lambda year: year > EARLY_YEAR + 1,
        id=f"{SCALE}[{EARLY_BRACKET}].amount",
    ),
    pytest.param(
        RANGE_FILE,
        ("values",),
        lambda year: year == RANGE_START_YEAR,
        id=RANGE_PARAMETER,
    ),
    pytest.param(
        BEFORE_FILE,
        ("SINGLE",),
        lambda year: year > BEFORE_START_YEAR,
        id=BEFORE_PARAMETER,
    ),
    pytest.param(
        EARLY_SCALAR_FILE,
        ("values",),
        lambda year: year > EARLY_SCALAR_YEAR + 1,
        id=EARLY_SCALAR,
    ),
    pytest.param(
        SWITCH_FILE,
        ("values",),
        lambda year: year > SWITCH_START_YEAR,
        id=SWITCH,
    ),
]


@pytest.mark.parametrize("file, keys, check", GUARDS)
def test_reformed_parameters_are_first_dated_after_2015(file, keys, check):
    # Guard: the tests below only discriminate while each parameter's first
    # dated value falls where the constants above assume.
    year = first_dated_year(file, *keys)
    assert check(year), (
        f"{file} is now first dated {year}; choose another parameter first "
        "dated after 2015 or these regression tests stop discriminating."
    )


def test_reform_on_first_dated_value_is_not_backdated(reformed):
    name = f"{SCALE}[{FIRST_DATE_BRACKET}].amount"
    baseline = series(system.parameters.get_child(name))
    assert series(reformed.get_child(name)) == {
        **baseline,
        FIRST_DATE_YEAR: FIRST_DATE_VALUE,
    }


def test_reform_before_first_dated_value_leaves_no_gap(reformed):
    name = f"{SCALE}[{EARLY_BRACKET}].amount"
    baseline = series(system.parameters.get_child(name))
    assert None not in baseline.values()
    assert series(reformed.get_child(name)) == {**baseline, EARLY_YEAR: EARLY_VALUE}


def test_reformed_scale_keeps_every_bracket(reformed):
    baseline_scale = system.parameters.get_child(SCALE)
    reformed_scale = reformed.get_child(SCALE)
    counts = {year: len(reformed_scale(f"{year}-01-01").thresholds) for year in YEARS}
    assert counts == {
        year: len(baseline_scale(f"{year}-01-01").thresholds) for year in YEARS
    }


def test_range_reform_from_first_dated_value_leaves_earlier_years(reformed):
    baseline = series(system.parameters.get_child(RANGE_PARAMETER))
    assert series(reformed.get_child(RANGE_PARAMETER)) == {
        year: RANGE_VALUE if year >= RANGE_START_YEAR else value
        for year, value in baseline.items()
    }


def test_range_reform_before_first_dated_value_leaves_earlier_years(reformed):
    baseline = series(system.parameters.get_child(BEFORE_PARAMETER))
    assert series(reformed.get_child(BEFORE_PARAMETER)) == {
        year: BEFORE_VALUE if year >= BEFORE_START_YEAR else value
        for year, value in baseline.items()
    }


def test_scalar_reform_before_first_dated_value_leaves_no_gap(reformed):
    baseline = series(system.parameters.get_child(EARLY_SCALAR))
    assert None not in baseline.values()
    assert series(reformed.get_child(EARLY_SCALAR)) == {
        **baseline,
        EARLY_SCALAR_YEAR: EARLY_SCALAR_VALUE,
    }


def test_parameter_added_by_reform_is_backdated(reformed):
    assert series(reformed.get_child(ADDED_PARAMETER)) == {
        year: ADDED_VALUE for year in YEARS
    }


def test_only_reformed_parameters_are_marked_modified(reformed):
    # The macro-impact cache reads ``modified`` as "differs from current law".
    # ``Parameter.update`` marks every late-dated parameter that backdating
    # fills, so the reset in ``__init__`` must stay after backdating. This
    # guards the new order; the old order passes it too.
    for name in (
        f"{SCALE}[{FIRST_DATE_BRACKET}].amount",
        f"{SCALE}[{EARLY_BRACKET}].amount",
        RANGE_PARAMETER,
        BEFORE_PARAMETER,
        EARLY_SCALAR,
    ):
        assert reformed.get_child(name).modified
    for name in (
        f"{SCALE}[1].amount",
        "gov.irs.deductions.tip_income.phase_out.rate",
    ):
        assert not reformed.get_child(name).modified


def test_simulation_reform_leaves_earlier_years():
    # ``Simulation(reform=...)`` builds ``CountryTaxBenefitSystem(reform=...)``
    # (``spm.py`` ``_prepare_spm_system``); core then applies the reform again.
    years = range(EARLY_SCALAR_YEAR - 1, RANGE_START_YEAR + 1)
    situation = {
        "people": {
            "worker": {
                "age": {year: 30 for year in years},
                "employment_income": {year: 80_000 for year in years},
                "tip_income": {year: TIPS for year in years},
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
                "qualified_passenger_vehicle_loan_interest": {
                    year: AUTO_LOAN_INTEREST for year in years
                },
            }
        },
    }
    baseline = Simulation(situation=situation)
    reformed = Simulation(
        situation=situation,
        reform={
            RANGE_PARAMETER: {f"{RANGE_START_YEAR}-01-01.2100-12-31": RANGE_VALUE},
            EARLY_SCALAR: {f"year:{EARLY_SCALAR_YEAR}:1": EARLY_SCALAR_VALUE},
        },
    )

    # The simulation's own tree, independent of how any formula gates by year.
    cap = reformed.tax_benefit_system.parameters.get_child(RANGE_PARAMETER)
    baseline_cap = system.parameters.get_child(RANGE_PARAMETER)
    before = RANGE_START_YEAR - 1
    assert cap(f"{before}-01-01") == baseline_cap(f"{before}-01-01")

    def tip_deduction(simulation, year):
        return simulation.calculate("tip_income_deduction", year)[0]

    # Guard: a leaked cap only shows while the baseline computes the
    # deduction before the cap's first dated year, below the reformed cap.
    assert 0 < tip_deduction(baseline, before) < min(TIPS, RANGE_VALUE)
    assert tip_deduction(reformed, before) == tip_deduction(baseline, before)
    assert tip_deduction(reformed, RANGE_START_YEAR) == min(TIPS, RANGE_VALUE)

    def auto_loan_deduction(simulation, year):
        return simulation.calculate("auto_loan_interest_deduction", year)[0]

    # The year after the bounded reform used to be undefined, so this formula
    # raised ParameterNotFoundError; the year before it received the reform.
    for year in (EARLY_SCALAR_YEAR - 1, EARLY_SCALAR_YEAR + 1):
        assert auto_loan_deduction(baseline, year) == AUTO_LOAN_INTEREST
        assert auto_loan_deduction(reformed, year) == AUTO_LOAN_INTEREST
    assert auto_loan_deduction(reformed, EARLY_SCALAR_YEAR) == EARLY_SCALAR_VALUE


def test_structural_reform_detected_at_start_instant_before_2024():
    # Detection reads the structural switches from ``start_instant``. The old
    # order read them before backdating, so building at a start before some
    # switch's first dated value raised ParameterNotFoundError, whatever the
    # reform. ``Simulation`` builds the system with ``start_instant`` and then
    # runs detection again.
    simulation = Simulation(
        situation={
            "people": {"parent": {"age": 40}},
            "tax_units": {"tax_unit": {"members": ["parent"]}},
            "households": {"household": {"members": ["parent"]}},
        },
        reform={SWITCH: {f"{SWITCH_START_YEAR}-01-01.2100-12-31": True}},
        start_instant=f"{SWITCH_START_YEAR}-01-01",
    )
    switch = simulation.tax_benefit_system.parameters.get_child(SWITCH)
    assert switch(f"{SWITCH_START_YEAR}-01-01")
    assert not switch(f"{SWITCH_START_YEAR - 1}-01-01")
    # Guard: the formula check only discriminates while the baseline formula
    # lives in another file.
    baseline_files = formula_files(system)
    assert baseline_files and SWITCH_REFORM_FILE not in baseline_files
    assert formula_files(simulation.tax_benefit_system) == {SWITCH_REFORM_FILE}


BACKDATED_FROM = "2015-01-01"
CHECKED_YEARS = range(2015, 2036)


def shifted(instant, years=0, days=0):
    date = datetime.date.fromisoformat(instant)
    date = date.replace(year=date.year + years) + datetime.timedelta(days=days)
    return date.isoformat()


def backdated_first_date(parameter):
    # Backdating inserts a copy of the first dated value at 2015-01-01.
    values = parameter.values_list
    if (
        len(values) > 1
        and values[-1].instant_str == BACKDATED_FROM
        and values[-2].value == values[-1].value
    ):
        return values[-2].instant_str
    return None


def perturbed(value):
    if isinstance(value, bool):
        return not value
    if isinstance(value, (int, float)) and math.isfinite(value):
        return type(value)(value * 1.5 + 7)
    return None


@pytest.fixture(scope="module")
def every_backdated_parameter():
    """Reform every backdated numeric or boolean parameter at once.

    Parameters cycle through three windows: the year from the first dated
    value, the year before it, and from a year before it to 2100 (the app's
    format). ``gov.contrib`` is left out because its switches trigger
    structural reforms.
    """
    windows = {}
    for parameter in sorted(
        system.parameters.get_descendants(), key=lambda node: node.name
    ):
        if not isinstance(parameter, Parameter):
            continue
        if parameter.name.startswith("gov.contrib."):
            continue
        first = backdated_first_date(parameter)
        value = perturbed(parameter(first)) if first else None
        if value is None:
            continue
        shape = len(windows) % 3
        if shape == 0:
            start, stop = first, shifted(first, years=1, days=-1)
        elif shape == 1:
            start, stop = shifted(first, years=-1), shifted(first, days=-1)
        else:
            start, stop = shifted(first, years=-1), "2100-12-31"
        windows[parameter.name] = (start, stop, value)
    reform = {
        name: {f"{start}.{stop}": value}
        for name, (start, stop, value) in windows.items()
    }
    constructed = CountryTaxBenefitSystem(reform=reform).parameters
    # A dict reform applied to the finished system, as the YAML test runner
    # and the household API apply one.
    applied_afterwards = Reform.from_dict(reform, country_id="us")(system).parameters
    return windows, constructed, applied_afterwards


def checked_instants(start, stop):
    instants = {f"{year}-{day}" for year in CHECKED_YEARS for day in ("01-01", "07-01")}
    instants |= {start, stop, shifted(start, days=-1), shifted(stop, days=1)}
    return sorted(t for t in instants if BACKDATED_FROM <= t <= "2100-12-31")


def test_every_backdated_parameter_changes_only_in_its_reform_period(
    every_backdated_parameter,
):
    # Invariant: from 2015 on, a reformed parameter equals the reform value
    # inside the reform's period and its baseline value everywhere else.
    windows, constructed, _ = every_backdated_parameter
    assert len(windows) > 1_000
    violations = []
    for name, (start, stop, value) in windows.items():
        baseline = system.parameters.get_child(name)
        reformed = constructed.get_child(name)
        for instant in checked_instants(start, stop):
            expected = value if start <= instant <= stop else baseline(instant)
            if reformed(instant) != expected:
                violations.append((name, instant, reformed(instant), expected))
                break
    assert not violations, f"{len(violations)} parameters, e.g. {violations[:5]}"


def test_reform_at_construction_matches_reform_applied_afterwards(
    every_backdated_parameter,
):
    # Differential: building the system with a reform must match applying the
    # same reform to the finished, already backdated system.
    windows, constructed, applied_afterwards = every_backdated_parameter
    violations = []
    for name, (start, stop, _) in windows.items():
        at_construction = constructed.get_child(name)
        afterwards = applied_afterwards.get_child(name)
        for instant in checked_instants(start, stop):
            if at_construction(instant) != afterwards(instant):
                violations.append(
                    (name, instant, at_construction(instant), afterwards(instant))
                )
                break
    assert not violations, f"{len(violations)} parameters, e.g. {violations[:5]}"
