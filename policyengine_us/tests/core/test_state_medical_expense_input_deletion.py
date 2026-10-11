"""State paid-cost bases after a supplied medical subtotal is deleted.

The intact inputs remain supplied. Deleted inputs must instead use the
recomputed subtotal and restore its federal premium exclusion. Core 3.32.27
fixes the retained input provenance that prevents this on older versions.
"""

from importlib.metadata import version

import numpy as np
from packaging.version import Version
import pytest

from policyengine_us import Simulation
from policyengine_us.system import system


PERIOD = 2025
SUBTOTAL_DELETION_CASES = [
    pytest.param(False, id="intact-input"),
    pytest.param(
        True,
        id="deleted-input",
        marks=pytest.mark.xfail(
            condition=Version(version("policyengine-core")) < Version("3.32.27"),
            strict=True,
            reason=(
                "policyengine-core<3.32.27 retains deleted input provenance and "
                "misclassifies a recomputed medical subtotal as supplied, "
                "suppressing the ND/NM premium add-back; fixed by "
                "policyengine-core#561."
            ),
        ),
    ),
]


def _simulation(state, other_expenses):
    simulation = Simulation(
        tax_benefit_system=system,
        situation={
            "people": {
                "head": {
                    "age": {PERIOD: 65},
                    "is_tax_unit_head": {PERIOD: True},
                    "employment_income": {PERIOD: 30_000},
                    "medicare_enrolled": {PERIOD: False},
                    "health_insurance_premiums": {PERIOD: 6_000},
                    "other_medical_expenses": {PERIOD: other_expenses},
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["head"],
                    "filing_status": {PERIOD: "SINGLE"},
                    "head_is_dependent_elsewhere": {PERIOD: False},
                    "self_employed_health_insurance_ald": {PERIOD: 1_000},
                }
            },
            "households": {
                "household": {
                    "members": ["head"],
                    "state_code": {PERIOD: state},
                }
            },
        },
    )
    simulation.set_input(
        "itemized_medical_expenses", PERIOD, np.array([6_000 + other_expenses])
    )
    return simulation


@pytest.mark.parametrize("delete_subtotal", SUBTOTAL_DELETION_CASES)
def test_nd_paid_cost_base_after_medical_subtotal_deletion(delete_subtotal):
    simulation = _simulation("ND", other_expenses=500)
    if delete_subtotal:
        simulation.delete_arrays("itemized_medical_expenses", PERIOD)

    # Calculate the state first: it recomputes the deleted subtotal as 5,500
    # before inspecting provenance. Restore its 1,000 exclusion to retain
    # 6,500 paid costs. Old core retains the marker and returns 24,500.
    assert simulation.calculate("nd_renters_refund_income", PERIOD).tolist() == [23_500]


@pytest.mark.parametrize("delete_subtotal", SUBTOTAL_DELETION_CASES)
def test_nm_senior_benefits_after_medical_subtotal_deletion(delete_subtotal):
    simulation = _simulation("NM", other_expenses=22_000)
    if delete_subtotal:
        simulation.delete_arrays("itemized_medical_expenses", PERIOD)

    # The recomputed federal subtotal is 27,000, but restoring its 1,000
    # exclusion meets NM's 28,000 paid-cost threshold. On old core both
    # benefits are zero. Calculate both before asserting to preserve evidence.
    benefits = tuple(
        simulation.calculate(variable, PERIOD).item()
        for variable in (
            "nm_medical_expense_credit",
            "nm_medical_expense_exemption",
        )
    )
    assert benefits == (2_800, 3_000)
