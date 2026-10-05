"""An unset or infinite bracket adds no tax in the additional_tax_bracket reform.

The reform taxes ordinary income on its own eight-bracket schedule,
``gov.contrib.additional_tax_bracket.bracket``, through the shared functions
``tax_at_main_rates`` and ``amount_taxed_below_rate``. Its parameter file sets
the thresholds of brackets 7 and 8 to infinity for every filing status and
year, so the added bracket is unset until a user sets bracket 7's threshold.
Bracket 8 then runs from infinity to infinity. Both functions took each
bracket's amount as ``amount_between(x, bottom, top)``, which is
``clip(x, bottom, top) - bottom`` (``amount_taxed_below_rate`` only for
brackets taxed below its limit), and for that bracket
clip(x, inf, inf) - inf = inf - inf = NaN. With its default parameters the
reform therefore gave NaN for ``income_tax_main_rates`` and
``regular_tax_before_credits`` for every household, including one with no
taxable income. Both now take each bracket's amount from
``amounts_in_brackets``, as max(0, min(x, top) - bottom), the form
policyengine-core's ``MarginalRateTaxScale.calc`` uses. It is zero for a
bracket whose bottom is infinite and equals the clip form whenever the bottom
is finite.

Properties of ``tax_at_main_rates`` for any thresholds (finite or infinite, in
any order), rates in [0, 1] and taxable amounts in [0, $10 million]:

- the tax is finite and non-negative;
- it agrees with policyengine-core's ``MarginalRateTaxScale`` over the same
  brackets (a differential test), and bit for bit with the old clip form
  wherever that form gave a number, so a schedule with finite bracket bottoms,
  such as the baseline's, is unchanged;
- the added bracket changes the tax by exactly (r8 - r7) times the income in
  bracket 8. So the tax is at least the tax with the bracket removed, meaning
  bracket 8's income taxed at bracket 7's rate, whenever r8 >= r7. When
  r8 < r7 the added bracket cuts the tax, as intended;
- with bracket 7's threshold at infinity, as shipped, bracket 8 adds exactly
  nothing, whatever its rate or threshold.

``amount_taxed_below_rate``, under the same conditions and for any rate limit
in [0, 1], is finite, between zero and the amount, bit for bit the tax at
rates of 1 for the brackets taxed below the limit and 0 for the others, and
bit for bit the old clip form wherever that form gave a number.

Properties of the reform, run in simulations:

- with its default parameters, every tax, and the taxable income taxed
  below 25 percent, is finite in 2025 and 2026;
- with its first seven brackets set to current law and the added bracket
  unset, it reproduces the baseline;
- for any thresholds of brackets 7 and 8, finite or infinite, the reform's
  ``income_tax_main_rates``, ``regular_tax_before_credits`` and
  ``taxable_income_taxed_below_25_percent`` are finite, and its two taxes are
  at least their values with the bracket removed when r8 >= r7. The
  households have no 28 percent rate gain or unrecaptured section 1250 gain,
  so the amount taxed below 25 percent does not change which of their income
  is taxed at the regular rates (``dwks19`` and
  ``capital_gains_excluded_from_taxable_income``).

No simulation here sets a foreign earned income exclusion, so the reform's
subtraction of the tax on the excluded amount is covered only through the
properties of ``tax_at_main_rates``, which hold for the excluded amount as for
any other, and not end to end.
"""

import numpy as np
import pytest
from policyengine_core.parameters import ParameterNode
from policyengine_core.reforms import Reform
from policyengine_core.taxscales import MarginalRateTaxScale

from policyengine_us import CountryTaxBenefitSystem, Simulation
from policyengine_us.reforms.additional_tax_bracket.additional_tax_bracket_reform import (
    additional_tax_bracket,
)
from policyengine_us.system import system as baseline_system
from policyengine_us.variables.gov.irs.tax.federal_income.before_credits.tax_at_main_rates import (
    amount_taxed_below_rate,
    tax_at_main_rates,
)
from policyengine_us.variables.household.demographic.tax_unit.filing_status import (
    FilingStatus,
)

