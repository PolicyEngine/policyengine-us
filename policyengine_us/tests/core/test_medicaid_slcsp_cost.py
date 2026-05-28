import numpy as np
import pytest

from policyengine_us import Simulation


def test_medicaid_slcsp_cost_index_allocates_ny_family_tier():
    simulation = Simulation(
        situation={
            "people": {
                "adult_1": {"age": {"2026": 40}},
                "adult_2": {"age": {"2026": 38}},
                "child_1": {
                    "age": {"2026": 10},
                    "is_tax_unit_dependent": {"2026": True},
                },
                "child_2": {
                    "age": {"2026": 8},
                    "is_tax_unit_dependent": {"2026": True},
                },
            },
            "tax_units": {
                "tax_unit": {"members": ["adult_1", "adult_2", "child_1", "child_2"]}
            },
            "spm_units": {
                "spm_unit": {"members": ["adult_1", "adult_2", "child_1", "child_2"]}
            },
            "families": {
                "family": {"members": ["adult_1", "adult_2", "child_1", "child_2"]}
            },
            "households": {
                "household": {
                    "members": ["adult_1", "adult_2", "child_1", "child_2"],
                    "state_code": {"2026": "NY"},
                }
            },
        }
    )

    base_cost = simulation.calculate("slcsp_age_0", "2026-01")[0]
    index = simulation.calculate("medicaid_slcsp_cost_index", 2026)

    np.testing.assert_allclose(index, np.full(4, base_cost * 2.85 / 4))


def test_medicaid_slcsp_cost_index_preserves_vt_child_only_fallback():
    simulation = Simulation(
        situation={
            "people": {
                "child_1": {
                    "age": {"2026": 12},
                    "is_tax_unit_dependent": {"2026": True},
                },
                "child_2": {
                    "age": {"2026": 10},
                    "is_tax_unit_dependent": {"2026": True},
                },
            },
            "tax_units": {"tax_unit": {"members": ["child_1", "child_2"]}},
            "spm_units": {"spm_unit": {"members": ["child_1", "child_2"]}},
            "families": {"family": {"members": ["child_1", "child_2"]}},
            "households": {
                "household": {
                    "members": ["child_1", "child_2"],
                    "state_code": {"2026": "VT"},
                }
            },
        }
    )

    base_cost = simulation.calculate("slcsp_age_0", "2026-01")[0]
    index = simulation.calculate("medicaid_slcsp_cost_index", 2026)

    np.testing.assert_allclose(index, np.full(2, base_cost))


def test_medicaid_slcsp_cost_index_fills_missing_values_with_state_average():
    simulation = Simulation(
        situation={
            "people": {
                "person_1": {"medicaid_slcsp_cost_index": {"2026": 0}},
                "person_2": {"medicaid_slcsp_cost_index": {"2026": 200}},
                "person_3": {"medicaid_slcsp_cost_index": {"2026": 400}},
            },
            "tax_units": {
                "tax_unit_1": {"members": ["person_1"]},
                "tax_unit_2": {"members": ["person_2"]},
                "tax_unit_3": {"members": ["person_3"]},
            },
            "spm_units": {
                "spm_unit_1": {"members": ["person_1"]},
                "spm_unit_2": {"members": ["person_2"]},
                "spm_unit_3": {"members": ["person_3"]},
            },
            "families": {
                "family_1": {"members": ["person_1"]},
                "family_2": {"members": ["person_2"]},
                "family_3": {"members": ["person_3"]},
            },
            "households": {
                "household_1": {
                    "members": ["person_1"],
                    "state_code": {"2026": "CA"},
                },
                "household_2": {
                    "members": ["person_2"],
                    "state_code": {"2026": "CA"},
                },
                "household_3": {
                    "members": ["person_3"],
                    "state_code": {"2026": "CA"},
                },
            },
        }
    )

    np.testing.assert_allclose(
        simulation.calculate("medicaid_slcsp_cost_index_filled", 2026),
        [300, 200, 400],
    )


def test_medicaid_cost_if_enrolled_is_not_pathway_dependent():
    simulation = Simulation(
        situation={
            "people": {
                "ssi_adult": {
                    "age": {"2026": 40},
                    "is_medicaid_eligible": {"2026": True},
                    "is_ssi_recipient_for_medicaid": {"2026": True},
                },
                "magi_adult": {
                    "age": {"2026": 40},
                    "is_medicaid_eligible": {"2026": True},
                },
            },
            "tax_units": {
                "ssi_unit": {"members": ["ssi_adult"]},
                "magi_unit": {"members": ["magi_adult"]},
            },
            "spm_units": {
                "ssi_spm": {"members": ["ssi_adult"]},
                "magi_spm": {"members": ["magi_adult"]},
            },
            "families": {
                "ssi_family": {"members": ["ssi_adult"]},
                "magi_family": {"members": ["magi_adult"]},
            },
            "households": {
                "ssi_household": {
                    "members": ["ssi_adult"],
                    "state_code": {"2026": "CA"},
                },
                "magi_household": {
                    "members": ["magi_adult"],
                    "state_code": {"2026": "CA"},
                },
            },
        }
    )

    costs = simulation.calculate("medicaid_cost_if_enrolled", 2026)

    assert costs[0] == pytest.approx(costs[1])
    assert costs[0] > 0


def test_household_medicaid_cost_uses_state_enrollment_denominator():
    simulation = Simulation(
        situation={
            "people": {
                "person_1": {"medicaid_slcsp_cost_index": {"2026": 100}},
                "person_2": {"medicaid_slcsp_cost_index": {"2026": 200}},
            },
            "tax_units": {
                "tax_unit_1": {"members": ["person_1"]},
                "tax_unit_2": {"members": ["person_2"]},
            },
            "spm_units": {
                "spm_unit_1": {"members": ["person_1"]},
                "spm_unit_2": {"members": ["person_2"]},
            },
            "families": {
                "family_1": {"members": ["person_1"]},
                "family_2": {"members": ["person_2"]},
            },
            "households": {
                "household_1": {
                    "members": ["person_1"],
                    "state_code": {"2026": "CA"},
                },
                "household_2": {
                    "members": ["person_2"],
                    "state_code": {"2026": "CA"},
                },
            },
        }
    )

    costs = simulation.calculate("medicaid_cost_if_enrolled", 2026)

    assert costs[1] == pytest.approx(costs[0] * 2)
    assert costs[0] > 0
    assert costs[1] < 50_000
