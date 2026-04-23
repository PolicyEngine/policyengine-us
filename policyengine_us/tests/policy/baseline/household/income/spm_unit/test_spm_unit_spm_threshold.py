"""Regression tests for the spm_unit_spm_threshold formula.

Verifies that:
1. Historical published years (2015-2024) match the Census Bureau's
   published Betson reference thresholds exactly (via spm-calculator).
2. Post-published years uprate via PolicyEngine's ``gov.bls.cpi.cpi_u``
   parameter.
3. Composition and tenure changes between periods flow through to the
   threshold while preserving the unit-specific geographic adjustment
   implied by the prior-year stored threshold.
4. The Betson three-parameter equivalence scale is applied (a 2A2C
   reference family at the renter national base equals 39430 in 2024).
"""

import numpy as np
import pytest
from policyengine_us import Simulation
from policyengine_us.variables.household.income.spm_unit.spm_unit_spm_threshold import (
    LATEST_PUBLISHED_SPM_THRESHOLD_YEAR,
    _reference_threshold_array,
)
from policyengine_us.variables.household.income.spm_unit.spm_unit_tenure_type import (
    SPMUnitTenureType,
)
from spm_calculator.equivalence_scale import spm_equivalence_scale
from spm_calculator.forecast import HISTORICAL_THRESHOLDS


def _cpi_u():
    from policyengine_us import CountryTaxBenefitSystem

    return CountryTaxBenefitSystem().parameters.gov.bls.cpi.cpi_u


def test_reference_threshold_matches_census_for_published_years():
    """The per-tenure reference threshold must equal the Census BLS
    published value for every year spm-calculator has on record."""
    cpi_u = _cpi_u()
    for year, expected in HISTORICAL_THRESHOLDS.items():
        for tenure_enum, key in [
            (SPMUnitTenureType.RENTER, "renter"),
            (SPMUnitTenureType.OWNER_WITH_MORTGAGE, "owner_with_mortgage"),
            (
                SPMUnitTenureType.OWNER_WITHOUT_MORTGAGE,
                "owner_without_mortgage",
            ),
        ]:
            got = _reference_threshold_array(
                np.array([tenure_enum]),
                year,
                cpi_u,
            )[0]
            assert got == expected[key], (
                f"{year} {key}: got {got}, expected {expected[key]}"
            )


def test_reference_threshold_uprates_with_cpi_u_past_latest_published():
    """Post-2024 reference threshold must equal the latest published
    value scaled by PolicyEngine's CPI-U ratio."""
    cpi_u = _cpi_u()
    latest = LATEST_PUBLISHED_SPM_THRESHOLD_YEAR
    target_year = latest + 2
    factor = float(cpi_u(f"{target_year}-02-01") / cpi_u(f"{latest}-02-01"))
    published_renter = HISTORICAL_THRESHOLDS[latest]["renter"]
    got = _reference_threshold_array(
        np.array([SPMUnitTenureType.RENTER]),
        target_year,
        cpi_u,
    )[0]
    assert got == published_renter * factor


def test_formula_respects_composition_change_between_years():
    """When a child ages into adulthood between the prior and current
    period, the threshold must rescale by the Betson equivalence-scale
    ratio (current composition / prior composition)."""
    YEAR = 2026
    PRIOR = 2025

    # Build a simulation where person "teen" is 17 (child) in PRIOR and
    # 18 (adult) in YEAR, converting the SPM unit from 2A2C to 3A1C.
    # Calibrate the prior stored threshold so the implied geoadj is
    # exactly 1.0; the current threshold must then be
    # current_base * current_equiv.
    cpi_u = _cpi_u()
    prior_base = _reference_threshold_array(
        np.array([SPMUnitTenureType.RENTER]),
        PRIOR,
        cpi_u,
    )[0]
    current_base = _reference_threshold_array(
        np.array([SPMUnitTenureType.RENTER]),
        YEAR,
        cpi_u,
    )[0]
    prior_equiv = spm_equivalence_scale(2, 2)  # 2A2C in PRIOR
    current_equiv = spm_equivalence_scale(3, 1)  # teen is adult in YEAR

    situation = {
        "people": {
            "adult1": {"age": {PRIOR: 40, YEAR: 41}},
            "adult2": {"age": {PRIOR: 40, YEAR: 41}},
            "teen": {"age": {PRIOR: 17, YEAR: 18}},
            "child": {"age": {PRIOR: 5, YEAR: 6}},
        },
        "spm_units": {
            "spm_unit": {
                "members": ["adult1", "adult2", "teen", "child"],
                "spm_unit_spm_threshold": {
                    PRIOR: float(prior_base * prior_equiv),
                },
                "spm_unit_tenure_type": {
                    PRIOR: "RENTER",
                    YEAR: "RENTER",
                },
            }
        },
    }

    sim = Simulation(situation=situation)
    expected = current_base * current_equiv
    got = float(sim.calculate("spm_unit_spm_threshold", YEAR)[0])
    assert got == pytest.approx(expected, rel=1e-4)


def test_formula_preserves_implied_geographic_adjustment():
    """A prior-year threshold 1.5x the national base should produce a
    current-year threshold 1.5x the current national base, all else
    equal."""
    YEAR = 2026
    PRIOR = 2025
    GEOADJ = 1.5

    cpi_u = _cpi_u()
    prior_base = _reference_threshold_array(
        np.array([SPMUnitTenureType.RENTER]),
        PRIOR,
        cpi_u,
    )[0]
    current_base = _reference_threshold_array(
        np.array([SPMUnitTenureType.RENTER]),
        YEAR,
        cpi_u,
    )[0]
    equiv = spm_equivalence_scale(2, 2)

    situation = {
        "people": {
            "a1": {"age": {PRIOR: 40, YEAR: 41}},
            "a2": {"age": {PRIOR: 40, YEAR: 41}},
            "k1": {"age": {PRIOR: 5, YEAR: 6}},
            "k2": {"age": {PRIOR: 3, YEAR: 4}},
        },
        "spm_units": {
            "spm_unit": {
                "members": ["a1", "a2", "k1", "k2"],
                "spm_unit_spm_threshold": {
                    PRIOR: float(prior_base * equiv * GEOADJ),
                },
                "spm_unit_tenure_type": {
                    PRIOR: "RENTER",
                    YEAR: "RENTER",
                },
            }
        },
    }

    sim = Simulation(situation=situation)
    got = float(sim.calculate("spm_unit_spm_threshold", YEAR)[0])
    expected = current_base * equiv * GEOADJ
    assert got == pytest.approx(expected, rel=1e-5)