# Hypothesis is a dev extra; skip rather than fail collection without it.
hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

INF = float("inf")
STATUSES = [status.name for status in FilingStatus]
N_BRACKETS = 8
BRACKET = "gov.contrib.additional_tax_bracket.bracket"
YEAR = 2026
REFORM_TAXES = ["income_tax_main_rates", "regular_tax_before_credits"]
# Every variable the reform replaces.
REFORM_VARIABLES = REFORM_TAXES + ["taxable_income_taxed_below_25_percent"]
DOWNSTREAM_VARIABLES = REFORM_VARIABLES + ["income_tax_before_credits", "income_tax"]
# Simulation variables are float32, about seven significant digits, so
# compare taxes of up to a few million dollars to the dollar.
SIMULATION_TOLERANCE = 1.0

# ---------------------------------------------------------------------------
# tax_at_main_rates on drawn schedules
# ---------------------------------------------------------------------------


def bracket_node(thresholds, rates, instant="2026-01-01"):
    """A bracket parameter node at an instant, shaped like the reform's.

    ``thresholds`` maps each filing status to the thresholds of brackets 1 to
    n, and ``rates`` lists the n rates.
    """
    data = {
        "rates": {
            str(i): {"values": {instant: rate}} for i, rate in enumerate(rates, 1)
        },
        "thresholds": {
            str(i): {
                status: {"values": {instant: thresholds[status][i - 1]}}
                for status in STATUSES
            }
            for i in range(1, len(rates) + 1)
        },
    }
    return ParameterNode("bracket", data=data)(instant)


def bracket_bottoms(thresholds):
    """Bottoms of brackets 1 to n + 1 for one status: 0, then the running
    maximum of the thresholds, as the loop clamps them (#9084)."""
    return np.maximum.accumulate([0.0, *thresholds])


def scale_tax(incomes, statuses, thresholds, rates):
    """The same schedule computed by policyengine-core's MarginalRateTaxScale.

    The loop leaves income above the last threshold untaxed, so the scale
    ends with a zero-rate bracket there.
    """
    tax = np.zeros_like(incomes)
    for status in STATUSES:
        in_status = statuses == status
        if not in_status.any():
            continue
        scale = MarginalRateTaxScale()
        scale.thresholds = list(bracket_bottoms(thresholds[status]))
        scale.rates = [*rates, 0.0]
        tax[in_status] = scale.calc(incomes[in_status])
    return tax


def clip_form_tax(incomes, filing_status, bracket, n_brackets):
    """tax_at_main_rates as it was before this fix, with amount_between's
    clip(x, bottom, top) - bottom."""
    tax = 0
    bottom = 0
    with np.errstate(invalid="ignore"):
        for i in range(1, n_brackets + 1):
            top = np.maximum(bottom, bracket.thresholds[str(i)][filing_status])
            tax = tax + bracket.rates[str(i)] * (np.clip(incomes, bottom, top) - bottom)
            bottom = top
    return tax


def clip_form_amount_below_rate(incomes, filing_status, bracket, n_brackets, limit):
    """amount_taxed_below_rate as it was before this fix."""
    amount = 0
    bottom = 0
    with np.errstate(invalid="ignore"):
        for i in range(1, n_brackets + 1):
            top = np.maximum(bottom, bracket.thresholds[str(i)][filing_status])
            if bracket.rates[str(i)] < limit:
                amount = amount + (np.clip(incomes, bottom, top) - bottom)
            bottom = top
    return amount


threshold_values = st.one_of(
    st.just(INF),
    st.floats(0, 2_000_000, allow_nan=False, allow_infinity=False),
)
rate_values = st.floats(0, 1, allow_nan=False, allow_infinity=False)


