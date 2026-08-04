"""Test that LSR and CG behavioral responses work together.

When both labor supply responses (LSR) and capital gains (CG) behavioral
responses are enabled, the combined revenue impact should be bounded
between the individual impacts — not orders of magnitude larger.

Fixes #7785.
"""

import os

import pytest
from policyengine_core.reforms import Reform
from policyengine_us import Microsimulation

YEAR = 2026
DATE_RANGE = "2020-01-01.2100-12-31"
# Subsample size for the default dataset. Larger than the 1,000 used in
# test_microsim.py because the reforms here mostly affect top-bracket and
# high-capital-gains households, which a smaller sample can miss entirely.
# subsample() seeds from the dataset name, so every simulation in this
# module draws the same households and the impacts stay comparable; the
# assertions are ratio-based, so they are subsample-scale-free.
SUBSAMPLE_SIZE = 10_000


def _federal_tax(reform_tuple=None):
    """Total federal income tax on a fixed subsample, optionally reformed."""
    sim = Microsimulation(reform=reform_tuple)
    sim.subsample(SUBSAMPLE_SIZE)
    return float(sim.calculate("income_tax", period=YEAR, map_to="household").sum())


def _make_tax_reform():
    """Create a simple tax reform that changes rates enough to trigger
    behavioral responses — raise the top bracket rate by 10pp."""
    return Reform.from_dict(
        {
            "gov.irs.income.bracket.rates.7": {
                DATE_RANGE: 0.47,
            },
        },
        country_id="us",
    )


def _make_lsr_reform():
    """Create CBO labor supply response reform."""
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
    """Create capital gains behavioral response reform."""
    return Reform.from_dict(
        {
            "gov.simulation.capital_gains_responses.elasticity": {
                DATE_RANGE: -0.62,
            },
        },
        country_id="us",
    )


def _make_watca_reform():
    """Create WATCA structural reform (overrides taxable_income and
    income_tax_before_credits variables)."""
    from policyengine_us.reforms.congress.watca.working_americans_tax_cut_act import (
        create_watca,
    )

    structural = create_watca()
    params = Reform.from_dict(
        {
            "gov.contrib.congress.watca.in_effect": {DATE_RANGE: True},
            "gov.contrib.congress.watca.surtax.in_effect": {DATE_RANGE: True},
        },
        country_id="us",
    )
    return (structural, params)


def _assert_combined_bounded(reform_tuple, label):
    """Assert combined LSR+CG impact is bounded for a given reform."""
    lsr = _make_lsr_reform()
    cg = _make_cg_reform()

    # The deterministic subsample makes the baseline identical for all
    # three impacts, so compute it once.
    tax_baseline = _federal_tax()
    impact_lsr = _federal_tax(reform_tuple + (lsr,)) - tax_baseline
    impact_cg = _federal_tax(reform_tuple + (cg,)) - tax_baseline
    impact_both = _federal_tax(reform_tuple + (lsr, cg)) - tax_baseline

    individual_sum = abs(impact_lsr) + abs(impact_cg)
    assert abs(impact_both) < 3 * individual_sum, (
        f"[{label}] Combined LSR+CG impact (${impact_both / 1e9:.1f}B) is "
        f"more than 3x the sum of individual impacts "
        f"(LSR=${impact_lsr / 1e9:.1f}B + CG=${impact_cg / 1e9:.1f}B"
        f" = ${individual_sum / 1e9:.1f}B). "
        f"This suggests a compounding feedback bug. See #7785."
    )


@pytest.mark.skipif(
    os.environ.get("RUN_HEAVY_TESTS") != "1",
    reason="Heavy: builds 4 default-dataset microsimulations; set RUN_HEAVY_TESTS=1",
)
def test_combined_lsr_cg_parametric_reform():
    """Parameter-only reform: combined LSR+CG should be bounded."""
    _assert_combined_bounded((_make_tax_reform(),), "parametric")


@pytest.mark.skipif(
    os.environ.get("RUN_HEAVY_TESTS") != "1",
    reason="Heavy: builds 4 default-dataset microsimulations; set RUN_HEAVY_TESTS=1",
)
def test_combined_lsr_cg_structural_reform():
    """Structural reform (WATCA): combined LSR+CG should be bounded.

    WATCA overrides taxable_income and income_tax_before_credits.
    This tests that behavioral responses work correctly even when
    the reform uses variable overrides, not just parameter changes.
    """
    _assert_combined_bounded(_make_watca_reform(), "WATCA structural")
