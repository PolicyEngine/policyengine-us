from __future__ import annotations

import pytest

from policyengine_us import CountryTaxBenefitSystem, Simulation

SYSTEM = CountryTaxBenefitSystem()
CPI_U = SYSTEM.parameters.gov.bls.cpi.cpi_u
REFERENCE_THRESHOLDS_2024 = {
    "renter": 39_430.0,
    "owner_with_mortgage": 39_068.0,
    "owner_without_mortgage": 32_586.0,
}


def _equivalence_scale(num_adults: int, num_children: int) -> float:
    reference_raw_scale = 3**0.7

    if num_adults <= 0 and num_children <= 0:
        return 0.0
    if num_children > 0:
        if num_adults <= 1:
            raw = (1.0 + 0.8 + 0.5 * max(num_children - 1, 0)) ** 0.7
        else:
            raw = (num_adults + 0.5 * num_children) ** 0.7
    else:
        if num_adults <= 1:
            raw = 1.0
        elif num_adults == 2:
            raw = 1.41
        else:
            raw = num_adults**0.7
    return raw / reference_raw_scale


def _future_base_threshold(tenure: str, year: int) -> float:
    return REFERENCE_THRESHOLDS_2024[tenure] * float(
        CPI_U(f"{year}-02-01") / CPI_U("2024-02-01")
    )


def _make_simulation(spm_unit_fields: dict, people: dict) -> Simulation:
    return Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": people,
            "households": {
                "household": {
                    "members": list(people.keys()),
                },
            },
            "tax_units": {
                "tax_unit": {
                    "members": list(people.keys()),
                },
            },
            "spm_units": {
                "spm_unit": {
                    "members": list(people.keys()),
                    **spm_unit_fields,
                },
            },
            "families": {
                "family": {
                    "members": list(people.keys()),
                },
            },
            "marital_units": {
                "marital_unit": {
                    "members": list(people.keys()),
                },
            },
        },
    )


def test_spm_threshold_recomputes_when_child_ages_into_adulthood():
    baseline_threshold = 40_000.0
    sim = _make_simulation(
        spm_unit_fields={
            "spm_unit_spm_threshold": {"2024": baseline_threshold},
            "spm_unit_tenure_type": {"2024": "RENTER", "2025": "RENTER"},
        },
        people={
            "adult": {"age": {"2024": 35, "2025": 36}},
            "child": {"age": {"2024": 17, "2025": 18}},
        },
    )

    result = sim.calculate("spm_unit_spm_threshold", 2025)[0]
    expected = baseline_threshold
    expected *= _future_base_threshold("renter", 2025) / REFERENCE_THRESHOLDS_2024["renter"]
    expected *= _equivalence_scale(2, 0) / _equivalence_scale(1, 1)

    assert result == pytest.approx(expected)


def test_spm_threshold_recomputes_when_tenure_changes():
    baseline_threshold = 20_000.0
    sim = _make_simulation(
        spm_unit_fields={
            "spm_unit_spm_threshold": {"2024": baseline_threshold},
            "spm_unit_tenure_type": {
                "2024": "RENTER",
                "2025": "OWNER_WITHOUT_MORTGAGE",
            },
        },
        people={
            "adult": {"age": {"2024": 35, "2025": 36}},
        },
    )

    result = sim.calculate("spm_unit_spm_threshold", 2025)[0]
    expected = baseline_threshold
    expected *= (
        _future_base_threshold("owner_without_mortgage", 2025)
        / REFERENCE_THRESHOLDS_2024["renter"]
    )

    assert result == pytest.approx(expected)


def test_manual_future_spm_threshold_input_still_wins():
    sim = _make_simulation(
        spm_unit_fields={
            "spm_unit_spm_threshold": {"2024": 20_000.0, "2025": 12_345.0},
            "spm_unit_tenure_type": {"2024": "RENTER", "2025": "RENTER"},
        },
        people={
            "adult": {"age": {"2024": 35, "2025": 36}},
        },
    )

    assert sim.calculate("spm_unit_spm_threshold", 2025)[0] == pytest.approx(
        12_345.0
    )