@st.composite
def schedules(draw):
    thresholds = {
        status: draw(
            st.lists(threshold_values, min_size=N_BRACKETS, max_size=N_BRACKETS)
        )
        for status in STATUSES
    }
    rates = draw(st.lists(rate_values, min_size=N_BRACKETS, max_size=N_BRACKETS))
    return thresholds, rates


@st.composite
def households(draw):
    count = draw(st.integers(1, 12))
    incomes = draw(
        st.lists(
            st.floats(0, 10_000_000, allow_nan=False, allow_infinity=False),
            min_size=count,
            max_size=count,
        )
    )
    statuses = draw(st.lists(st.sampled_from(STATUSES), min_size=count, max_size=count))
    return np.array(incomes), np.array(statuses)


# Shaped like the reform's defaults: brackets 7 and 8 at infinity.
UNSET_BRACKET_THRESHOLDS = {
    status: [10_000, 40_000, 90_000, 190_000, 240_000, 600_000, INF, INF]
    for status in STATUSES
}
UNSET_BRACKET_RATES = [0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37, 0.37]
# A loaded machine can stall a draw; as in the repository's other Hypothesis
# tests, slow generation is not a failure.
HEALTH_CHECKS = [hypothesis.HealthCheck.too_slow, hypothesis.HealthCheck.data_too_large]
SETTINGS = dict(
    max_examples=300,
    deadline=None,
    derandomize=True,
    suppress_health_check=HEALTH_CHECKS,
)


@hypothesis.settings(**SETTINGS)
@hypothesis.given(schedules(), households())
@hypothesis.example(
    (UNSET_BRACKET_THRESHOLDS, UNSET_BRACKET_RATES),
    (np.array([0.0, 50_000.0, 2_000_000.0]), np.array(["SINGLE", "JOINT", "SEPARATE"])),
)
def test_schedule_tax_is_finite_and_matches_core_tax_scale(schedule, units):
    thresholds, rates = schedule
    incomes, statuses = units
    bracket = bracket_node(thresholds, rates)
    filing_status = FilingStatus.encode(statuses)
    tax = tax_at_main_rates(incomes, filing_status, bracket)

    assert np.all(np.isfinite(tax))
    assert np.all(tax >= 0)
    np.testing.assert_allclose(
        tax, scale_tax(incomes, statuses, thresholds, rates), rtol=1e-12, atol=1e-6
    )
    # Where the clip form gave a number it is unchanged, bit for bit.
    old = clip_form_tax(incomes, filing_status, bracket, N_BRACKETS)
    defined = ~np.isnan(old)
    assert np.array_equal(tax[defined], old[defined])
    # And it gave NaN exactly where a bracket's bottom is infinite.
    infinite_bottom = np.array(
        [np.isinf(bracket_bottoms(thresholds[s])[N_BRACKETS - 1]) for s in statuses]
    )
    assert np.array_equal(~defined, infinite_bottom)


@hypothesis.settings(**SETTINGS)
@hypothesis.given(schedules(), households())
def test_added_bracket_changes_tax_by_its_own_income_only(schedule, units):
    thresholds, rates = schedule
    incomes, statuses = units
    filing_status = FilingStatus.encode(statuses)
    with_bracket = tax_at_main_rates(
        incomes, filing_status, bracket_node(thresholds, rates)
    )
    # Removing the added bracket taxes its income at bracket 7's rate.
    removed_rates = [*rates[:-1], rates[-2]]
    removed = tax_at_main_rates(
        incomes, filing_status, bracket_node(thresholds, removed_rates)
    )
    bottoms = np.array([bracket_bottoms(thresholds[s]) for s in statuses])
    bracket_8_income = np.maximum(
        0, np.minimum(incomes, bottoms[:, N_BRACKETS]) - bottoms[:, N_BRACKETS - 1]
    )
    np.testing.assert_allclose(
        with_bracket - removed,
        (rates[-1] - rates[-2]) * bracket_8_income,
        rtol=1e-9,
        atol=1e-6,
    )
    if rates[-1] >= rates[-2]:
        assert np.all(with_bracket >= removed - 1e-6)


