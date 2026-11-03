"""Properties of the ACA applicable percentage table.

`aca_required_contribution_percentage` is the applicable percentage of
26 U.S.C. 36B(b)(3)(A): within each income tier of the table it rises "on a
sliding scale in a linear manner" from the tier's initial percentage to its
final percentage (26 CFR 1.36B-3(g)(1)). The IRS indexes the table each year;
Rev. Proc. 2026-26 sets it for 2027. Hypothesis draws incomes as fractions of
the poverty line from 0 to 400 percent. Each drawn example is one simulation,
calculated for every year from 2018 through 2027 against that year's table.
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
   rises with income up to 400 percent (checked for 2026 and 2027, from income
   in dollars through the poverty-line fraction).

Why Python: the YAML cases pin the 2027 table at chosen points; this checks
every year's table at its edges and at drawn incomes, so a mistyped edge, an
interpolation that runs past a tier's final percentage, or a new table row
entered in the wrong order fails wherever it falls. Cost, measured
locally (macOS, shared host): about 6 s of test calls, 12 s in pytest and 36 s
wall time including the model import, peak memory footprint 1.7 GB. It runs in
the `core` group of the rest Python tests.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEARS = tuple(range(2018, 2028))
CONTRIBUTION_YEARS = (2026, 2027)
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


def build(tax_unit_inputs, years):
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


@settings(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    # Fixed incomes in four tiers, so every example compares distinct incomes.
    st.lists(st.integers(0, 70_000), max_size=60).map(
        lambda drawn: sorted([10_000, 25_000, 40_000, 60_000, *drawn])
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
    income = np.array(incomes, dtype=float)
    for year in CONTRIBUTION_YEARS:
        fraction = np.asarray(simulation.calculate("aca_magi_fraction", year))
        rate = np.asarray(
            simulation.calculate("aca_required_contribution_percentage", year)
        )
        credit = np.asarray(simulation.calculate("aca_ptc_before_filing_gate", year))
        within = fraction <= 4
        contribution = (income * rate)[within]
        # Property 4.
        assert (np.diff(contribution) >= -1e-6).all(), year
        assert (np.diff(credit[within]) <= 1e-6).all(), year
