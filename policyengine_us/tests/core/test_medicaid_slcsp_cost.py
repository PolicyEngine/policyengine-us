import numpy as np
import pytest
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.variables.gov.hhs.medicaid.costs.state_aggregate_helpers import (
    sum_by_state,
)


class NoOpReform(Reform):
    def apply(self):
        pass


def test_sum_by_state_does_not_mix_states():
    # Cross-state contamination check: each person should receive only their
    # own state's total, never another state's.
    values = np.array([1.0, 2.0, 3.0, 4.0])
    state = np.array(["TX", "CO", "TX", "CO"])

    result = sum_by_state(values, state)

    # TX = 1 + 3 = 4; CO = 2 + 4 = 6.
    np.testing.assert_allclose(result, [4.0, 6.0, 4.0, 6.0])


def test_medicaid_slcsp_cost_index_allocates_vt_family_tier():
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
                    "state_code": {"2026": "VT"},
                }
            },
        }
    )

    base_cost = simulation.calculate("slcsp_age_0", "2026-01")[0]
    index = simulation.calculate("medicaid_slcsp_cost_index", 2026)

    # VT two-adults-with-children multiplier is 2.81, spread over 4 members.
    np.testing.assert_allclose(index, np.full(4, base_cost * 2.81 / 4))


def test_medicaid_slcsp_cost_index_allocates_ny_child_only():
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
                    "state_code": {"2026": "NY"},
                }
            },
        }
    )

    base_cost = simulation.calculate("slcsp_age_0", "2026-01")[0]
    index = simulation.calculate("medicaid_slcsp_cost_index", 2026)

    # NY child-only multiplier is 0.412, spread over the 2 children.
    np.testing.assert_allclose(index, np.full(2, base_cost * 0.412 / 2))


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


def test_reform_medicaid_denominator_uses_baseline_enrollment():
    simulation = Simulation(
        situation={
            "people": {
                "person_1": {
                    "is_medicaid_eligible": {"2026": True},
                    "medicaid_slcsp_cost_index": {"2026": 100},
                },
                "person_2": {
                    "is_medicaid_eligible": {"2026": True},
                    "medicaid_slcsp_cost_index": {"2026": 200},
                },
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
        },
        reform=NoOpReform,
    )
    simulation.is_over_dataset = True
    simulation.baseline.is_over_dataset = True

    simulation.set_input("medicaid_enrolled", 2026, [True, False])

    np.testing.assert_allclose(
        simulation.calculate("medicaid_slcsp_state_denominator", 2026),
        [300, 300],
    )


def test_medicaid_cost_allocation_recovers_state_spending():
    # The point of the allocation: over a dataset, the weighted sum of
    # per-enrollee costs in a state must recover that state's total spending.
    simulation = Simulation(
        situation={
            "people": {
                "person_1": {"medicaid_slcsp_cost_index": {"2026": 100}},
                "person_2": {"medicaid_slcsp_cost_index": {"2026": 200}},
                "person_3": {"medicaid_slcsp_cost_index": {"2026": 300}},
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
                    "state_code": {"2026": "TX"},
                },
                "household_2": {
                    "members": ["person_2"],
                    "state_code": {"2026": "TX"},
                },
                "household_3": {
                    "members": ["person_3"],
                    "state_code": {"2026": "TX"},
                },
            },
        }
    )
    simulation.is_over_dataset = True
    simulation.set_input("person_weight", 2026, [1_000, 2_000, 1_500])
    simulation.set_input("medicaid_enrolled", 2026, [True, True, True])

    weight = simulation.calculate("person_weight", 2026)
    enrolled = simulation.calculate("medicaid_enrolled", 2026)
    cost = simulation.calculate("medicaid_cost_if_enrolled", 2026)
    total_allocated = np.sum(weight * enrolled * cost)

    spending_tx = simulation.tax_benefit_system.parameters(
        "2026-01-01"
    ).calibration.gov.hhs.medicaid.totals.spending.TX

    assert total_allocated == pytest.approx(spending_tx, rel=1e-6)


def test_medicaid_cost_if_enrolled_is_zero_when_denominator_is_zero():
    # With no enrollees in the state the over-dataset denominator is 0; the
    # guard must return 0 rather than NaN/inf.
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
                    "state_code": {"2026": "TX"},
                },
                "household_2": {
                    "members": ["person_2"],
                    "state_code": {"2026": "TX"},
                },
            },
        }
    )
    simulation.is_over_dataset = True
    simulation.set_input("person_weight", 2026, [1_000, 2_000])
    simulation.set_input("medicaid_enrolled", 2026, [False, False])

    denominator = simulation.calculate("medicaid_slcsp_state_denominator", 2026)
    cost = simulation.calculate("medicaid_cost_if_enrolled", 2026)

    np.testing.assert_allclose(denominator, [0, 0])
    np.testing.assert_allclose(cost, [0, 0])