@hypothesis.settings(**SETTINGS)
@hypothesis.given(schedules(), households())
def test_unset_added_bracket_adds_nothing(schedule, units):
    thresholds, rates = schedule
    incomes, statuses = units
    # Bracket 7's threshold at infinity, as shipped.
    thresholds = {
        status: [*values[: N_BRACKETS - 2], INF, values[-1]]
        for status, values in thresholds.items()
    }
    filing_status = FilingStatus.encode(statuses)
    eight = tax_at_main_rates(incomes, filing_status, bracket_node(thresholds, rates))
    seven = tax_at_main_rates(
        incomes,
        filing_status,
        bracket_node(
            {status: thresholds[status][:-1] for status in STATUSES}, rates[:-1]
        ),
    )
    assert np.all(np.isfinite(eight))
    assert np.array_equal(eight, seven)


@hypothesis.settings(**SETTINGS)
@hypothesis.given(schedules(), households(), rate_values)
@hypothesis.example(
    (UNSET_BRACKET_THRESHOLDS, [0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.10, 0.10]),
    (np.array([0.0, 50_000.0, 2_000_000.0]), np.array(["SINGLE", "JOINT", "SEPARATE"])),
    0.25,
)
# A rate equal to the limit is not below it, as with the reform's 2026
# bracket 3 rate of 25 percent.
@hypothesis.example(
    (UNSET_BRACKET_THRESHOLDS, [0.10, 0.15, 0.25, 0.28, 0.33, 0.35, 0.396, 0.396]),
    (np.array([0.0, 50_000.0, 2_000_000.0]), np.array(["SINGLE", "JOINT", "SEPARATE"])),
    0.25,
)
def test_amount_taxed_below_rate_is_finite_and_matches_indicator_rates(
    schedule, units, limit
):
    thresholds, rates = schedule
    incomes, statuses = units
    bracket = bracket_node(thresholds, rates)
    filing_status = FilingStatus.encode(statuses)
    # With no rate below the limit the function returns the scalar 0, which
    # policyengine-core fills into an array for a formula.
    amount = np.broadcast_to(
        amount_taxed_below_rate(incomes, filing_status, bracket, limit),
        incomes.shape,
    )

    assert np.all(np.isfinite(amount))
    assert np.all(amount >= 0)
    # The brackets' pieces sum to at most the taxable amount, up to rounding.
    assert np.all(amount <= incomes + 1e-6)
    # The amount is the tax at rates of 1 below the limit and 0 otherwise.
    indicators = [1.0 if rate < limit else 0.0 for rate in rates]
    at_indicators = tax_at_main_rates(
        incomes, filing_status, bracket_node(thresholds, indicators)
    )
    assert np.array_equal(amount, at_indicators)
    np.testing.assert_allclose(
        amount,
        scale_tax(incomes, statuses, thresholds, indicators),
        rtol=1e-12,
        atol=1e-6,
    )
    old = np.broadcast_to(
        clip_form_amount_below_rate(incomes, filing_status, bracket, N_BRACKETS, limit),
        incomes.shape,
    )
    defined = ~np.isnan(old)
    assert np.array_equal(amount[defined], old[defined])


def test_baseline_schedule_is_unchanged_in_every_year():
    # The baseline's top bracket has an infinite threshold but a finite
    # bottom, so the clip form was defined; the new form must reproduce it,
    # for the tax and for the income taxed below 25 percent.
    incomes = np.linspace(0, 2_000_000, 401)
    for status in STATUSES:
        statuses = np.full(incomes.shape, status)
        filing_status = FilingStatus.encode(statuses)
        for year in range(2018, 2036):
            bracket = baseline_system.parameters(f"{year}-01-01").gov.irs.income.bracket
            n_brackets = len(list(bracket.rates))
            tax = tax_at_main_rates(incomes, filing_status, bracket)
            old = clip_form_tax(incomes, filing_status, bracket, n_brackets)
            assert np.all(np.isfinite(tax))
            assert np.array_equal(tax, old), (status, year)
            limit = baseline_system.parameters(
                f"{year}-01-01"
            ).gov.irs.capital_gains.regular_rate_limit
            below = amount_taxed_below_rate(incomes, filing_status, bracket, limit)
            old_below = clip_form_amount_below_rate(
                incomes, filing_status, bracket, n_brackets, limit
            )
            assert np.array_equal(below, old_below), (status, year)


