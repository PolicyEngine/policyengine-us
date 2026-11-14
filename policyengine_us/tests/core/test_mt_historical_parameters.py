"""Check Montana's 2017-2020 Form 2 amounts at their calculation boundaries.

Each rate schedule must match the sum of its published marginal brackets.
Standard deductions stay within the year's limits and increase with AGI.
Pension exemptions stay between zero and the year's cap and decrease with
federal AGI above the year's threshold. All five filing statuses use the
same pre-2024 rate schedule. Existing surviving-spouse deduction limits
remain unchanged.

Sources: Montana Department of Revenue Form 2 instructions for 2017-2020,
PDF pages 11, 13, 14 and 13 (tax and personal exemptions); PDF pages 23, 25,
30 and 27 (pension exemptions); and the 2021 instructions, PDF page 54
(historical standard deduction limits).
"""

import numpy as np
from hypothesis import given, settings, strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

# Year: exemption, single standard floor/cap, pension cap/threshold, brackets.
HISTORY = {
    2017: (
        2_400,
        2_000,
        4_510,
        4_110,
        34_260,
        (2_900, 5_200, 7_900, 10_600, 13_600, 17_600),
    ),
    2018: (
        2_440,
        2_030,
        4_580,
        4_180,
        34_820,
        (3_000, 5_200, 8_000, 10_800, 13_900, 17_900),
    ),
    2019: (
        2_510,
        2_090,
        4_710,
        4_300,
        35_800,
        (3_100, 5_400, 8_200, 11_100, 14_300, 18_400),
    ),
    2020: (
        2_560,
        2_130,
        4_790,
        4_370,
        36_420,
        (3_100, 5_500, 8_400, 11_300, 14_500, 18_700),
    ),
}
RATES = (0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.069)
STATUSES = ("SINGLE", "SEPARATE", "JOINT", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE")


def _bracket_tax(incomes, thresholds):
    tax = np.zeros_like(incomes, dtype=float)
    edges = (0, *thresholds, np.inf)
    for lower, upper, rate in zip(edges, edges[1:], RATES):
        tax += np.maximum(np.minimum(incomes, upper) - lower, 0) * rate
    return tax


@settings(max_examples=4, deadline=None, derandomize=True)
@given(income=st.integers(min_value=0, max_value=300_000))
def test_historical_schedules_match_published_brackets(income):
    for year, (_, floor, cap, _, _, thresholds) in HISTORY.items():
        p = system.parameters(f"{year}-01-01").gov.states.mt.tax.income
        points = np.array([income, *[t + d for t in thresholds for d in (-1, 0, 1)]])
        expected = _bracket_tax(points, thresholds)
        for status in STATUSES:
            actual = getattr(p.main, status.lower()).calc(points)
            np.testing.assert_allclose(actual, expected, atol=0.001, rtol=0)
            multiple = 2 if status in ("JOINT", "HEAD_OF_HOUSEHOLD") else 1
            assert getattr(p.deductions.standard.floor, status) == multiple * floor
            assert getattr(p.deductions.standard.cap, status) == multiple * cap
        assert p.married_filing_separately_on_same_return_allowed
        assert p.exemptions.amount == HISTORY[year][0]


@settings(max_examples=4, deadline=None, derandomize=True)
@given(agi=st.integers(min_value=0, max_value=100_000))
def test_historical_deduction_and_pension_boundaries(agi):
    points_by_year = {}
    for year, (_, floor, cap, pension_cap, threshold, _) in HISTORY.items():
        # Keep duplicates so every year uses the same entity count.
        points_by_year[year] = sorted(
            [
                agi,
                *[floor * 5 + d for d in (-1, 0, 1)],
                *[cap * 5 + d for d in (-1, 0, 1)],
                *[threshold + d for d in (-1, 0, 1)],
                *[threshold + pension_cap / 2 + d for d in (-1, 0, 1)],
            ]
        )

    people, tax_units, households = {}, {}, {}
    for index in range(len(next(iter(points_by_year.values())))):
        name = f"person_{index}"
        incomes = {year: points[index] for year, points in points_by_year.items()}
        people[name] = {
            "age": {year: 40 for year in HISTORY},
            "is_tax_unit_head": {year: True for year in HISTORY},
            "mt_agi_indiv": incomes,
            "adjusted_gross_income_person": incomes,
            "taxable_pension_income": {year: 10_000 for year in HISTORY},
        }
        tax_units[name] = {"members": [name]}
        households[name] = {
            "members": [name],
            "state_code": {year: "MT" for year in HISTORY},
        }
    simulation = Simulation(
        tax_benefit_system=system,
        situation={"people": people, "tax_units": tax_units, "households": households},
    )

    for year, (_, floor, cap, pension_cap, threshold, _) in HISTORY.items():
        points = np.asarray(points_by_year[year])
        deduction = simulation.calculate("mt_standard_deduction_indiv", year)
        expected_deduction = np.clip(0.2 * points, floor, cap)
        np.testing.assert_allclose(deduction, expected_deduction, atol=0.01, rtol=0)
        assert np.all((deduction >= floor) & (deduction <= cap))
        assert np.all(np.diff(deduction) >= -0.01)
        pension = simulation.calculate("mt_pension_exemption_indiv", year)
        expected_pension = np.maximum(
            pension_cap - 2 * np.maximum(points - threshold, 0), 0
        )
        np.testing.assert_allclose(pension, expected_pension, atol=0.01, rtol=0)
        assert np.all((pension >= 0) & (pension <= pension_cap))
        assert np.all(np.diff(pension) <= 0.01)


@settings(max_examples=4, deadline=None, derandomize=True)
@given(amount=st.integers(min_value=0, max_value=800))
def test_historical_subtractions_include_each_existing_component(amount):
    amounts = {year: amount for year in HISTORY}
    simulation = Simulation(
        tax_benefit_system=system,
        situation={
            "people": {
                "head": {
                    "mt_interest_exemption_person": amounts,
                    "us_govt_interest_person": amounts,
                    "mt_tuition_subtraction_person": amounts,
                    "salt_refund_income": amounts,
                }
            },
            "tax_units": {"unit": {"members": ["head"]}},
            "households": {
                "household": {
                    "members": ["head"],
                    "state_code": {year: "MT" for year in HISTORY},
                }
            },
        },
    )
    for year in HISTORY:
        assert simulation.calculate("mt_subtractions", year)[0] == 4 * amount
