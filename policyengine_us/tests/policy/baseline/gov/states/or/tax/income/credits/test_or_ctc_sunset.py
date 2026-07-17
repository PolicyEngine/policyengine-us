"""Regression tests for the Oregon Kids' Credit sunset (issue #9074).

HB 3235 (2023) Section 11 limits the credit to tax years beginning on or
after January 1, 2023, and before January 1, 2029. The sunset is encoded
solely in ``gov.states.or.tax.income.credits.ctc.in_effect`` (the credit
stays in the refundable-credits list), so a single parameter switch models
renewal scenarios.
"""

import math
from types import SimpleNamespace

import pytest

from policyengine_core.parameters import Parameter
from policyengine_core.periods import instant
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.parameters.uprating_extensions import get_or_ctc_cola
from policyengine_us.system import system


OR_CTC_PARAMS = system.parameters.gov.states.children["or"].tax.income.credits.ctc

SITUATION = {
    "people": {
        "parent": {"age": {"2028": 30, "2029": 31}},
        "child1": {"age": {"2028": 2, "2029": 3}},
        "child2": {"age": {"2028": 4, "2029": 5}},
    },
    "tax_units": {
        "tax_unit": {
            "members": ["parent", "child1", "child2"],
            "or_agi": {"2028": 10_000, "2029": 10_000},
        }
    },
    "households": {
        "household": {
            "members": ["parent", "child1", "child2"],
            "state_code": {"2028": "OR", "2029": "OR"},
        }
    },
}


def _renew_in_effect_from_2029():
    """A reform flipping only the in_effect switch back on from 2029."""

    class RenewFrom2029(Reform):
        def apply(self):
            def modify(parameters):
                node = parameters
                path = "gov.states.or.tax.income.credits.ctc.in_effect"
                for part in path.split("."):
                    node = getattr(node, part)
                node.update(
                    start=instant("2029-01-01"),
                    stop=instant("2100-12-31"),
                    value=True,
                )
                return parameters

            self.modify_parameters(modify)

    return RenewFrom2029


def test_or_ctc_pays_through_2028_and_stops_in_2029():
    sim = Simulation(situation=SITUATION)
    assert sim.calculate("or_ctc", 2028)[0] > 0
    assert sim.calculate("or_ctc", 2029)[0] == 0
    # The credit also drops out of the refundable-credit total (the family
    # qualifies for no other Oregon refundable credit).
    assert sim.calculate("or_refundable_credits", 2028)[0] > 0
    assert sim.calculate("or_refundable_credits", 2029)[0] == 0


def test_in_effect_reform_restores_the_credit_from_2029():
    sim = Simulation(situation=SITUATION, reform=_renew_in_effect_from_2029())
    p = sim.tax_benefit_system.parameters("2029-01-01")
    amount = p.gov.states["or"].tax.income.credits.ctc.amount
    expected = 2 * amount
    result = sim.calculate("or_ctc", 2029)[0]
    assert result == expected
    assert result > 0
    # The renewed credit flows through the refundable-credits list.
    assert sim.calculate("or_refundable_credits", 2029)[0] == expected


def test_statutory_cola_matches_published_and_determined_values():
    """ORS 315.273(5) values for published and CPI-determined years.

    2024 and 2025 are Department of Revenue published values (OR-40
    instructions). Tax year 2026 is already determined by published CPI-U:
    the window ending August 2025 averages 319.24, a 9.114% COLA over the
    2022 Q2 base of 292.572, so the $91.14 amount increase floors to $50
    (no change at the $50 grid: $1,000 base + $50 = $1,050) and the
    $2,278.47 threshold increase floors to $2,250.
    """
    assert OR_CTC_PARAMS.amount("2024-01-01") == 1_000
    assert OR_CTC_PARAMS.reduction.start("2024-01-01") == 25_750
    assert OR_CTC_PARAMS.amount("2025-01-01") == 1_050
    assert OR_CTC_PARAMS.reduction.start("2025-01-01") == 26_550
    assert OR_CTC_PARAMS.amount("2026-01-01") == 1_050
    assert OR_CTC_PARAMS.reduction.start("2026-01-01") == 27_250


