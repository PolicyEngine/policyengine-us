"""Disability proxy gates using native parameters without constructing a US model."""

from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from policyengine_core.parameters import ParameterNode
from policyengine_core.periods import period

from policyengine_us.tools.social_security.population import (
    _disability_proxy_year,
    _record_basis,
)
from policyengine_us.tools.social_security_benefit_levers import (
    SocialSecurityBenefitSource,
)


PARAMETER_ROOT = Path(__file__).resolve().parents[2] / "parameters"
PERIOD = period(2026)


@pytest.fixture
def parameters():
    # Load the authored defaults into real Core nodes. Only the three small
    # subtrees used by the adapter are needed; no country model is built.
    root = ParameterNode(data={})
    for path in (
        "gov.contrib.ssa.pia",
        "gov.contrib.congress.s770.section_2",
        "gov.contrib.ssa.benefit_levers.pia_ratio",
    ):
        parent = root
        parts = path.split(".")
        for name in parts[:-1]:
            if name not in parent.children:
                full_name = ".".join(filter(None, (parent.name, name)))
                parent.add_child(name, ParameterNode(full_name, data={}))
            parent = getattr(parent, name)
        parent.add_child(
            parts[-1],
            ParameterNode(
                path,
                directory_path=str(PARAMETER_ROOT.joinpath(*parts)),
            ),
        )
    return root


class DisabilityInputs:
    ids = ("recipient",)

    def __init__(self, **inputs):
        values = {
            "age": 45,
            "birth_year": 1981,
            "social_security_disability_reported": 12000,
            "social_security_disability_source": SocialSecurityBenefitSource.reported,
            "social_security_disability_worker_eligibility_year": 0,
            "social_security_disability_worker_id": "",
            "social_security_worker_computation_year": 0,
            "social_security_disability_entitlement_year": 0,
            **inputs,
        }
        self.inputs = {name: np.asarray([value]) for name, value in values.items()}
        self.simulation = SimpleNamespace(
            tax_benefit_system=SimpleNamespace(
                variables={"birth_year": SimpleNamespace(definition_period="year")}
            ),
            _get_visible_branch_names=lambda: ("default",),
            _user_input_keys=set(),
        )

    def __call__(self, name, requested_period):
        assert requested_period == PERIOD
        return self.inputs[name]


@pytest.mark.parametrize("recompute_existing", [False, True])
def test_missing_onset_proxy_precedes_factor_start_not_enablement_timestamp(
    parameters, recompute_existing
):
    pia = parameters.gov.contrib.ssa.pia
    # Inline YAML reform values begin in 2000; the formula starts in 2026.
    pia.in_effect.update(start="2000-01-01", value=True)
    pia.recompute_existing.update(start="2000-01-01", value=recompute_existing)
    pia.factors.first.update(start="2000-01-01", value=0.95)
    pia.factors.start_year.update(start="2000-01-01", value=2026)

    result = _record_basis(DisabilityInputs(), PERIOD, parameters, "disability")

    assert result["eligibility_year"][0] == 2025
    assert result["claiming_adjustment"][0] == Fraction(1)
    assert result["proxy"][0]
    assert not result["unmodeled"][0]


def test_enabled_identity_path_does_not_supply_a_reform_start(parameters):
    parameters.gov.contrib.ssa.pia.in_effect.update(start="2000-01-01", value=True)

    assert _disability_proxy_year(parameters, 2026, "pre_reform") == 2025
    assert _disability_proxy_year(parameters, 2035, "pre_reform") == 2034


def test_bend_point_change_uses_its_effective_cohort(parameters):
    pia = parameters.gov.contrib.ssa.pia
    pia.in_effect.update(start="2000-01-01", value=True)
    pia.bend_point_multipliers.first.update(start="2000-01-01", value=1.15)
    pia.effective_year.update(start="2000-01-01", value=2024)

    assert _disability_proxy_year(parameters, 2026, "pre_reform") == 2023


def test_disabled_interval_postpones_the_first_operative_change(parameters):
    pia = parameters.gov.contrib.ssa.pia
    pia.in_effect.update(start="2000-01-01", value=True)
    pia.in_effect.update(start="2024-01-01", value=False)
    pia.in_effect.update(start="2026-01-01", value=True)
    pia.factors.first.update(start="2000-01-01", value=0.95)
    pia.factors.start_year.update(start="2000-01-01", value=2024)

    assert _disability_proxy_year(parameters, 2026, "pre_reform") == 2025


def test_s770_start_is_2026_even_when_the_switch_was_enabled_earlier(parameters):
    parameters.gov.contrib.congress.s770.section_2.in_effect.update(
        start="2000-01-01", value=True
    )

    assert _disability_proxy_year(parameters, 2025, "pre_reform") == 2024
    assert _disability_proxy_year(parameters, 2030, "pre_reform") == 2025


def test_future_formula_change_does_not_backdate_the_proxy(parameters):
    pia = parameters.gov.contrib.ssa.pia
    pia.in_effect.update(start="2000-01-01", value=True)
    pia.factors.first.update(start="2000-01-01", value=0.95)
    pia.factors.start_year.update(start="2000-01-01", value=2032)

    assert _disability_proxy_year(parameters, 2026, "pre_reform") == 2025


def test_indexing_identity_anchor_is_still_the_start_of_its_path(parameters):
    pia = parameters.gov.contrib.ssa.pia
    pia.in_effect.update(start="2000-01-01", value=True)
    pia.full_price_indexing.in_effect.update(start="2000-01-01", value=True)
    pia.full_price_indexing.start_year.update(start="2000-01-01", value=2024)
    pia.full_price_indexing.real_wage_scale.update(start="2024-01-01", value=1)

    assert _disability_proxy_year(parameters, 2026, "pre_reform") == 2023


def test_current_year_sensitivity_bypasses_formula_path_reads():
    assert _disability_proxy_year(None, 2026, "current_year") == 2026


def test_unknown_disability_proxy_is_rejected():
    with pytest.raises(ValueError, match="Choose pre_reform or current_year"):
        _disability_proxy_year(None, 2026, "unknown")


def test_supplied_worker_year_precedes_entitlement_and_current_year_proxy(parameters):
    policy = parameters.gov.contrib.ssa.benefit_levers.pia_ratio
    policy.disability_eligibility_proxy.update(
        start="1983-01-01", value=["current_year"]
    )
    person = DisabilityInputs(
        social_security_disability_worker_eligibility_year=2018,
        social_security_disability_entitlement_year=2020,
    )

    result = _record_basis(person, PERIOD, parameters, "disability")

    assert result["eligibility_year"][0] == 2018
    assert result["claiming_adjustment"][0] == Fraction(1)
    assert not result["proxy"][0]


def test_supplied_entitlement_year_precedes_missing_onset_proxy(parameters):
    person = DisabilityInputs(social_security_disability_entitlement_year=2020)

    result = _record_basis(person, PERIOD, parameters, "disability")

    assert result["eligibility_year"][0] == 2020
    assert result["claiming_adjustment"][0] == Fraction(1)
    assert not result["proxy"][0]