# ---------------------------------------------------------------------------
# The reform in simulations
# ---------------------------------------------------------------------------

ORDINARY_INCOMES = [0, 30_000, 250_000, 700_000, 3_000_000]
# (long-term capital gains, qualified dividends): none, and enough to take
# the Schedule D Tax Worksheet path in regular_tax_before_credits.
PREFERENTIAL_INCOME = [(0, 0), (150_000, 20_000)]


def grid_situation(year):
    """One single-member tax unit per (status, taxable income, gains) cell.

    Taxable income is an input, so the schedule is the only part of the tax
    that varies across these simulations.
    """
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for status in STATUSES:
        for income in ORDINARY_INCOMES:
            for gains, dividends in PREFERENTIAL_INCOME:
                key = f"{status}_{income}_{gains}"
                situation["people"][key] = {
                    "age": {year: 40},
                    "long_term_capital_gains": {year: gains},
                    "qualified_dividend_income": {year: dividends},
                }
                situation["tax_units"][key] = {
                    "members": [key],
                    "filing_status": {year: status},
                    "taxable_income": {year: income + gains + dividends},
                }
                situation["households"][key] = {
                    "members": [key],
                    "state_code": {year: "TX"},
                }
    return situation


GRID_SIZE = len(STATUSES) * len(ORDINARY_INCOMES) * len(PREFERENTIAL_INCOME)


@pytest.fixture(scope="module")
def reform_system():
    """The reform's system, built once; each simulation that changes its
    parameters works on its own clone."""
    return CountryTaxBenefitSystem(reform=additional_tax_bracket)


