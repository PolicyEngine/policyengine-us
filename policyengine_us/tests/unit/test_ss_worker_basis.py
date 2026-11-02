"""Worker-link resolution without simulation or country-model fixtures."""

import numpy as np
import pytest

from policyengine_us.tools.social_security.records import resolve_worker_basis


class Records:
    ids = ("recipient", "worker")

    def __init__(self, component, **inputs):
        self.inputs = {
            f"social_security_{component}_worker_eligibility_year": np.array([0, 0]),
            f"social_security_{component}_worker_id": np.array(["", ""], dtype=object),
            "social_security_worker_computation_year": np.array([0, 0]),
            "social_security_retirement_worker_eligibility_year": np.array([0, 0]),
        }
        self.inputs.update({key: np.asarray(value) for key, value in inputs.items()})

    def __call__(self, variable, period):
        return self.inputs[variable]


@pytest.mark.parametrize("component", ["retirement", "disability"])
def test_unlinked_own_record_uses_shared_year_without_mutating_inputs(component):
    key = f"social_security_{component}_worker_eligibility_year"
    records = Records(component, social_security_worker_computation_year=[2020, 2021])
    years, linked, indices = resolve_worker_basis(
        records, 2026, component, [True, True]
    )
    np.testing.assert_array_equal(years, [2020, 2021])
    np.testing.assert_array_equal(linked, [False, False])
    np.testing.assert_array_equal(indices, [0, 1])
    np.testing.assert_array_equal(records.inputs[key], [0, 0])


def test_supplied_component_year_precedes_own_shared_year():
    records = Records(
        "retirement",
        social_security_retirement_worker_eligibility_year=[2018, 0],
        social_security_worker_computation_year=[2020, 2021],
    )
    years, _, _ = resolve_worker_basis(records, 2026, "retirement", [True, True])
    np.testing.assert_array_equal(years, [2018, 2021])


def test_link_reads_workers_same_component_year_before_shared_year():
    records = Records(
        "survivors",
        social_security_survivors_worker_id=["worker", ""],
        social_security_survivors_worker_eligibility_year=[0, 2018],
        social_security_worker_computation_year=[0, 2020],
    )
    years, linked, indices = resolve_worker_basis(
        records, 2026, "survivors", [True, False]
    )
    assert years[0] == 2018
    np.testing.assert_array_equal(linked, [True, False])
    np.testing.assert_array_equal(indices, [1, 1])


@pytest.mark.parametrize("component", ["survivors", "dependents"])
def test_auxiliary_link_can_use_workers_retirement_year(component):
    records = Records(
        component,
        **{
            f"social_security_{component}_worker_id": ["worker", ""],
            "social_security_retirement_worker_eligibility_year": [0, 2019],
        },
    )
    years, linked, _ = resolve_worker_basis(records, 2026, component, [True, False])
    assert years[0] == 2019
    assert linked[0]


def test_auxiliary_without_worker_link_does_not_borrow_own_shared_year():
    records = Records("survivors", social_security_worker_computation_year=[2020, 2021])
    years, linked, _ = resolve_worker_basis(records, 2026, "survivors", [True, True])
    np.testing.assert_array_equal(years, [0, 0])
    assert not np.any(linked)


def test_link_without_worker_year_stays_missing_for_callers_to_handle():
    records = Records("retirement", social_security_retirement_worker_id=["worker", ""])
    years, linked, _ = resolve_worker_basis(records, 2026, "retirement", [True, False])
    assert years[0] == 0
    assert linked[0]


def test_links_read_supplied_worker_basis_without_order_dependent_link_chasing():
    records = Records(
        "survivors",
        social_security_survivors_worker_id=["worker", "recipient", ""],
        social_security_survivors_worker_eligibility_year=[0, 0, 2019],
        social_security_worker_computation_year=[0, 0, 0],
        social_security_retirement_worker_eligibility_year=[0, 0, 0],
    )
    records.ids = ("recipient", "linked", "worker")
    years, linked, _ = resolve_worker_basis(
        records, 2026, "survivors", [True, True, False]
    )
    np.testing.assert_array_equal(years, [2019, 0, 2019])
    np.testing.assert_array_equal(linked, [True, True, False])


def test_recipient_supplied_year_can_identify_linked_worker_basis():
    records = Records(
        "survivors",
        social_security_survivors_worker_id=["worker", ""],
        social_security_survivors_worker_eligibility_year=[2018, 0],
    )
    years, linked, _ = resolve_worker_basis(records, 2026, "survivors", [True, False])
    assert years[0] == 2018
    assert linked[0]


def test_conflicting_supplied_and_linked_years_rejected():
    records = Records(
        "survivors",
        social_security_survivors_worker_id=["worker", ""],
        social_security_survivors_worker_eligibility_year=[2018, 2019],
    )
    with pytest.raises(ValueError, match="Conflicting"):
        resolve_worker_basis(records, 2026, "survivors", [True, False])


def test_unknown_worker_id_rejected_only_for_active_records():
    records = Records(
        "retirement", social_security_retirement_worker_id=["missing", ""]
    )
    with pytest.raises(ValueError, match="does not identify a person"):
        resolve_worker_basis(records, 2026, "retirement", [True, False])
    years, linked, _ = resolve_worker_basis(records, 2026, "retirement", [False, True])
    assert years[0] == 0
    assert not np.any(linked)
