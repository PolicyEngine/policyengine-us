"""Reported-benefit inference and public-formula factor composition.

The authored SSA parameter subtrees exercise the production adapter and public
formula without constructing a country system or cloning its parameter tree.
"""

from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from policyengine_core.parameters import ParameterNode
from policyengine_core.periods import period

import policyengine_us
from policyengine_us.tools.social_security.cola import (
    cola_factor,
    read_parameter_events,
)
from policyengine_us.tools.social_security.population import reported_pia_ratio_output
from policyengine_us.tools.social_security_benefit_levers import (
    SocialSecurityBenefitSource,
    reported_joint_cola_factor,
)
from policyengine_us.variables.gov.ssa.ss.social_security_retirement import (
    social_security_retirement,
)

PERIOD = period(2026)
E = 2025
OLD_PIA = Decimal("2156.8")
NEW_PIA = Decimal("2295.5")


@pytest.fixture
def parameters():
    parameter_root = Path(policyengine_us.__file__).resolve().parent / "parameters"
    root = ParameterNode(data={})
    for dotted in (
        "gov.contrib.ssa.pia",
        "gov.contrib.congress.s770.section_2",
        "gov.contrib.ssa.benefit_levers",
        "gov.ssa.cola_history",
        "gov.ssa.social_security.cola",
        "gov.ssa.social_security.pia",
    ):
        parent = root
        parts = dotted.split(".")
        for part in parts[:-1]:
            if part not in parent.children:
                full_name = ".".join(filter(None, (parent.name, part)))
                parent.add_child(part, ParameterNode(full_name, data={}))
            parent = getattr(parent, part)
        parent.add_child(
            parts[-1],
            ParameterNode(dotted, directory_path=str(parameter_root.joinpath(*parts))),
        )
    # Fix the C2 initial-eligibility bends without cloning the whole country.
    root.gov.ssa.social_security.pia.bend_points.first.update(
        start="2025-01-01", value=960
    )
    root.gov.ssa.social_security.pia.bend_points.second.update(
        start="2025-01-01", value=5785
    )
    pia = root.gov.contrib.ssa.pia
    pia.in_effect.update(start="2026-01-01", value=True)
    pia.recompute_existing.update(start="2026-01-01", value=True)
    pia.factors.first.update(start="2026-01-01", value=0.95)
    pia.bend_point_multipliers.first.update(start="2026-01-01", value=1.15)
    cola = root.gov.contrib.ssa.benefit_levers.cola
    cola.pp_change.update(start="2026-01-01", value=0.01)
    cola.start_year.update(start="2026-01-01", value=2026)
    return root


class ReportedRetiree:
    ids = ("retiree",)

    def __init__(self, annual_reported):
        self.reads = []
        values = {
            "age": 63,
            "birth_year": 1963,
            "social_security_retirement_reported": float(annual_reported),
            "social_security_retirement_base": float(annual_reported),
            "social_security_retirement_source": SocialSecurityBenefitSource.reported,
            "social_security_retirement_worker_eligibility_year": E,
            "social_security_retirement_worker_id": "",
            "social_security_worker_computation_year": 0,
            "social_security_retirement_entitlement_year": 2025,
            "social_security_retirement_entitlement_month": 1,
            "social_security_retirement_first_cola_year": 2026,
            "social_security_retirement_first_cola_month": 1,
            "social_security_retirement_claim_age_months": 744,
            "social_security_birth_month": 0,
            "social_security_birth_day": 0,
            "ss_calculator_birth_date": "",
            "social_security_survivors_reported": 0,
            "social_security_dependents_reported": 0,
            "social_security_disability_reported": 0,
            # Deliberately implausible final outputs make an accidental read
            # of an already-reformed benefit/factor easy to detect.
            "social_security_retirement": 1_000_000,
            "social_security_retirement_joint_cola_factor": 7.0,
            "social_security_retirement_pia_ratio_factor": 9.0,
            "social_security_across_the_board_factor": 1.08,
            "social_security_retirement_payable_factor": 0.80,
        }
        self.inputs = {name: np.asarray([value]) for name, value in values.items()}
        self.simulation = SimpleNamespace(
            tax_benefit_system=SimpleNamespace(
                variables={"birth_year": SimpleNamespace(definition_period="year")}
            ),
            _get_visible_branch_names=lambda: ("default",),
            _user_input_keys={("birth_year", "default", PERIOD)},
        )

    def __call__(self, name, requested_period):
        assert requested_period == PERIOD
        self.reads.append(name)
        return self.inputs[name]

    def set(self, name, value):
        self.inputs[name] = np.asarray([value])


