"""Regression tests for the Oregon Kids' Credit sunset (issue #9074).

HB 3235 (2023) Section 11 limits the credit to tax years beginning on or
after January 1, 2023, and before January 1, 2029. The sunset is encoded
solely in ``gov.states.or.tax.income.credits.ctc.in_effect`` (the credit
stays in the refundable-credits list), so a single parameter switch models
renewal scenarios.
"""

import math

from policyengine_core.periods import instant
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
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
    residue and drift low by $50 steps. Expected values are derived from the
    raw CPI-U parameter directly — the annual projection point stored at the
    February instant ahead of each tax year — independently of the COLA
    helper, so a window bug in the helper cannot hide here.
    """
    cpi = system.parameters.gov.bls.cpi.cpi_u
    q2_2022 = sum(cpi(f"2022-{month:02d}-01") for month in (4, 5, 6)) / 3
    for year in (2027, 2028, 2040):
        cola = max(cpi(f"{year - 1}-02-01") / q2_2022 - 1, 0)
        expected_amount = 1_000 + math.floor(1_000 * cola / 50) * 50
        expected_start = 25_000 + math.floor(25_000 * cola / 50) * 50
        assert OR_CTC_PARAMS.amount(f"{year}-01-01") == expected_amount
        assert OR_CTC_PARAMS.reduction.start(f"{year}-01-01") == expected_start
