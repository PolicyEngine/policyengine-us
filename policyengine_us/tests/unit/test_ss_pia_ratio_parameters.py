"""Load only C's authored parameter subtree, without a US model or simulation."""

from pathlib import Path

import pytest
from policyengine_core.parameters import ParameterNode


PARAMETER_PATH = (
    Path(__file__).resolve().parents[2]
    / "parameters/gov/contrib/ssa/benefit_levers/pia_ratio"
)
PARAMETER_NAME = "gov.contrib.ssa.benefit_levers.pia_ratio"


@pytest.fixture
def parameters():
    # The native Core loader must read the authored files. A hand-built dict or
    # mocked snapshot would miss unsupported scalar-string parameter syntax.
    return ParameterNode(
        name=PARAMETER_NAME,
        directory_path=str(PARAMETER_PATH),
    )


@pytest.mark.parametrize("instant", ["1983-01-01", "2026-01-01", "2035-01-01"])
def test_authored_defaults_load_as_native_named_selector_lists(parameters, instant):
    snapshot = parameters(instant)
    assert snapshot.claiming_scenario == ["supplied_claim_age"]
    assert snapshot.disability_eligibility_proxy == ["pre_reform"]
    assert snapshot.annual_rounding_bound == 0


def test_authored_selector_paths_and_metadata_survive_loading(parameters):
    assert parameters.claiming_scenario.name == PARAMETER_NAME + ".claiming_scenario"
    assert (
        parameters.disability_eligibility_proxy.name
        == PARAMETER_NAME + ".disability_eligibility_proxy"
    )
    assert parameters.claiming_scenario.metadata["unit"] == "str"
    assert parameters.disability_eligibility_proxy.metadata["unit"] == "str"


def test_named_selector_reform_and_snapshots_keep_dated_values(parameters):
    parameters.claiming_scenario.update(start="2026-01-01", value=["entitlement_dates"])
    parameters.disability_eligibility_proxy.update(
        start="2026-01-01", value=["current_year"]
    )
    parameters.annual_rounding_bound.update(start="2026-01-01", value=0.5)
    earlier = parameters("2025-01-01")
    current = parameters("2026-01-01")
    assert earlier.claiming_scenario == ["supplied_claim_age"]
    assert earlier.disability_eligibility_proxy == ["pre_reform"]
    assert earlier.annual_rounding_bound == 0
    assert current.claiming_scenario == ["entitlement_dates"]
    assert current.disability_eligibility_proxy == ["current_year"]
    assert current.annual_rounding_bound == 0.5