def test_projections_compute_from_statutory_bases_not_chained():
    """Projected years recompute from the $1,000 / $25,000 bases.

    ORS 315.273(5) applies the COLA to the statutory base amounts each year;
    chaining from a later rounded value would permanently discard rounding
    residue and drift low by $50 steps. The COLA helper's window semantics
    are pinned independently, on fixed synthetic series, by the
    test_cola_* cases below.
    """
    for year in (2027, 2028, 2040):
        cola = get_or_ctc_cola(system.parameters, year)
        expected_amount = 1_000 + math.floor(1_000 * cola / 50) * 50
        expected_start = 25_000 + math.floor(25_000 * cola / 50) * 50
        assert OR_CTC_PARAMS.amount(f"{year}-01-01") == expected_amount
        assert OR_CTC_PARAMS.reduction.start(f"{year}-01-01") == expected_start


def _cola_on_series(values, tax_year):
    """Run the COLA helper against a synthetic CPI-U series."""
    cpi_u = Parameter("cpi_u", data=dict(values))
    bls = SimpleNamespace(cpi=SimpleNamespace(cpi_u=cpi_u))
    parameters = SimpleNamespace(gov=SimpleNamespace(bls=bls))
    return get_or_ctc_cola(parameters, tax_year)


def _monthly(values, start_year, start_month, end_year, end_month, level):
    year, month = start_year, start_month
    while (year, month) <= (end_year, end_month):
        values[f"{year}-{month:02d}-01"] = level
        month += 1
        if month == 13:
            year, month = year + 1, 1


# A synthetic mirror of the live series shape: 2022 Q2 base months averaging
# 300, monthly observations through August 2025, then annual projection
# points at February instants.
def _base_series():
    values = {"2022-04-01": 297, "2022-05-01": 300, "2022-06-01": 303}
    _monthly(values, 2022, 7, 2025, 8, 331)
    values["2026-02-01"] = 347
    values["2027-02-01"] = 361
    return values


def test_cola_fully_observed_window_averages_monthly_data():
    # Tax year 2026 window (September 2024 - August 2025) is fully observed
    # at 331: COLA = 331 / 300 - 1.
    assert _cola_on_series(_base_series(), 2026) == pytest.approx(31 / 300)


def test_cola_unobserved_window_uses_annual_projection_point():
    # Tax year 2027 has no observed months, so the February 2026 annual
    # projection point (347) applies: COLA = 347 / 300 - 1.
    assert _cola_on_series(_base_series(), 2027) == pytest.approx(47 / 300)


def test_cola_partial_window_ignores_overwritten_february_projection():
    # A monthly refresh lands observations for September 2025 - June 2026,
    # overwriting the February 2026 instant (formerly the 347 projection)
    # with the observed 342. The levels are chosen so every algorithm
    # disagrees: the tax year 2027 window averages the ten observed months
    # (five at 330, five at 342) with a flat two-month tail at the last
    # observation (342), giving (5 * 330 + 5 * 342 + 2 * 342) / 12 = 337 and
    # COLA = 37 / 300. Reading the overwritten February instant as an
    # annual projection would instead give 42 / 300 — so this assertion
    # fails against the raw-February-read regression it guards against.
    values = _base_series()
    _monthly(values, 2025, 9, 2026, 1, 330)
    _monthly(values, 2026, 2, 2026, 6, 342)
    assert _cola_on_series(values, 2027) == pytest.approx(37 / 300)
    # Later, fully unobserved windows still read their own projection
    # points: tax year 2028 uses February 2027 (361).
    assert _cola_on_series(values, 2028) == pytest.approx(61 / 300)


def test_cola_observations_ending_on_a_february_stay_conservative():
    # Observations end exactly on February 2026, with the February actual
    # (348) different from the January level (330). February instants
    # cannot be distinguished from projections, so detection conservatively
    # treats January 2026 as the last observation: the tax year 2027 window
    # averages the five observed months at 330 with a flat tail at the
    # January level, giving COLA = 30 / 300. Reading the February instant
    # would instead give 48 / 300, so this assertion proves the February
    # value is not consulted. The completed tax year 2026 window is
    # unaffected.
    values = _base_series()
    _monthly(values, 2025, 9, 2026, 1, 330)
    values["2026-02-01"] = 348
    assert _cola_on_series(values, 2027) == pytest.approx(30 / 300)
    assert _cola_on_series(values, 2026) == pytest.approx(31 / 300)
