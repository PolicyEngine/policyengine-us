"""Properties of the ACA applicable percentage table.

`aca_required_contribution_percentage` is the applicable percentage of
26 U.S.C. 36B(b)(3)(A): within each income tier of the table it rises "on a
sliding scale in a linear manner" from the tier's initial percentage to its
final percentage (26 CFR 1.36B-3(g)(1)). The IRS indexes the table each year;
Rev. Proc. 2026-26 sets it for 2027. Hypothesis draws incomes as fractions of
the poverty line from 0 to 400 percent. Each drawn example is one simulation,
calculated for every year from 2014 through 2027 against that year's table.
For every year:

1. At each tier's lower edge the percentage equals the tier's initial
   percentage, and at exactly 400 percent it equals the top tier's final
   percentage.
2. Within a tier the percentage is the straight line from the tier's initial
   to its final percentage, which is continuous, rounded to the nearest
   hundredth of a percent (26 CFR 1.36B-3(g)(1)). So it stays between the
   tier's initial and final percentages, it reaches the final percentage just
   below the next edge, and at every income it is within half a rounding step
   of the line. The bound holds whether or not the model rounds.
3. The percentage never decreases as income rises from 0 to 400 percent,
   including across tier edges. Before rounding, its only jumps are at tier
   edges; rounding adds steps of 0.01 percentage point.
4. The required contribution (household income times the percentage) never
   decreases as income rises, so for a fixed benchmark premium the credit never
   rises with income up to 400 percent (checked for 2014–2017, 2026 and 2027, from
   income in dollars through the poverty-line fraction).
5. In 2014–2017 the credit stays between zero and the benchmark premium,
   including supplied negative MAGI. Later years retain that bound for
   nonnegative MAGI and preserve their existing negative-input arithmetic.
6. From 2018 through 2027, percentages and credits match the tables and
   calculation used before historical coverage.

Why Python: the YAML cases pin annual tables at chosen points; this checks
every year's table at its edges and at drawn incomes, so a mistyped edge, an
interpolation that runs past a tier's final percentage, or a new table row
entered in the wrong order fails wherever it falls. The compatibility check
compares against a frozen copy of the existing tables and detects historical
entries leaking into later years.
These tests run in the `core` group of the rest Python tests.
"""

import gc

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEARS = tuple(range(2014, 2028))
CONTRIBUTION_YEARS = (2014, 2015, 2016, 2017, 2026, 2027)
# The model holds incomes and percentages in float32 (about seven significant
# digits), so edges are approached from 1e-5 away and percentages compared to
# within 1e-6.
EPSILON = 1e-5
TOLERANCE = 1e-6
# 26 CFR 1.36B-3(g)(1) rounds the interpolated percentage to the nearest
# hundredth of a percent, which moves it off the line by up to half of 0.0001.
ROUNDING = 1e-4
# Every tier edge in any year's table, approached from both sides.
EDGES = (0.0, 1.33, 1.5, 2.0, 2.5, 3.0, 4.0)
KNOTS = sorted(
    {
        min(max(edge + offset, 0.0), 4.0)
        for edge in EDGES
        for offset in (-EPSILON, 0.0, EPSILON)
    }
)

fractions = st.lists(
    st.one_of(
        st.floats(0, 4, allow_nan=False, allow_infinity=False),
        # Whole percents, as aca_magi_fraction produces from income.
        st.integers(0, 400).map(lambda percent: percent / 100),
    ),
    min_size=1,
    max_size=60,
)


def clear_parameter_caches(system):
    root = system.parameters
    system._parameters_at_instant_cache.clear()
    for node in (root, *root.get_descendants()):
        cache = getattr(node, "_at_instant_cache", None)
        if cache is not None:
            cache.clear()


@pytest.fixture(autouse=True)
def clear_shared_parameter_caches():
    # Monthly benchmark reads cache snapshots of the entire parameter tree.
    system = Simulation.default_tax_benefit_system_instance
    clear_parameter_caches(system)
    yield
    clear_parameter_caches(system)
    gc.collect()