def calculate(variables, year, tax_benefit_system, reform=None):
    sim = Simulation(
        tax_benefit_system=tax_benefit_system,
        reform=reform,
        situation=grid_situation(year),
    )
    assert np.array_equal(
        sim.calculate("filing_status", year).decode_to_str(),
        np.repeat(STATUSES, GRID_SIZE // len(STATUSES)),
    )
    return {variable: sim.calculate(variable, year) for variable in variables}


@pytest.mark.parametrize("year", [2025, 2026])
def test_default_parameters_give_finite_taxes(reform_system, year):
    taxes = calculate(DOWNSTREAM_VARIABLES, year, reform_system)
    for variable, values in taxes.items():
        assert len(values) == GRID_SIZE
        assert np.all(np.isfinite(values)), variable
    assert np.all(taxes["income_tax_main_rates"] >= 0)
    assert taxes["income_tax_main_rates"].max() > 0


def current_law_first_seven_brackets(year):
    """Set the reform's brackets 1 to 7 to the baseline's for one year, and
    leave the added bracket unset (its shipped infinite thresholds)."""
    p = baseline_system.parameters(f"{year}-01-01").gov.irs.income.bracket
    period = f"{year}-01-01.{year}-12-31"
    changes = {}
    for i in range(1, 8):
        changes[f"{BRACKET}.rates.{i}"] = {period: float(p.rates[str(i)])}
        for status in STATUSES:
            changes[f"{BRACKET}.thresholds.{i}.{status}"] = {
                period: float(p.thresholds[str(i)][status])
            }
    return Reform.from_dict(changes, country_id="us")


def test_reform_with_unset_bracket_reproduces_current_law(reform_system):
    reform = calculate(
        DOWNSTREAM_VARIABLES,
        YEAR,
        reform_system,
        reform=current_law_first_seven_brackets(YEAR),
    )
    baseline = calculate(DOWNSTREAM_VARIABLES, YEAR, baseline_system)
    for variable in DOWNSTREAM_VARIABLES:
        np.testing.assert_allclose(
            reform[variable], baseline[variable], atol=SIMULATION_TOLERANCE
        )
    assert baseline["income_tax_main_rates"].max() > 0


def added_bracket(thresholds_7, thresholds_8, rate_7, rate_8):
    period = f"{YEAR}-01-01.{YEAR}-12-31"
    changes = {
        f"{BRACKET}.rates.7": {period: rate_7},
        f"{BRACKET}.rates.8": {period: rate_8},
    }
    for status in STATUSES:
        changes[f"{BRACKET}.thresholds.7.{status}"] = {period: thresholds_7[status]}
        changes[f"{BRACKET}.thresholds.8.{status}"] = {period: thresholds_8[status]}
    return Reform.from_dict(changes, country_id="us")


def per_status(values):
    return st.fixed_dictionaries({status: values for status in STATUSES})


simulation_thresholds = st.one_of(
    st.just(INF),
    st.floats(0, 4_000_000, allow_nan=False, allow_infinity=False),
)


# Thresholds are set per filing status, so one simulation covers a shape of
# brackets 7 and 8 for each status: (bracket 7 threshold, bracket 8 threshold).
THRESHOLD_SHAPES = {
    # As shipped: both infinite.
    "SINGLE": (INF, INF),
    # As the YAML tests use it: a finite bracket 7 threshold, bracket 8
    # unbounded.
    "JOINT": (800_000, INF),
    # Bracket 8's threshold below bracket 7's.
    "SEPARATE": (900_000, 500_000),
    # A zero bracket 7 threshold.
    "HEAD_OF_HOUSEHOLD": (0, INF),
    # Bracket 7 unbounded above a finite bracket 8 threshold.
    "SURVIVING_SPOUSE": (INF, 300_000),
}
SHAPES_7 = {status: shape[0] for status, shape in THRESHOLD_SHAPES.items()}
SHAPES_8 = {status: shape[1] for status, shape in THRESHOLD_SHAPES.items()}


# Each example runs two simulations on clones of the reform's system, and the
# file runs in two CI steps, so the generated examples are few; the schedule
# properties above take 300 examples each.
@hypothesis.settings(
    max_examples=3,
    deadline=None,
    derandomize=True,
    suppress_health_check=HEALTH_CHECKS,
)
@hypothesis.given(
    per_status(simulation_thresholds),
    per_status(simulation_thresholds),
    st.tuples(rate_values, rate_values).map(sorted),
)
# The shipped rates, equal, so the bracket changes nothing.
@hypothesis.example(SHAPES_7, SHAPES_8, [0.396, 0.396])
# A higher top rate, as in the YAML tests.
@hypothesis.example(SHAPES_7, SHAPES_8, [0.396, 0.42])
@hypothesis.example(SHAPES_7, SHAPES_8, [0.0, 1.0])
def test_reform_tax_is_finite_and_at_least_tax_without_the_bracket(
    reform_system, thresholds_7, thresholds_8, rates
):
    rate_7, rate_8 = rates
    with_bracket = calculate(
        REFORM_VARIABLES,
        YEAR,
        reform_system,
        reform=added_bracket(thresholds_7, thresholds_8, rate_7, rate_8),
    )
    removed = calculate(
        REFORM_VARIABLES,
        YEAR,
        reform_system,
        reform=added_bracket(thresholds_7, thresholds_8, rate_7, rate_7),
    )
    for variable in REFORM_VARIABLES:
        assert np.all(np.isfinite(with_bracket[variable])), variable
        assert np.all(np.isfinite(removed[variable])), variable
    for variable in REFORM_TAXES:
        assert np.all(
            with_bracket[variable] >= removed[variable] - SIMULATION_TOLERANCE
        ), variable
