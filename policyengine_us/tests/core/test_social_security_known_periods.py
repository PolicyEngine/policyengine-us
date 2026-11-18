"""Keep reported source periods compatible with both Core holder APIs."""

import inspect

import numpy as np
import pytest
from policyengine_core.holders import Holder
from policyengine_core.periods import period

import test_social_security_real_core as real_core
from test_social_security_real_core import installed_hooks as installed_hooks


@pytest.fixture
def branch_aware_core():
    physical = real_core.hooks._PHYSICAL["get_known_periods"]
    if "branch_name" not in inspect.signature(physical).parameters:
        pytest.skip("Core master Holder.get_known_periods accepts no branch argument")


@pytest.mark.parametrize("public", real_core.COMPONENTS)
def test_known_periods_without_branch_keeps_reported_sources(public):
    reported = f"{public}_reported"
    simulation = real_core.fresh(
        {public: {"2024": [12_000]}, reported: {"2026": [6_000]}}
    )
    holder = simulation.get_holder(reported)
    assert {str(known) for known in holder.get_known_periods()} == {"2024", "2026"}
    assert {str(known) for known in holder.get_known_periods(None)} == {"2024", "2026"}


@pytest.mark.usefixtures("branch_aware_core")
@pytest.mark.parametrize("public", real_core.COMPONENTS)
def test_known_periods_lists_only_sources_readable_by_requested_branch(public):
    reported = f"{public}_reported"
    simulation = real_core.fresh()
    simulation.get_holder(public).set_input(
        period(2024), np.array([12_000]), branch_name="later"
    )
    holder = simulation.get_holder(reported)
    holder.set_input(period(2026), np.array([6_000]), branch_name="later")

    assert holder.get_array(period(2024), "later")[0] == 12_000
    assert holder.get_array(period(2024), "default") is None
    assert {str(known) for known in holder.get_known_periods("later")} == {
        "2024",
        "2026",
    }
    assert holder.get_known_periods("default") == []
    assert holder.get_known_periods("unrelated") == []


@pytest.mark.usefixtures("branch_aware_core")
def test_known_periods_forwards_branch_to_fallback_check(monkeypatch):
    simulation = real_core.fresh()
    holder = simulation.get_holder(f"{real_core.PUBLIC}_reported")
    original = real_core.hooks._allow_fallback
    branches = []

    def allow_fallback(simulation, name, period=None, branch_name=None):
        if period is None:
            branches.append(branch_name)
        return original(simulation, name, period, branch_name)

    monkeypatch.setattr(real_core.hooks, "_allow_fallback", allow_fallback)
    assert holder.get_known_periods("later") == []
    assert branches == ["later"]


@pytest.mark.parametrize("public", real_core.COMPONENTS)
def test_root_fallback_calculates_missing_reported_input(public):
    simulation = real_core.fresh()
    assert simulation.calculate(f"{public}_reported", 2024)[0] == 0


def test_root_fallback_calculates_missing_nonreported_input():
    simulation = real_core.fresh()
    simulation.delete_arrays("independent_input")
    assert simulation.calculate("independent_input", 2024)[0] == 0