def test_adapter_uses_baseline_cola_and_public_formula_applies_each_factor_once(
    parameters,
):
    events = read_parameter_events(parameters, 2026)
    baseline_cola = cola_factor(E, "2026-12", events)
    assert baseline_cola == Decimal("1.028")
    # A claim at 62 with FRA 67 gives .70. The 2025 benchmark has exactly
    # the December 2025 / January 2026 statutory COLA in its 2026 level.
    annual = Decimal(12) * Decimal(".70") * OLD_PIA * baseline_cola
    assert annual == Decimal("18624.39936")
    person = ReportedRetiree(annual)
    inferred = reported_pia_ratio_output(
        person, PERIOD, parameters, "retirement", "aime"
    )
    ratio = reported_pia_ratio_output(
        person, PERIOD, parameters, "retirement", "factor"
    )
    assert inferred[0] == pytest.approx(5000, abs=0.001)
    assert ratio[0] == pytest.approx(float(NEW_PIA / OLD_PIA), abs=1e-7)
    assert "social_security_retirement" not in person.reads
    assert "social_security_retirement_joint_cola_factor" not in person.reads
    assert "social_security_retirement_pia_ratio_factor" not in person.reads

    joint = reported_joint_cola_factor(person, PERIOD, parameters, "retirement")
    assert joint[0] == pytest.approx(1.038 / 1.028)
    assert joint[0] != 1
    person.set("social_security_retirement_joint_cola_factor", joint[0])
    person.set("social_security_retirement_pia_ratio_factor", ratio[0])
    actual = social_security_retirement.formula(person, PERIOD, parameters)
    expected = float(annual) * joint[0] * ratio[0] * 1.08 * 0.80
    assert actual[0] == pytest.approx(expected, rel=1e-12)

    # Change both the configured joint-COLA reform and cached reformed values.
    # Neither can enter baseline PIA recovery; the gross amount changes only
    # when the public formula applies the new joint-COLA factor.
    parameters.gov.contrib.ssa.benefit_levers.cola.pp_change.update(
        start="2026-01-01", value=0.02
    )
    person.set("social_security_retirement", actual[0])
    person.set("social_security_retirement_joint_cola_factor", 123.0)
    person.set("social_security_retirement_pia_ratio_factor", 456.0)
    np.testing.assert_array_equal(
        reported_pia_ratio_output(person, PERIOD, parameters, "retirement", "aime"),
        inferred,
    )
    np.testing.assert_array_equal(
        reported_pia_ratio_output(person, PERIOD, parameters, "retirement", "factor"),
        ratio,
    )
    next_joint = reported_joint_cola_factor(person, PERIOD, parameters, "retirement")
    assert next_joint[0] == pytest.approx(1.048 / 1.028)
    person.set("social_security_retirement_joint_cola_factor", next_joint[0])
    person.set("social_security_retirement_pia_ratio_factor", ratio[0])
    next_actual = social_security_retirement.formula(person, PERIOD, parameters)
    assert next_actual[0] == pytest.approx(
        float(annual) * next_joint[0] * ratio[0] * 1.08 * 0.80, rel=1e-12
    )
    assert next_actual[0] / actual[0] == pytest.approx(1.048 / 1.038)
