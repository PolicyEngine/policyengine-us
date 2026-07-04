"""Test behavioral responses with structural reforms.

Any structural reform that overrides variables in the income tax chain
should produce bounded results when combined with behavioral responses.

This is a unit-level test using a minimal structural reform (adding a
flat $100 surtax) to avoid the full WATCA complexity while still
testing the interaction pattern.

Fixes #7785.
"""

import os

import numpy as np
import pytest
from policyengine_core.reforms import Reform
from policyengine_us import Microsimulation
from policyengine_us.model_api import *

TEST_YEAR = 2026
DATE_RANGE = "2020-01-01.2100-12-31"
# Subsample size for the default dataset. Larger than the 1,000 used in
# test_microsim.py because the surtax and CG reforms here mostly affect
# high-AGI / high-capital-gains households, which a smaller sample can
# miss entirely. subsample() seeds from the dataset name, so every
# simulation in this module draws the same households and the impacts
# stay comparable; the assertions are ratio-based, so they are
# subsample-scale-free.
SUBSAMPLE_SIZE = 10_000


def _make_structural_surtax_reform():
    """Create a minimal structural reform that adds a surtax.

    Overrides income_tax_before_credits to add a flat $1000 surtax
    on AGI above $500k, similar to how WATCA overrides it.
    """

    class income_tax_before_credits(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "income tax before credits with test surtax"
        unit = USD

        def formula(tax_unit, period, parameters):
            base = add(
                tax_unit,
                period,
                [
                    "income_tax_main_rates",
                    "capital_gains_tax",
                    "alternative_minimum_tax",
                ],
            )
            agi = tax_unit("adjusted_gross_income", period)
            surtax = where(agi > 500_000, 1000, 0)
            return base + surtax

    class reform(Reform):
        def apply(self):
            self.update_variable(income_tax_before_credits)

    return reform


def _make_lsr_reform():
    return Reform.from_dict(
        {
            "gov.simulation.labor_supply_responses.elasticities.income": {
                DATE_RANGE: -0.05,
            },
            "gov.simulation.labor_supply_responses.elasticities.substitution.all": {
                DATE_RANGE: 0.25,
            },
        },
        country_id="us",
    )


def _make_cg_reform():
    return Reform.from_dict(
        {
            "gov.simulation.capital_gains_responses.elasticity": {
                DATE_RANGE: -0.62,
            },
        },
        country_id="us",
    )


def _tax(reform_tuple=None):
    """Total federal income tax on a fixed subsample, optionally reformed."""
    sim = Microsimulation(reform=reform_tuple)
    sim.subsample(SUBSAMPLE_SIZE)
    return float(
        sim.calculate("income_tax", period=TEST_YEAR, map_to="household").sum()
    )


@pytest.mark.skipif(
    os.environ.get("RUN_HEAVY_TESTS") != "1",
    reason="Heavy: builds 4 default-dataset microsimulations; set RUN_HEAVY_TESTS=1",
)
def test_structural_reform_with_lsr_and_cg():
    """Structural reform + LSR + CG should produce bounded results."""
    structural = (_make_structural_surtax_reform(),)
    lsr = _make_lsr_reform()
    cg = _make_cg_reform()

    # The deterministic subsample makes the baseline identical for all
    # three impacts, so compute it once.
    tax_baseline = _tax()
    impact_lsr = _tax(structural + (lsr,)) - tax_baseline
    impact_cg = _tax(structural + (cg,)) - tax_baseline
    impact_both = _tax(structural + (lsr, cg)) - tax_baseline

    individual_sum = abs(impact_lsr) + abs(impact_cg)
    assert abs(impact_both) < 3 * individual_sum, (
        f"Combined impact (${impact_both / 1e9:.1f}B) is >3x individual "
        f"sum (${individual_sum / 1e9:.1f}B). See #7785."
    )


@pytest.mark.skipif(
    os.environ.get("RUN_HEAVY_TESTS") != "1",
    reason="Heavy: builds a default-dataset microsimulation; set RUN_HEAVY_TESTS=1",
)
def test_structural_reform_cg_response_bounded():
    """CG response with structural reform should not produce extreme values.

    The CG behavioral response should reduce capital gains by a
    reasonable fraction, not produce values larger than the original.
    """
    structural = (_make_structural_surtax_reform(),)
    cg = _make_cg_reform()

    sim = Microsimulation(reform=structural + (cg,))
    sim.subsample(SUBSAMPLE_SIZE)
    cg_resp = np.array(
        sim.calculate("capital_gains_behavioral_response", period=TEST_YEAR)
    )
    ltcg_before = np.array(
        sim.calculate("long_term_capital_gains_before_response", period=TEST_YEAR)
    )

    # Response should not exceed the original gains in magnitude
    mask = ltcg_before != 0
    if mask.any():
        ratios = np.abs(cg_resp[mask]) / np.abs(ltcg_before[mask])
        max_ratio = ratios.max()
        assert max_ratio < 5, (
            f"CG response/original ratio is {max_ratio:.1f}x — "
            f"response exceeds 5x original gains. See #7785."
        )
