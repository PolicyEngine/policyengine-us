"""New reform controls must be inert under current law, including input history.

Python covers Core's input provenance, constructor migration, and generated
years/values. All cases reuse the default country system without a reform.
"""

from copy import deepcopy
from types import SimpleNamespace

import numpy as np
import pytest
from hypothesis import example, given, settings, strategies as st
from policyengine_core.periods import period as to_period

from policyengine_us import Simulation
from policyengine_us.data.economic_assumptions import _EXACT_YEAR_COLA_OVERRIDES
from policyengine_us.tests.unit.test_ss_cola_means_test import (
    COMPONENTS,
    _calculator_record,
    _record,
    _simulation,
    _situation,
)
from policyengine_us.tools.general import earliest_input_year


OVERRIDES = tuple(f"social_security_{c}_cola_override" for c in COMPONENTS) + (
    "ss_calculator_cola_override",
)


def test_cola_override_inventory_covers_inference_reset_and_invariance():
    system = Simulation.default_tax_benefit_system_instance
    registered = {name for name in system.variables if name.endswith("_cola_override")}
    coverage_message = (
        "New COLA override controls need inference, reset and invariance coverage: "
        "update earliest_input_year, _EXACT_YEAR_COLA_OVERRIDES and OVERRIDES."
    )
    assert registered == set(OVERRIDES), coverage_message
    assert registered == set(_EXACT_YEAR_COLA_OVERRIDES), coverage_message

    # Exercise the exclusions without building another country system or simulation.
    historical_period = to_period(2020)
    holder = SimpleNamespace(
        get_known_branch_periods=lambda: {("default", historical_period)}
    )
    probe = SimpleNamespace(
        tax_benefit_system=system,
        _get_visible_branch_names=lambda: ["default"],
        _user_input_keys=[(name, "default", historical_period) for name in registered],
        get_holder=lambda name: holder,
    )
    assert earliest_input_year(probe) is None, coverage_message

    # Component exclusions stay exact; calculator records use the prefix rule.
    variables = system.variables.copy()
    probe.tax_benefit_system = SimpleNamespace(variables=variables)
    for name, expected in (
        ("social_security_auxiliary_cola_override", 2020),
        ("ss_calculator_inventory_guard", None),
    ):
        variables[name] = system.variables[OVERRIDES[0]]
        probe._user_input_keys = [(name, "default", historical_period)]
        assert earliest_input_year(probe) == expected, name


@pytest.fixture(scope="module")
def irmaa_control():
    situation = _situation(
        {
            "worker": {
                "age": {2027: 70},
                "employment_income": {2027: 500_000},
                "is_tax_unit_head": {2027: True},
            }
        }
    )
    # The review's minimal record has no auxiliary tax-unit input history.
    situation["tax_units"]["worker"].pop("tax_unit_itemizes")
    simulation = _simulation(situation)
    assert earliest_input_year(simulation) == 2027
    values = {
        name: simulation.calculate(name, 2027).copy()
        for name in ("medicare_irmaa_magi_two_years_prior", "medicare_part_b_premium")
    }
    np.testing.assert_allclose(
        values["medicare_irmaa_magi_two_years_prior"], [463100.31], rtol=0, atol=0.01
    )
    np.testing.assert_allclose(
        values["medicare_part_b_premium"], [7790.40], rtol=0, atol=0.01
    )
    return situation, values


@pytest.mark.parametrize("name", OVERRIDES)
@pytest.mark.parametrize("value", [-1, 1])
def test_override_does_not_supply_irmaa_income_history(irmaa_control, name, value):
    situation, expected = irmaa_control
    situation = deepcopy(situation)
    situation["people"]["worker"][name] = {2020: value}
    simulation = _simulation(situation)
    assert earliest_input_year(simulation) == 2027
    for output, control in expected.items():
        np.testing.assert_array_equal(simulation.calculate(output, 2027), control)


def test_legacy_withholding_still_supplies_input_history(irmaa_control):
    situation, _ = irmaa_control
    situation = deepcopy(situation)
    for component in COMPONENTS:
        situation["people"]["worker"][f"social_security_{component}_cola_withheld"] = {
            2020: False
        }
    assert earliest_input_year(_simulation(situation)) == 2020


@pytest.fixture(scope="module")
def default_routes():
    reported = _record()
    public = {name.removesuffix("_reported"): value for name, value in reported.items()}
    records = {
        "public": public,
        "reported": reported,
        "calculator": _calculator_record("calculator"),
    }
    for record in records.values():
        record["employment_income"] = {2027: 500_000}
    situation = _situation(records)
    simulation = _simulation(situation)
    outputs = (
        tuple(f"social_security_{c}" for c in COMPONENTS)
        + tuple(f"social_security_{c}_cola_means_test_withheld" for c in COMPONENTS)
        + tuple(f"social_security_{c}_joint_cola_factor" for c in COMPONENTS)
        + (
            "social_security",
            "taxable_social_security",
            "adjusted_gross_income",
            "income_tax",
            "ssi",
            "household_net_income",
            "medicare_irmaa_magi_two_years_prior",
            "medicare_part_b_premium",
            "ss_calculated_annual_entitlement",
            "ss_calculated_annual_payment",
        )
    )
    expected = {
        (name, 2027): simulation.calculate(name, 2027).copy() for name in outputs
    }
    expected.update(
        {
            ("ss_calculated_payment", month): simulation.calculate(
                "ss_calculated_payment", month
            ).copy()
            for month in ("2027-01", "2028-01")
        }
    )
    return situation, expected, earliest_input_year(simulation)


@pytest.mark.parametrize("ingress", ["situation", "set_input"])
@settings(max_examples=6, deadline=None)
@example(name=OVERRIDES[0], year=2027, value=2)
@example(name=OVERRIDES[1], year=2027, value=-2)
@example(name=OVERRIDES[2], year=2027, value=0.5)
@example(name=OVERRIDES[3], year=2027, value=1)
@example(name=OVERRIDES[4], year=2027, value=2)
@given(
    name=st.sampled_from(OVERRIDES),
    year=st.integers(min_value=1900, max_value=2100),
    value=st.one_of(
        st.integers(-10_000, 10_000),
        st.floats(-10_000, 10_000, allow_nan=False, allow_infinity=False),
    ),
)
def test_default_policy_ignores_override_years_and_values(
    default_routes, ingress, name, year, value
):
    """Any stored decision is inert on public, reported and calculator routes.

    Vary one control at a time so another channel cannot mask its effect.
    Include invalid active-policy decisions: disabled policy must never read
    or validate them. Raw input variables themselves are controls, not outputs.
    """
    situation, expected, expected_earliest_year = default_routes
    situation = deepcopy(situation)
    if ingress == "situation":
        for record in situation["people"].values():
            record[name] = {year: value}
    simulation = _simulation(situation)
    if ingress == "set_input":
        simulation.set_input(name, year, np.full(len(situation["people"]), value))
    assert earliest_input_year(simulation) == expected_earliest_year
    for (output, period), control in expected.items():
        np.testing.assert_array_equal(simulation.calculate(output, period), control)