def build(tax_unit_inputs, years):
    # Collect simulation reference cycles between generated cases.
    gc.collect()
    people, tax_units, households = {}, {}, {}
    groups = {"marital_units": {}, "spm_units": {}, "families": {}}
    for index, inputs in enumerate(tax_unit_inputs):
        person, members = f"person_{index}", [f"person_{index}"]
        people[person] = {
            "age": {year: 40 for year in years},
            "is_aca_ptc_eligible": {year: True for year in years},
        }
        tax_units[f"tax_unit_{index}"] = {
            "members": members,
            **{name: {year: value for year in years} for name, value in inputs.items()},
        }
        households[f"household_{index}"] = {
            "members": members,
            "state_code": {year: "TX" for year in years},
        }
        for name in groups:
            groups[name][f"{name}_{index}"] = {"members": members}
    return Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
            **groups,
        }
    )


def table(simulation, year):
    p = simulation.tax_benefit_system.parameters(
        f"{year}-01-01"
    ).gov.aca.required_contribution_percentage
    return np.array(p.threshold), np.array(p.initial), np.array(p.final)


@settings(
    max_examples=8,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(fractions.map(lambda drawn: sorted(KNOTS + drawn)))
def test_applicable_percentage_table(points):
    simulation = build([{"aca_magi_fraction": x} for x in points], YEARS)
    try:
        x = np.array(points)
        # The fractions the model sees, after float32 storage.
        seen = x.astype(np.float32).astype(float)
        for year in YEARS:
            thresholds, initial, final = table(simulation, year)
            # Every edge is probed; a new or mistyped edge must be added to EDGES.
            assert set(thresholds) <= set(EDGES), (year, thresholds)
            rate = np.asarray(
                simulation.calculate("aca_required_contribution_percentage", year)
            )
            # Property 1.
            for tier, edge in enumerate(thresholds[:-1]):
                np.testing.assert_allclose(
                    rate[x == edge], initial[tier], atol=TOLERANCE, err_msg=str(year)
                )
            np.testing.assert_allclose(
                rate[x == thresholds[-1]], final[-1], atol=TOLERANCE, err_msg=str(year)
            )
            # Property 2.
            tier = np.clip(
                np.searchsorted(thresholds, seen, side="right") - 1, 0, len(initial) - 1
            )
            slope = (final - initial) / np.diff(thresholds)
            assert (rate >= initial[tier] - TOLERANCE).all(), year
            assert (rate <= final[tier] + TOLERANCE).all(), year
            for upper, top, rise in zip(thresholds[1:], final, slope):
                below = rate[x == upper - EPSILON]
                assert (top - below >= -TOLERANCE).all(), year
                assert (top - below <= rise * EPSILON + TOLERANCE).all(), year
            line = initial[tier] + slope[tier] * (seen - thresholds[tier])
            assert (np.abs(rate - line) <= ROUNDING / 2 + TOLERANCE).all(), year
            # Property 3.
            assert (np.diff(rate) >= -TOLERANCE).all(), year
    finally:
        del simulation
        gc.collect()


@settings(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    # Fixed incomes in four tiers, so every example compares distinct incomes.
    st.lists(st.integers(-20_000, 70_000), max_size=60).map(
        lambda drawn: sorted([-1_000, 0, 10_000, 25_000, 40_000, 60_000, *drawn])
    ),
    st.integers(1_000, 20_000),
)
def test_required_contribution_rises_with_income(incomes, slcsp):
    simulation = build(
        [
            {"aca_magi": income, "slcsp": slcsp, "tax_unit_is_filer": True}
            for income in incomes
        ],
        CONTRIBUTION_YEARS,
    )
    try:
        income = np.array(incomes, dtype=float)
        for year in CONTRIBUTION_YEARS:
            fraction = np.asarray(simulation.calculate("aca_magi_fraction", year))
            rate = np.asarray(
                simulation.calculate("aca_required_contribution_percentage", year)
            )
            credit = np.asarray(
                simulation.calculate("aca_ptc_before_filing_gate", year)
            )
            benchmark = np.asarray(simulation.calculate("slcsp", year))
            # Property 5 also covers the zero floor outside the income range.
            assert (credit >= 0).all(), year
            bounded = np.ones(len(income), dtype=bool) if year < 2018 else income >= 0
            assert (credit[bounded] <= benchmark[bounded] + 1e-6).all(), year
            within = fraction <= 4
            contribution_income = np.maximum(income, 0) if year < 2018 else income
            contribution = (contribution_income * rate)[within]
            # Property 4.
            assert (np.diff(contribution) >= -1e-6).all(), year
            assert (np.diff(credit[within]) <= 1e-6).all(), year
    finally:
        del simulation
        gc.collect()


# Freeze the tables used before extending historical coverage. Repeated knots
# let numpy.interp retain the jump at 133 percent without sharing the model's
# bracket-selection implementation.
POST_2017_TABLES = {
    2018: (
        [0.0201, 0.0302, 0.0403, 0.0634, 0.081, 0.0956],
        [0.0201, 0.0403, 0.0634, 0.081, 0.0956, 0.0956],
    ),
    2019: (
        [0.0208, 0.0311, 0.0415, 0.0654, 0.0836, 0.0986],
        [0.0208, 0.0415, 0.0654, 0.0836, 0.0986, 0.0986],
    ),
    2020: (
        [0.0206, 0.0309, 0.0412, 0.0649, 0.0829, 0.0978],
        [0.0206, 0.0412, 0.0649, 0.0829, 0.0978, 0.0978],
    ),
    **{
        year: ([0, 0, 0.02, 0.04, 0.06], [0, 0.02, 0.04, 0.06, 0.085])
        for year in range(2021, 2026)
    },
    2026: (
        [0.021, 0.0314, 0.0419, 0.066, 0.0844, 0.0996],
        [0.021, 0.0419, 0.066, 0.0844, 0.0996, 0.0996],
    ),
    2027: (
        [0.0215, 0.0323, 0.043, 0.0678, 0.0866, 0.1022],
        [0.0215, 0.043, 0.0678, 0.0866, 0.1022, 0.1022],
    ),
}


@settings(
    max_examples=4,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    st.lists(
        st.tuples(
            st.floats(0, 6, allow_nan=False, allow_infinity=False),
            st.integers(-20_000, 120_000),
            st.integers(0, 30_000),
        ),
        min_size=1,
        max_size=24,
    )
)
def test_post_2017_credit_matches_existing_rules(drawn):
    rows = [(edge, 30_000, 12_000) for edge in [*KNOTS, 4.01, 5.0]]
    rows += [(0, -1_000, 12_000), *drawn]
    simulation = build(
        [
            {
                "aca_magi_fraction": fraction,
                "aca_magi": income,
                "slcsp": premium,
                "tax_unit_is_filer": True,
            }
            for fraction, income, premium in rows
        ],
        tuple(POST_2017_TABLES),
    )
    try:
        fractions, incomes, premiums = np.array(rows, dtype=np.float32).T
        for year, (initial, final) in POST_2017_TABLES.items():
            thresholds = [0, 1.5, 2, 2.5, 3, 4]
            if not 2021 <= year <= 2025:
                thresholds.insert(1, 1.33)
            knots = np.repeat(thresholds, 2)[1:-1]
            expected_rate = np.interp(
                fractions, knots, np.column_stack((initial, final)).ravel()
            )
            if not 2021 <= year <= 2025:
                expected_rate = np.where(fractions > 4, 0, expected_rate)
            rate = simulation.calculate("aca_required_contribution_percentage", year)
            np.testing.assert_allclose(
                rate, expected_rate, atol=TOLERANCE, err_msg=str(year)
            )
            expected_credit = np.maximum(0, premiums - incomes * expected_rate)
            for variable in ("aca_ptc_before_filing_gate", "aca_ptc"):
                credit = simulation.calculate(variable, year)
                np.testing.assert_allclose(
                    credit,
                    expected_credit,
                    rtol=1e-6,
                    atol=0.02,
                    err_msg=f"{year}: {variable}",
                )
            clear_parameter_caches(simulation.tax_benefit_system)
            gc.collect()
    finally:
        del simulation
        gc.collect()
