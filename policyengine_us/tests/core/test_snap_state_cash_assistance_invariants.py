"""Check how SNAP budgets state and local cash grants supplied as inputs."""

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2026
MONTH = f"{YEAR}-01"
ADULT = {
    "age": {YEAR: 45},
    "meets_snap_general_work_requirements": {MONTH: True},
    "meets_snap_work_requirements_person": {MONTH: True},
}


def _add_unit(situation, state, people, **unit_inputs):
    unit = f"unit_{len(situation['spm_units'])}"
    members = [f"{unit}_person_{i}" for i in range(len(people))]
    situation["people"].update(zip(members, people, strict=True))
    situation["spm_units"][unit] = {"members": members, **unit_inputs}
    situation["households"][unit] = {
        "members": members,
        "state_code": {YEAR: state},
    }


@settings(max_examples=6, deadline=None, derandomize=True)
@given(amount=st.integers(250, 450), increase=st.integers(10, 100))
def test_snap_counts_each_unit_grant_once_and_lowers_the_allotment(amount, increase):
    situation = {"people": {}, "spm_units": {}, "households": {}}
    expected = []
    for state, grant in (
        ("NY", "ny_safety_net_assistance"),
        ("CA", "ca_ala_general_assistance"),
    ):
        for size in range(1, 5):
            # Hold eligibility and deductions fixed within each pair.
            for payment in (amount, amount + increase):
                _add_unit(
                    situation,
                    state,
                    [ADULT] * size,
                    is_snap_eligible={MONTH: True},
                    snap_deductions={MONTH: 200},
                    **{grant: {MONTH: payment}},
                )
                expected.append(payment)

    sim = Simulation(situation=situation)
    np.testing.assert_allclose(sim.calculate("snap_unearned_income", MONTH), expected)
    allotments = np.asarray(sim.calculate("snap_normal_allotment", MONTH))
    assert (allotments[1::2] < allotments[::2]).all()


@settings(max_examples=6, deadline=None, derandomize=True)
@given(amount=st.integers(1, 1_300), size=st.integers(2, 5))
def test_snap_applies_member_income_share_to_person_grants(amount, size):
    situation = {"people": {}, "spm_units": {}, "households": {}}
    expected = []
    for state, grant, capi_eligible in (
        ("IL", "il_aabd_person", False),
        ("CA", "ca_capi_person", True),
        ("CA", "ca_capi_person", False),
    ):
        for prorated in (False, True):
            recipient = {
                **ADULT,
                grant: {MONTH: amount},
                "is_snap_prorated_income_member": {MONTH: prorated},
                "is_snap_excluded_member": {MONTH: prorated},
            }
            _add_unit(
                situation,
                state,
                [recipient, *([ADULT] * (size - 1))],
                ca_capi_eligible={YEAR: capi_eligible},
            )
            paid = amount if state == "IL" or capi_eligible else 0
            counted_share = (size - 1) / size if prorated else 1
            expected.append(paid * counted_share)

    sim = Simulation(situation=situation)
    np.testing.assert_allclose(
        sim.calculate("snap_unearned_income", MONTH), expected, atol=0.01
    )
