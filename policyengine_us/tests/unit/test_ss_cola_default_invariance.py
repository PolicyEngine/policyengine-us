"""New reform controls must be inert under current law, including input history.

Python covers Core's input provenance, constructor migration, and generated
years/values. All cases reuse the default country system without a reform.
"""

from copy import deepcopy

import numpy as np
import pytest
from hypothesis import example, given, settings, strategies as st

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


@pytest.fixture(scope="module")
def irmaa_control():
    situation = _situation(
        {
            "worker": {
                "age": {2027: 70},
                "employment_income": {2027: 500_000},
                "is_tax_unit_head": True,
            }
        }
    )
    # The review's minimal record has no auxiliary tax-unit input history.
    situation["tax_units"]["worker"].pop("tax_unit_itemizes")
    simulation = _simulation(situation)
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
